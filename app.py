import os
import random
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import OpenAI

# 1. Configuration & Setup
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "est-sale-2026-secret")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'est_social.db')
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

client_ai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


# 2. Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(100), default="default_avatar.png")
    bio = db.Column(db.String(200), default="Étudiant à l'EST Salé")
    is_admin = db.Column(db.Boolean, default=False)
    game_level = db.Column(db.Integer, default=1)
    exp_points = db.Column(db.Integer, default=0)
    native_lang = db.Column(db.String(20), default="Arabe")
    target_lang = db.Column(db.String(20), default="Anglais")


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    media_file = db.Column(db.String(100))
    is_hidden = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    likes = db.relationship('Like', backref='post', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    is_audio = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user = db.relationship('User', backref='comments_list')


class SiteConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default="EST SOCIAL")


class LearnedWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    word = db.Column(db.String(100))
    translation = db.Column(db.String(100))
    date_learned = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# 3. Helper Functions
def get_rank(level):
    if level < 3: return "Nouveau 🐣"
    if level < 7: return "Warrior ⚔️"
    if level < 12: return "Master 🎓"
    return "Legend 👑"


# 4. Core Routes
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    curr_user = db.session.get(User, session['user_id'])
    if curr_user is None:
        session.clear()
        return redirect(url_for('login_page'))

    if curr_user.is_admin:
        posts = Post.query.order_by(Post.id.desc()).all()
    else:
        posts = Post.query.filter_by(is_hidden=False).order_by(Post.id.desc()).all()

    config = SiteConfig.query.first()
    return render_template('index.html', curr_user=curr_user, posts=posts, config=config)


@app.route('/login')
def login_page():
    config = SiteConfig.query.first()
    return render_template('welcome.html', config=config)


@app.route('/auth', methods=['POST'])
def auth():
    u_in = request.form.get('username').strip()
    p_in = request.form.get('password')
    if u_in == "admin" and p_in == "admin123":
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", password=generate_password_hash("admin123"), is_admin=True)
            db.session.add(admin)
            db.session.commit()
        session['user_id'] = admin.id
        session['role'] = "admin"
        return redirect(url_for('index'))

    user = User.query.filter_by(username=u_in).first()
    if not user:
        user = User(username=u_in, password=generate_password_hash(p_in))
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['role'] = "student"
        return redirect(url_for('index'))

    if check_password_hash(user.password, p_in):
        session['user_id'] = user.id
        session['role'] = "admin" if user.is_admin else "student"
        return redirect(url_for('index'))
    return "Erreur", 401


# 5. Interactions
@app.route('/like/<int:post_id>', methods=['POST'])
def toggle_like(post_id):
    if 'user_id' not in session: return jsonify({"error": "Auth"}), 401
    uid = session['user_id']
    existing = Like.query.filter_by(user_id=uid, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
        status = "unliked"
    else:
        db.session.add(Like(user_id=uid, post_id=post_id))
        status = "liked"
    db.session.commit()
    return jsonify({"status": status, "total": Like.query.filter_by(post_id=post_id).count()})


@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if 'user_id' not in session: return redirect(url_for('login_page'))
    content = request.form.get('content')
    if content:
        db.session.add(Comment(content=content, user_id=session['user_id'], post_id=post_id))
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/comment_audio/<int:post_id>', methods=['POST'])
def comment_audio(post_id):
    if 'user_id' not in session: return jsonify({"error": "Auth"}), 401
    if 'audio' in request.files:
        file = request.files['audio']
        filename = f"audio_{int(datetime.now().timestamp())}.webm"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_com = Comment(content=filename, is_audio=True, user_id=session['user_id'], post_id=post_id)
        db.session.add(new_com)
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"error": "No audio file"}), 400


# 6. Admin Actions
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if session.get('role') == 'admin':
        post = db.session.get(Post, post_id)
        if post:
            db.session.delete(post)
            db.session.commit()
    return redirect(url_for('index'))


@app.route('/toggle_visibility/<int:post_id>', methods=['POST'])
def toggle_visibility(post_id):
    if session.get('role') == 'admin':
        post = db.session.get(Post, post_id)
        if post:
            post.is_hidden = not post.is_hidden
            db.session.commit()
    return redirect(url_for('index'))


@app.route('/upload', methods=['POST'])
def upload():
    if session.get('role') == 'admin':
        file = request.files.get('media')
        title, content = request.form.get('title'), request.form.get('content')
        filename = ""
        if file:
            filename = f"{int(datetime.now().timestamp())}_{file.filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if filename.lower().endswith(('.mp4', '.mov', '.avi')): title = f"TYPE_VIDEO:{title}"
        db.session.add(Post(title=title, content=content, media_file=filename, author_id=session['user_id']))
        db.session.commit()
    return redirect(url_for('index'))


# 7. Profile Management
@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect(url_for('login_page'))
    curr_user = db.session.get(User, session['user_id'])
    return render_template('profile.html', curr_user=curr_user, config=SiteConfig.query.first())


@app.route('/update_profile', methods=['POST'])
def update_profile():
    user = db.session.get(User, session['user_id'])
    user.username, user.bio = request.form.get('username'), request.form.get('bio')
    user.native_lang, user.target_lang = request.form.get('native_lang'), request.form.get('target_lang')
    file = request.files.get('avatar')
    if file:
        fname = f"avatar_{user.id}_{int(datetime.now().timestamp())}.png"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        user.profile_pic = fname
    db.session.commit()
    return redirect(url_for('profile'))


# 8. Game & AI (Smart Learning System)
@app.route('/game')
def game():
    if 'user_id' not in session: return redirect(url_for('login_page'))
    return render_template('game.html', curr_user=db.session.get(User, session['user_id']))

@app.route('/game/spawn_monster', methods=['POST'])
def spawn_monster():
    if 'user_id' not in session: return jsonify({"error": "Auth"}), 401
    user = db.session.get(User, session['user_id'])

    # 1. Check wach BOSS TIME (kol 10 d l-kalimate)
    word_count = LearnedWord.query.filter_by(user_id=user.id).count()
    is_boss = (word_count > 0 and word_count % 10 == 0)

    # 2. Hezz history dial user (Words + Translations)
    history_data = LearnedWord.query.filter_by(user_id=user.id).order_by(LearnedWord.id.desc()).limit(20).all()
    history_list = [{"word": h.word, "trans": h.translation} for h in history_data]

    # 3. Gad l-Prompt dqi9
    prompt = f"""
    Rôle: Maître de la Terre de Zikola.
    Objectif: Enseigner le {user.target_lang} à un élève de niveau {user.game_level}.

    HISTORIQUE DES MOTS DÉJÀ APPRIS (INTERDIT DE RÉPÉTER):
    {json.dumps(history_list)}

    MISSION:
    - Si 'is_boss' est FALSE: Génère un NOUVEAU mot stimulant (pas trop simple comme 'house' ou 'cat').
    - Si 'is_boss' est TRUE: Sélectionne le mot le plus difficile de l'historique pour un test oral final.

    RÈGLES:
    - Ne jamais donner un mot présent dans l'historique sauf si c'est un Boss.
    - Donne un nom de monstre fantastique (ex: Aris, Shamher, Zoldik).
    - Réponds UNIQUEMENT en JSON.
    """

    try:
        res = client_ai.chat.completions.create(
            model="google/gemini-2.0-flash-001",
            messages=[{"role": "system", "content": "Tu es un moteur de jeu RPG éducatif."},
                      {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.9  # Bach i-koun creative o may-3awedch
        )

        data = json.loads(res.choices[0].message.content)
        data['is_boss'] = is_boss  # Force l-flag

        return jsonify(data)
    except Exception as e:
        print(f"Erreur AI: {e}")
        # Fallback kelma s3iba ila t-9te3 l-AI
        return jsonify({"word": "Perseverance", "translation": "المثابرة", "name": "Guardian", "is_boss": is_boss})

@app.route('/game/win', methods=['POST'])
def game_win():
    if 'user_id' not in session: return jsonify({"error": "Auth"}), 401
    user = db.session.get(User, session['user_id'])
    data = request.json

    # Save to history
    word = data.get('word')
    trans = data.get('translation')
    if word:
        new_learned = LearnedWord(user_id=user.id, word=word, translation=trans)
        db.session.add(new_learned)

    # Update XP & Level
    user.exp_points += 10
    if user.exp_points >= (user.game_level * 100):
        user.game_level += 1
        user.exp_points = 0

    db.session.commit()
    return jsonify({
        "new_xp": user.exp_points,
        "new_level": user.game_level,
        "rank": get_rank(user.game_level)
    })


@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    msg = request.json.get('message')
    try:
        res = client_ai.chat.completions.create(model="google/gemini-2.0-flash-001",
                                                messages=[{"role": "user", "content": msg}])
        return jsonify({"reply": res.choices[0].message.content})
    except:
        return jsonify({"reply": "Désolé..."}), 500


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


# 9. Start
if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(os.path.join(basedir, 'instance')): os.makedirs(os.path.join(basedir, 'instance'))
        db.create_all()
    app.run(debug=True)
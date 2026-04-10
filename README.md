
---

## **GitHub Repository Description :**

### **EST Social - Gamified Social Learning Platform**

**EST Social** is an interactive web application built with **Flask** that combines social networking with gamified language learning. It's designed for students to practice English through real-life roleplay scenarios, earn XP, level up, and interact with AI-powered NPCs.

---

### **✨ Key Features:**

#### **👥 Social Feed**
- Post images & videos (admin only)
- Like & comment on posts
- Voice comments (audio recording)
- Dark/Light mode toggle
- AI Assistant (Gemini via OpenRouter)

#### **🎮 Gamified Learning**
- Roleplay chat in real locations (Airport, Cafe, Hotel, Restaurant)
- Mission-based learning (order coffee, ask for directions, etc.)
- XP points & Level system (1-12+)
- Rank system: Nouveau → Warrior → Master → Legend
- Timer-based challenges
- Hint system (max 3 hints per mission)

#### **👑 Group System** (Level 3+)
- Create & manage your own groups
- Invite members
- Group posts (images, videos, text)
- Member roles (owner, admin, member)
- Group becomes a public fan page

#### **🔧 Admin Panel**
- Manage posts (hide/delete)
- Update site name
- View all groups & users

---

### **🛠️ Tech Stack:**

| Layer | Technology |
|-------|------------|
| Backend | Flask (Python) |
| Database | SQLite + SQLAlchemy |
| Frontend | TailwindCSS, JavaScript |
| AI API | OpenRouter (Gemini 2.0 Flash) |
| Auth | Session-based, Werkzeug security |

---

### **📁 Project Structure:**

```
est_sale_web/
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── index.html         # Social feed
│   ├── game.html          # Location selector
│   ├── location_chat.html # Roleplay chat with timer/XP
│   ├── profile.html       # User profile & admin console
│   ├── welcome.html       # Login page
│   ├── admin_dash.html    # Admin dashboard
│   ├── groups_list.html   # Browse groups
│   ├── create_group.html  # Create new group
│   ├── group_page.html    # Group feed
│   └── my_groups.html     # User's groups
├── static/uploads/        # User avatars, post media, audio
├── instance/              # SQLite database
├── .env                   # Environment variables (API keys)
└── requirements.txt       # Python dependencies
```

---

### **🚀 Installation:**

```bash
# Clone the repository
git clone https://github.com/yourusername/est-social.git
cd est-social

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "OPENROUTER_API_KEY=your_api_key_here" > .env
echo "SECRET_KEY=your_secret_key_here" >> .env

# Run the application
python app.py
```

Access the app at `http://127.0.0.1:5000`

**Default Admin Login:** `admin` / `admin123`

---

### **🎯 Game Mechanics:**

| Level | Rank | Ability |
|-------|------|---------|
| 1-2 | Nouveau 🐣 | View & join groups |
| 3-6 | Warrior ⚔️ | **Create groups** |
| 7-11 | Master 🎓 | Admin privileges in groups |
| 12+ | Legend 👑 | Full moderation |

**How to level up:**
- Complete location missions → +50 XP
- Win word battles in game mode → +10 XP
- Every 100 XP = +1 level

---

### **🧪 Demo Mode (No API Key Required):**

If you don't have an OpenRouter API key, the app includes a **fallback mode** with rule-based AI responses. Simply comment out the AI section or the app will automatically use local responses.

---

### **📄 License:**

MIT License - Feel free to use, modify, and distribute.

---

### **🙏 Acknowledgments:**

- Flask & SQLAlchemy community
- TailwindCSS for styling
- OpenRouter for free Gemini API access
- DiceBear for avatar generation

---

## **Version Française (pour GitHub en français) :**

### **EST Social - Plateforme Sociale Gamifiée**

**EST Social** est une application web interactive développée avec **Flask** qui combine réseau social et apprentissage gamifié des langues. Conçue pour les étudiants, elle permet de pratiquer l'anglais via des mises en situation réelles, gagner de l'XP, monter de niveau et interagir avec des PNJ alimentés par IA.

---

### **Fonctionnalités principales :**

- **Fil d'actualité** : posts (images/vidéos), likes, commentaires audio, mode sombre
- **Jeu de rôle** : chat interactif dans lieux réels (Aéroport, Café, Hôtel)
- **Système de missions** : commander un café, demander son chemin, etc.
- **XP & Niveaux** : 12 niveaux avec grades (Nouveau → Légende)
- **Groupes** (niveau 3+) : créer des groupes, inviter des membres, publier
- **Panel Admin** : gestion des posts, configuration du site

---

### **Installation rapide :**

```bash
pip install -r requirements.txt
python app.py
```

**Admin par défaut :** `admin` / `admin123`

---

### **📬 Contact / Support:**

For issues or feature requests, please open an issue on GitHub.

---

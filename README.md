# 🎙️ VNote – Voice

VNote is a Flask-based web application that converts **voice to text** and **text/documents to speech**. It also supports **automatic language detection**, **translation**, user authentication, and history management, making it a complete voice note management system.

---

## ✨ Features

- 🎤 Convert Speech to Text using OpenAI Whisper
- 📝 Convert Text to Voice
- 📄 Read PDF and Word documents aloud
- 🌍 Automatic Language Detection
- 🔄 Translate extracted text into multiple languages
- 👤 User Registration & Login Authentication
- 📚 View Conversion History
- 💾 MySQL Database Integration
- 🎨 Responsive User Interface

---

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask

### Database
- MySQL

### Libraries
- OpenAI Whisper
- PyPDF2
- python-docx
- pyttsx3
- langdetect
- deep-translator
- Flask-MySQLdb
- Werkzeug

---

## 📂 Project Structure

```
VNote-Voice/
│
├── app.py
├── config.py
├── requirements.txt
│
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── voice_to_note.html
│   ├── note_to_voice.html
│   └── history.html
│
├── static/
│   ├── css/
│   └── audio/
│
├── uploads/
│
└── whisper_cache/
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/GanaparthiHarathi/VNote-Voice.git
cd VNote-Voice
```

### 2. Create Virtual Environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Setup

1. Install MySQL.
2. Create a database.

```sql
CREATE DATABASE vnote;
```

3. Create the required tables (such as `users` and history tables if applicable).

4. Update `config.py` with your MySQL credentials.

```python
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_password"
MYSQL_DB = "vnote"
```

---

## ▶️ Run the Application

```bash
python app.py
```

Open your browser and visit

```
http://127.0.0.1:5000
```

---

## 📋 Requirements

Main packages used:

- Flask
- Flask-MySQLdb
- OpenAI Whisper
- PyPDF2
- python-docx
- pyttsx3
- langdetect
- deep-translator
- Werkzeug

Install them using:

```bash
pip install -r requirements.txt
```

---

## 📖 How It Works

### Voice to Note

1. Upload an audio file.
2. Whisper converts speech into text.
3. Language is detected automatically.
4. Text can be translated into a selected language.
5. The result is displayed to the user.

### Note to Voice

1. Enter text or upload a PDF/DOCX file.
2. The application extracts the text.
3. Text is converted into speech.
4. Audio is generated for playback.

---

## 📸 Screens

- Home Page
- Login & Registration
- Voice to Note
- Note to Voice
- History

---

## 🔮 Future Enhancements

- Real-time voice recording
- Speech summarization
- AI-powered note organization
- Cloud storage integration
- Mobile application
- Dark mode
- Voice commands

---

## 👩‍💻 Author

**Harathi Ganaparthi**
**Nomitha Pathivada**


B.Tech – Computer Science & Engineering (Artificial Intelligence)

GitHub: https://github.com/GanaparthiHarathi

---

## 📄 License

This project is developed for educational and learning purposes.

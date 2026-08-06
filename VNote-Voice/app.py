from PyPDF2 import PdfReader
from docx import Document
import pyttsx3
import os
import whisper

from langdetect import detect
from deep_translator import GoogleTranslator

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash
)

from flask_mysqldb import MySQL

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

import config


# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

app.config["MYSQL_HOST"] = config.MYSQL_HOST
app.config["MYSQL_USER"] = config.MYSQL_USER
app.config["MYSQL_PASSWORD"] = config.MYSQL_PASSWORD
app.config["MYSQL_DB"] = config.MYSQL_DB

mysql = MySQL(app)


# ---------------- WHISPER MODEL ----------------
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

model = whisper.load_model(
    "base",
    download_root=os.path.join(os.getcwd(), "whisper_cache")
)


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- VOICE PAGE ----------------
@app.route("/voice_to_note")
def voice_to_note():
    return render_template(
        "voice_to_note.html",
        converted_text="",
        translated_text="",
        detected_language=""
    )


# ---------------- NOTE TO VOICE PAGE ----------------
@app.route("/note_to_voice")
def note_to_voice():
    return render_template("note_to_voice.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]

        password = generate_password_hash(request.form["password"])

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO users(name,email,password)
            VALUES(%s,%s,%s)
        """, (name, email, password))

        mysql.connection.commit()
        cur.close()

        flash("Registration Successful")
        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT * FROM users WHERE email=%s
        """, [email])

        user = cur.fetchone()

        cur.close()

        if user and check_password_hash(user[3], password):

            session["user_id"] = user[0]
            session["name"] = user[1]

            return redirect("/")

        flash("Invalid Login")

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- UPLOAD AUDIO + WHISPER ----------------
@app.route("/upload-audio", methods=["POST"])
def upload_audio():

    audio = request.files["audio"]

    if audio.filename == "":
        return "No file selected"

    filename = secure_filename(audio.filename)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    upload_folder = os.path.join(BASE_DIR, "uploads")

    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, filename)
    audio.save(filepath)

    result = model.transcribe(filepath)
    text = result["text"]

    try:
        language = detect(text)
    except:
        language = "Unknown"

    target_language = request.form.get("target_language", "en")

    translated_text = GoogleTranslator(
        source="auto",
        target=target_language
    ).translate(text)

    return render_template(
        "voice_to_note.html",
        converted_text=text,
        translated_text=translated_text,
        detected_language=language
    )


# ---------------- SAVE NOTE ----------------
@app.route("/save-note", methods=["POST"])
def save_note():

    if "user_id" not in session:
        return redirect("/login")

    original_text = request.form["original_text"]
    translated_text = request.form["translated_text"]

    detected_language = session.get("language", "Unknown")
    audio_file = session.get("audio_file", "")

    cur = mysql.connection.cursor()

    cur.execute("""
        INSERT INTO notes(
            user_id,
            original_text,
            translated_text,
            detected_language,
            audio_file
        )
        VALUES(%s,%s,%s,%s,%s)
    """, (
        session["user_id"],
        original_text,
        translated_text,
        detected_language,
        audio_file
    ))

    mysql.connection.commit()
    cur.close()

    return redirect("/history")


# ---------------- HISTORY ----------------
@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT id,
                original_text,
                translated_text,
                detected_language,
                audio_file,
                created_at
        FROM notes
        WHERE user_id=%s
        ORDER BY id DESC
        """, [session["user_id"]])

    notes = cur.fetchall()
    cur.close()

    return render_template("history.html", notes=notes)

@app.route("/save-audio-history", methods=["POST"])
def save_audio_history():

    if "user_id" not in session:
        return redirect("/login")

    text = request.form["text"]
    language = request.form["language"]
    audio_file = request.form["audio_file"]

    cur = mysql.connection.cursor()

    cur.execute("""
        INSERT INTO notes(
            user_id,
            original_text,
            translated_text,
            detected_language,
            audio_file
        )
        VALUES(%s,%s,%s,%s,%s)
    """, (
        session["user_id"],
        text,
        text,
        language,
        audio_file
    ))

    mysql.connection.commit()
    cur.close()

    return redirect("/history")
# ---------------- TEXT TO AUDIO ----------------
@app.route("/generate-audio", methods=["POST"])
def generate_audio():

    text = request.form.get("text", "").strip()
    language = request.form["language"]
    voice = request.form["voice"]

    if text == "":

        uploaded_file = request.files.get("note_file")

        if uploaded_file and uploaded_file.filename != "":

            filename = uploaded_file.filename.lower()

            if filename.endswith(".txt"):
                text = uploaded_file.read().decode("utf-8")

            elif filename.endswith(".pdf"):
                pdf = PdfReader(uploaded_file)
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            elif filename.endswith(".docx"):
                doc = Document(uploaded_file)
                text = "\n".join([p.text for p in doc.paragraphs])

            else:
                return "Unsupported file type"

    output_folder = os.path.join("static", "audio")
    os.makedirs(output_folder, exist_ok=True)

    output_file = os.path.join(output_folder, "output.mp3")

    engine = pyttsx3.init()
    engine.setProperty("rate", 160)
    engine.save_to_file(text, output_file)
    engine.runAndWait()

    return render_template(
        "note_to_voice.html",
        audio_ready=True,
        text=text,
        language=language,
        voice=voice,
        audio_file="audio/output.mp3"
    )


# ---------------- DELETE SINGLE NOTE ----------------
@app.route("/delete/<int:note_id>")
def delete(note_id):

    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        DELETE FROM notes
        WHERE id=%s AND user_id=%s
    """, (note_id, session["user_id"]))

    mysql.connection.commit()
    cur.close()

    return redirect("/history")


# ---------------- DELETE ALL HISTORY ----------------
@app.route("/delete-all-history")
def delete_all_history():

    if "user_id" not in session:
        return redirect("/login")

    cur = mysql.connection.cursor()

    cur.execute("""
        DELETE FROM notes
        WHERE user_id=%s
    """, (session["user_id"],))

    mysql.connection.commit()
    cur.close()

    return redirect("/history")

from flask import send_file
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

@app.route("/download-pdf", methods=["POST"])
def download_pdf():

    text = request.form.get("text", "")

    if not text.strip():
        return "No text found"

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    content = []

    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 10))

    doc.build(content)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="vnote_output.pdf",
        mimetype="application/pdf"
    )

from io import BytesIO
from flask import send_file

@app.route("/download-doc", methods=["POST"])
def download_doc():

    text = request.form.get("text", "")

    if not text.strip():
        return "No text found"

    buffer = BytesIO()
    buffer.write(text.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="vnote_output.doc",
        mimetype="application/msword"
    )
# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
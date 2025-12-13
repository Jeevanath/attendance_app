from flask import Flask, render_template, request, redirect, session, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename
from processing import process_excel   # keep your existing logic

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- CONFIG ----------------
USERS = {
    "admin": {"password": "vilvan123", "role": "admin"},
    "employee": {"password": "emp123", "role": "employee"}
}

UPLOAD_FOLDER = "data"
ALLOWED_EXTENSIONS = {"xls", "xlsx"}
ATTENDANCE_FILE = os.path.join(UPLOAD_FOLDER, "attendance.xlsx")
PROCESSED_FILE = os.path.join(UPLOAD_FOLDER, "processed.xlsx")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- HELPERS ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        if user in USERS and USERS[user]["password"] == pwd:
            session["user"] = user
            session["role"] = USERS[user]["role"]
            return redirect("/dashboard")

        return render_template("login.html", error="Incorrect username or password")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", role=session["role"])


@app.route("/upload", methods=["GET", "POST"])
def upload_excel():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            return render_template("upload.html", error="No file selected")

        if not allowed_file(file.filename):
            return render_template("upload.html", error="Only .xls or .xlsx allowed")

        filename = secure_filename(file.filename)
        ext = filename.rsplit(".", 1)[1].lower()
        temp_path = os.path.join(UPLOAD_FOLDER, filename)

        # Save uploaded file temporarily
        file.save(temp_path)

        # ---- AUTO CONVERT XLS → XLSX ----
        if ext == "xls":
            df = pd.read_excel(temp_path, engine="xlrd")
            df.to_excel(ATTENDANCE_FILE, index=False, engine="openpyxl")
            os.remove(temp_path)
        else:
            os.replace(temp_path, ATTENDANCE_FILE)

        return redirect("/actual")

    return render_template("upload.html")


@app.route("/actual")
def actual():
    if "user" not in session:
        return redirect("/")

    if not os.path.exists(ATTENDANCE_FILE):
        return "Attendance file not found", 404

    df = pd.read_excel(ATTENDANCE_FILE, engine="openpyxl")
    return render_template(
        "actual.html",
        table=df.to_html(index=False, classes="table table-striped table-bordered")
    )


@app.route("/customised")
def customised():
    if "user" not in session:
        return redirect("/")

    if not os.path.exists(ATTENDANCE_FILE):
        return "Attendance file not found", 404

    df = process_excel(ATTENDANCE_FILE)
    df.to_excel(PROCESSED_FILE, index=False, engine="openpyxl")

    return render_template(
        "customised.html",
        table=df.to_html(index=False, classes="table table-striped table-bordered")
    )


@app.route("/download")
def download():
    if "user" not in session:
        return redirect("/")

    if not os.path.exists(PROCESSED_FILE):
        return "Processed file not found", 404

    return send_file(PROCESSED_FILE, as_attachment=True)


@app.route("/logout")
def logout():
    # Cleanup files
    for f in [ATTENDANCE_FILE, PROCESSED_FILE]:
        if os.path.exists(f):
            os.remove(f)

    session.clear()
    return redirect("/")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)

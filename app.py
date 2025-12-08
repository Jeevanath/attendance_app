from flask import Flask, render_template, request, redirect, session, send_file
import pandas as pd
from processing import process_excel
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

USERS = {
    "admin": {"password": "vilvan123", "role": "admin"},
    "employee": {"password": "emp123", "role": "employee"}
}

UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
        file = request.files["file"]
        if file:
            file.save(os.path.join(UPLOAD_FOLDER, "attendance.xlsx"))
            return redirect("/actual")

    return render_template("upload.html")


@app.route("/actual")
def actual():
    if "user" not in session:
        return redirect("/")

    df = pd.read_excel("data/attendance.xlsx")
    return render_template("actual.html", table=df.to_html(index=False, classes="table table-striped table-bordered"))


@app.route("/customised")
def customised():
    if "user" not in session:
        return redirect("/")

    df = process_excel("data/attendance.xlsx")
    df.to_excel("data/processed.xlsx", index=False)

    return render_template("customised.html", table=df.to_html(index=False, classes="table table-striped table-bordered"))


@app.route("/download")
def download():
    if "user" not in session:
        return redirect("/")
    return send_file("data/processed.xlsx", as_attachment=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

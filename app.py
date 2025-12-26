from flask import Flask, render_template, request, redirect, session, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename
<<<<<<< HEAD
from string import Template
from processing import process_excel, generate_emp_rtf_from_df   # keep your existing logic
from rtf_process import generate_rtf

=======
from processing import process_excel   # keep your existing logic
>>>>>>> 627dbccd9164190ee095cb33cfcdd1a218e67d04

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- CONFIG ----------------
USERS = {
    "admin": {"password": "vilvan123", "role": "admin"},
    "employee": {"password": "emp123", "role": "employee"}
}

UPLOAD_FOLDER = "data"
<<<<<<< HEAD
REPORT_FOLDER = "reports"
ALLOWED_EXTENSIONS = {"xls", "xlsx"}
ATTENDANCE_FILE = os.path.join(UPLOAD_FOLDER, "attendance.xlsx")
PROCESSED_FILE = os.path.join(UPLOAD_FOLDER, "processed.xlsx")
REPORT_TEMPLATE = os.path.join(REPORT_FOLDER, "report_template/template.rtf")
REPORT_FILE = os.path.join(REPORT_FOLDER, "output.rtf")
=======
ALLOWED_EXTENSIONS = {"xls", "xlsx"}
ATTENDANCE_FILE = os.path.join(UPLOAD_FOLDER, "attendance.xlsx")
PROCESSED_FILE = os.path.join(UPLOAD_FOLDER, "processed.xlsx")
>>>>>>> 627dbccd9164190ee095cb33cfcdd1a218e67d04

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- HELPERS ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

<<<<<<< HEAD

def load_processed_employees():
    if not os.path.exists(PROCESSED_FILE):
        return None

    p_df = pd.read_excel(PROCESSED_FILE)
    if p_df is None:
        return None

    return generate_emp_rtf_from_df(p_df)


=======
>>>>>>> 627dbccd9164190ee095cb33cfcdd1a218e67d04
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
<<<<<<< HEAD
    processed_dfs["current"] = df
=======
>>>>>>> 627dbccd9164190ee095cb33cfcdd1a218e67d04
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


<<<<<<< HEAD

@app.route("/download-report")
def download_report():
    if "user" not in session:
        return redirect("/")

    if not os.path.exists(PROCESSED_FILE):
        return "Attendance file not found", 404

    p_df = pd.read_excel(PROCESSED_FILE)

    if p_df is None:
        return "No processed data", 400

    EMPLOYEES = generate_emp_rtf_from_df(p_df)
    with open(REPORT_TEMPLATE, "r", encoding="utf-8") as f:
        tpl = Template(f.read())

    filled_rtf = generate_rtf(EMPLOYEES["VRE0008"], tpl)

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(filled_rtf)

    return send_file(REPORT_FILE, as_attachment=True)









@app.route("/download-report/all")
def download_report_all():
    if "user" not in session:
        return redirect("/")

    EMPLOYEES = load_processed_employees()
    if EMPLOYEES is None:
        return "Attendance file not found", 404

    with open(REPORT_TEMPLATE, "r", encoding="utf-8") as f:
        tpl = Template(f.read())

    # generate report for ALL employees
    filled_rtf = generate_rtf_all(EMPLOYEES, tpl)

    output_file = "TimeCard_Report_All.rtf"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(filled_rtf)

    return send_file(output_file, as_attachment=True)





@app.route("/download-report/employee")
def download_report_employee():
    if "user" not in session:
        return redirect("/")

    paycode = request.args.get("paycode")
    if not paycode:
        return "Paycode is required", 400

    EMPLOYEES = load_processed_employees()
    if EMPLOYEES is None:
        return "Attendance file not found", 404

    if paycode not in EMPLOYEES:
        return f"Employee {paycode} not found", 404

    with open(REPORT_TEMPLATE, "r", encoding="utf-8") as f:
        tpl = Template(f.read())

    filled_rtf = generate_rtf(EMPLOYEES[paycode], tpl)

    output_file = f"reports/TimeCard_{paycode}.rtf"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(filled_rtf)

    return send_file(output_file, as_attachment=True)











=======
>>>>>>> 627dbccd9164190ee095cb33cfcdd1a218e67d04
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

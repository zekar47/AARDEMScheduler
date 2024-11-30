from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from dataManager import loadData, saveData, FILENAME
from scheduleManager import addTeacher, addClassType, addOverride, setClassStatus, getTeachers, getStudentNameForSlot
from syncToSheets import getBotEmail
import json

app = Flask(__name__)
app.secret_key = 'secretKey'

# --- Routes ---
@app.route("/")
def home():
    """Displays the homepage with a list of teachers."""
    data = loadData()
    return render_template("index.html", teachers=data["teachers"])

@app.route("/addTeacher", methods=["GET", "POST"])
def addTeacherRoute():
    """Handles adding a new teacher."""
    if request.method == "POST":
        name = request.form["name"]
        spreadsheetLink = request.form["spreadsheetLink"]

        # Save teacher data
        teacherData = json.load(open('defaultTeacher.json', 'r'))
        data = loadData()
        addTeacher(data, name, teacherData)

        # Save the spreadsheet link in a file
        with open("teacherSpreadsheets.json", "r+") as f:
            spreadsheets = json.load(f)
            spreadsheets[name] = spreadsheetLink
            f.seek(0)
            json.dump(spreadsheets, f, indent=4)

        # Provide a message to the user
        flash(
            f"Teacher '{name}' has been added. Please ensure the bot's email address "
            f"'{getBotEmail()}' has access to modify the spreadsheet.",
            "info"
        )
        return redirect(url_for("home"))
    return render_template("addTeacher.html", bot_email=getBotEmail())

@app.route("/addClass", methods=["GET", "POST"])
def addClassRoute():
    """Handles adding a class or override."""
    data = loadData()
    if request.method == "POST":
        teacher = request.form["teacher"]
        classType = request.form["classType"]

        # Determine if it's an override or a regular class
        if classType in ['class', 'free', 'blocked']:
            day = request.form["day"]  # Dropdown ensures valid day
            time = request.form["time"]
            studentName = request.form.get("studentName")
            instrument = request.form.get("instrument")
            addClassType(data, teacher, day, time, classType, studentName.capitalize(), instrument.lower())
        elif classType in ['trial', 'makeup']:
            date = request.form["date"]  # Date input ensures correct format
            time = request.form["time"]
            studentName = request.form["studentName"]
            instrument = request.form["instrument"]
            addOverride(data, teacher, date, time, classType, studentName.title(), instrument.lower())
        return redirect(url_for("home"))
    return render_template("addClass.html", teachers=data["teachers"])

@app.route('/setClassStatus', methods=['GET', 'POST'])
def setClassStatusRoute():
    if request.method == 'POST':
        teacher = request.form.get('teacher')
        date = request.form.get('date')  # e.g., 2024-11-29
        time = request.form.get('time')  # e.g., 16:00
        name = request.form.get('name')
        action = request.form.get('action')  # cancelled or confirmed
        notes = request.form.get('notes', '')

        try:
            setClassStatus(teacher, date, time, name, action, notes, FILENAME)
            flash(f'Class {action} for {name} on {date} at {time}.', 'success')
        except ValueError as e:
            flash(str(e), 'error')
        return redirect(url_for('setClassStatusRoute'))

    # Fetch teacher names for the dropdown
    teachers = getTeachers(FILENAME)
    return render_template('setClassStatus.html', teachers=teachers)

@app.route('/getStudentName', methods=['GET'])
def getStudentName():
    teacher = request.args.get('teacher')
    date = request.args.get('date')  # e.g., 2024-11-29
    time = request.args.get('time')  # e.g., 16:00

    try:
        name = getStudentNameForSlot(teacher, date, time, FILENAME)
        return jsonify({"name": name})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/schedule/<teacher>")
def schedule(teacher):
    """Displays a teacher's schedule."""
    data = loadData()
    teacherSchedule = data["teachers"].get(teacher, {}).get("schedule", {})
    return render_template("schedule.html", teacher=teacher, schedule=teacherSchedule)

if __name__ == "__main__":
    app.run(debug=True)

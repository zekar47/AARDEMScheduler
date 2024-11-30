from datetime import datetime
from dataManager import saveData, loadData
from syncToSheets import syncToGoogleSheets

DAY_MAP = {
    "monday": "lunes",
    "tuesday": "martes",
    "wednesday": "miercoles",
    "thursday": "jueves",
    "friday": "viernes",
    "saturday": "sabado",
    "sunday": "domingo"
}

def addTeacher(data, teacherName, teacherData):
    """Adds a new teacher to the data."""
    data["teachers"][teacherName] = teacherData
    saveData(data)
    syncToGoogleSheets()

def addClassType(data, teacher, day, time, classType, studentName=None, instrument=None):
    """Adds a class to a teacher's schedule."""
    classInfo = {"time": time, "type": classType}
    if classType == 'class':
        classInfo.update({"name": studentName.capitalize(), "instrument": instrument.capitalize()})
    data["teachers"][teacher]["schedule"][day][time] = classInfo
    sortScheduleByTime(data["teachers"][teacher]["schedule"][day])
    saveData(data)
    syncToGoogleSheets()

def addOverride(data, teacher, date, time, classType, studentName=None, instrument=None):
    """Adds an override to a teacher's schedule."""
    overrideKey= f'{date}/{time}'
    overrideInfo = {
        "type": classType,
        "name": studentName,
        "instrument": instrument,
        "status": "pending",
        "notes": ""
    }

    # Initialize the key as a list if it doesn't exist
    if overrideKey not in data["teachers"][teacher]["overrides"]:
        data["teachers"][teacher]["overrides"][overrideKey] = []

    # Append the new override
    data["teachers"][teacher]["overrides"][overrideKey].append(overrideInfo)

    saveData(data)
    syncToGoogleSheets()

def getOverridesForSlot(data, teacher, date, time):
    """Retrieve all overrides for a specific date and time."""
    overrideKey = f'{date}/{time}'
    return data["teachers"][teacher]["overrides"].get(overrideKey, [])

def sortScheduleByTime(daySchedule):
    """Sorts the schedule for a single day by time."""
    sortedSchedule = dict(sorted(daySchedule.items(), key=lambda item: datetime.strptime(item[0], "%H:%M")))
    daySchedule.clear()
    daySchedule.update(sortedSchedule)

def setClassStatus(teacher, date, time, name, action, notes, filename):
    """
    Updates the schedule with a cancellation or confirmation for a specific teacher and class.
    """
    data = loadData(filename)
    if teacher not in data['teachers']:
        raise ValueError(f"Teacher '{teacher}' not found in the database.")
    
    teacherInfo = data['teachers'][teacher]
    overrideKey = f"{date}/{time}"

    # Initialize the overrides list if necessary
    if overrideKey not in teacherInfo['overrides']:
        teacherInfo['overrides'][overrideKey] = []

    # Append the new action as an override
    teacherInfo['overrides'][overrideKey].append({
        'type': action,  # 'cancelled' or 'confirmed'
        'name': name,
        'instrument': teacherInfo['schedule']
            .get("viernes", {})
            .get(time, {})
            .get("instrument", "Unknown"),
        'status': action,
        'notes': notes
    })

    saveData(data, filename)
    syncToGoogleSheets()

def getTeachers(filename):
    """
    Retrieve a list of teacher names from the database.
    """
    data = loadData(filename)
    return list(data['teachers'].keys())

def getStudentNameForSlot(teacher, date, time, filename):
    """
    Retrieves the student's name for the given teacher, date, and time.
    """
    data = loadData(filename)

    if teacher not in data['teachers']:
        raise ValueError(f"Teacher '{teacher}' not found in the database.")

    teacherInfo = data['teachers'][teacher]
    dayOfWeek = DAY_MAP.get(datetime.strptime(date, "%Y-%m-%d").strftime("%A").lower())

    # Check for overrides first
    overrideKey = f"{date}/{time}"
    if overrideKey in teacherInfo.get('overrides', {}):
        latestOverride = teacherInfo['overrides'][overrideKey][-1]
        return latestOverride.get('name', "No hay clase")

    # Otherwise, look at the regular schedule
    if dayOfWeek in teacherInfo['schedule'] and time in teacherInfo['schedule'][dayOfWeek]:
        return teacherInfo['schedule'][dayOfWeek][time].get('name', "No hay clase")

    return "No hay clase"

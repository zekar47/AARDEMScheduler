# Copyright (C) 2024 ZEKAR
#
# This file is part of AARDEMScheduler.
#
# AARDEMScheduler is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AARDEMScheduler is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AARDEMScheduler. If not, see <https://www.gnu.org/licenses/>.

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import datetime, timedelta
from dataManager import loadData
from dataManager import FILENAME
import os

# Constants and configuration
DAYSTR = {"lunes": 0, 
        "martes": 1,
        "miercoles": 2, 
        "jueves": 3,
        "viernes": 4,
        "sabado": 5}

DAYS = {"lunes": 'b', 
        "martes": 'c',
        "miercoles": 'd', 
        "jueves": 'e',
        "viernes": 'f',
        "sabado": 'g'}
TIMES = ["10:00", "10:45", "11:30", "12:15", "13:00", "13:45", "14:30", "15:15", "16:00", "16:45", "17:30", "18:15", "19:00"]
MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
CREDENTIALS = './aardemscheduler-010fc69f6d9f.json'
TRANSLATION = {'free': 'libre',
               'class': 'clase',
               'blocked': 'bloqueado',
               'makeup': 'reposición',
               'trial': 'Clase de Prueba'}

gc = gspread.service_account(filename=CREDENTIALS)

# Function to load spreadsheet links
def loadSpreadsheetLinks():
    """
    Loads the teacher-to-spreadsheet mapping from a JSON file.
    If the file doesn't exist, it creates an empty one.
    """
    filepath = "teacherSpreadsheets.json"
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            json.dump({}, f)
    with open(filepath, "r") as f:
        return json.load(f)

def getBotEmail(credentials=CREDENTIALS):
    """
    Extract the bot's email address from the service account credentials.
    """
    with open(credentials, "r") as f:
        credentialsData = json.load(f)
        return credentialsData.get("client_email", "unknown-email@example.com")

# Retrieve the Google Sheets spreadsheet by URL key
def getSpreadsheet(key):
    try: 
        print(f"Opening spreadsheet {key}")
        return gc.open_by_url(key)
    except gspread.SpreadsheetNotFound:
        print(f"Spreadsheet {key} not found")
        return None

# Formats class information to display in a cell
def formatClassInfo(timeSlot, classInfo):
    if classInfo['type'] == 'class':
        r = f'{timeSlot} \n{classInfo["name"]} \n{classInfo["instrument"]}'
    elif classInfo['type'] == 'free':
        r = f'{timeSlot} \n{TRANSLATION.get(classInfo["type"])}'
    elif classInfo['type'] == 'blocked':
        r = f'{timeSlot} \nBLOQUEADO'
    return r

def formatOverrideInfo(dtDay, classInfo):
    day = dtDay.day
    month = MONTHS[dtDay.month - 1]
    if classInfo['type'] == 'trial':
        return f'--- \nCP. {day} {month} \n{classInfo["name"]} \n{classInfo["instrument"]}'
    elif classInfo['type'] == 'makeup':
        return f'--- \nRep. {day} {month} \n{classInfo["name"]} \n{classInfo["instrument"]}'
    elif classInfo['type'] == 'cancelled':
        return f'No viene {day} {month}'
    elif classInfo['type'] == 'confirmed':
        return f'\nCONFIRMADO {day} {month}'
    return ""

# Prepares batch updates for schedule and overrides
def prepareBatchUpdates(teacherInfo):
    batchUpdates = []
    today = datetime.now()

    # Prepare schedule data with possible overrides for two weeks
    for dayName, dayInfo in teacherInfo['schedule'].items():
        for timeSlot, classInfo in dayInfo.items():
            row = TIMES.index(timeSlot) + 2
            col = DAYS.get(dayName)
            cellContent = formatClassInfo(timeSlot, classInfo)

            # Check if there's an override in the future
            for overrideKey, overrides in teacherInfo.get('overrides', {}).items():
                overrideDate, overrideTime = overrideKey.split("/")
                overrideDate = datetime.strptime(overrideDate, "%Y-%m-%d")
                
                if overrideTime == timeSlot and today <= overrideDate + timedelta(days=2):
                    if DAYSTR.get(dayName) == (overrideDate.weekday()):
                        for override in overrides:
                            cellContent += f"\n{formatOverrideInfo(overrideDate, override)}"

            # Add formatted cell content to batch updates
            batchUpdates.append({
                'range': f'{col}{row}:{col}{row}',
                'values': [[cellContent]]
            })
    return batchUpdates

def syncToGoogleSheets(credentials=CREDENTIALS, filename=FILENAME):
    """
    Syncs the schedule data from the database to Google Sheets for each teacher,
    using batch updates to optimize API requests.
    """
    data = loadData(filename)
    SPREADSHEETS = loadSpreadsheetLinks()

    for teacherName, teacherInfo in data['teachers'].items():
        spreadsheetUrl = SPREADSHEETS.get(teacherName)
        if not spreadsheetUrl:
            print(f"No spreadsheet URL configured for {teacherName}")
            continue

        # Open or create the teacher's spreadsheet
        spreadsheet = getSpreadsheet(spreadsheetUrl)
        if not spreadsheet:
            continue

        # Access the first worksheet (or create if none exists)
        worksheet = spreadsheet.get_worksheet(0) or spreadsheet.add_worksheet(title="Schedule", rows="20", cols="7")

        # Prepare and execute batch updates
        batchData = prepareBatchUpdates(teacherInfo)
        worksheet.batch_update(batchData, value_input_option='RAW')
        print(f"Synced schedule for {teacherName}")

if __name__ == '__main__':
    syncToGoogleSheets()

import json
FILENAME = 'db.json'

# --- Database Management ---
def loadData(filename=FILENAME):
    with open(filename, "r") as file:
        return json.load(file)

def saveData(data, filename=FILENAME, sync=False):
    with open(filename, "w") as file:
        json.dump(data, file, indent=2)

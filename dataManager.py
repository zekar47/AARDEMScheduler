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

import json
FILENAME = 'db.json'

# --- Database Management ---
def loadData(filename=FILENAME):
    with open(filename, "r") as file:
        return json.load(file)

def saveData(data, filename=FILENAME, sync=False):
    with open(filename, "w") as file:
        json.dump(data, file, indent=2)

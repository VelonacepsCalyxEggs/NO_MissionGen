import json
import copy
import random
import math

TEAM_SIZE = 4
PLAYER_TEAM = ""
FACTIONS = ["Primeva", "Boscali", "Neutral"]

# BOSCALI AIRCRAFT PLACEMENT
X_BOSCALI = 0
Y_BOSCALI = 300 # Height above sea level.
Z_BOSCALI = 0

# PRIMEVA AIRCRAFT PLACEMENT
X_PRIMEVA = 0
Y_PRIMEVA = 300
Z_PRIMEVA = 10000

class Aircraft:
    def __init__(self, type, faction, unique_name, x, y, z, rotation_y, livery, weapon_selections, skill_range, bravery_range, speed_range):
        self.type = type
        self.faction = faction
        self.unique_name = unique_name
        self.global_position = {"x": x, "y": y, "z": z}
        self.rotation = {"x": 0.0, "y": rotation_y, "z": 0.0, "w": 0.0}
        self.spawn_timing = ""
        self.player_controlled = False
        self.player_controlled_priority = 0
        self.loadout = {"weaponSelections": weapon_selections}
        self.livery = livery
        self.livery_type = 0
        self.livery_name = ""
        self.skill = round(random.uniform(*skill_range), 2)
        self.bravery = round(random.uniform(*bravery_range), 2)
        self.starting_speed = round(random.uniform(*speed_range), 1)
    
    def to_dict(self):
        return {
            "type": self.type,
            "faction": self.faction,
            "UniqueName": self.unique_name,
            "unitCustomID": "",
            "globalPosition": self.global_position,
            "rotation": self.rotation,
            "spawnTiming": self.spawn_timing,
            "playerControlled": self.player_controlled,
            "playerControlledPriority": self.player_controlled_priority,
            "loadout": self.loadout,
            "livery": self.livery,
            "liveryType": self.livery_type,
            "liveryName": self.livery_name,
            "skill": self.skill,
            "bravery": self.bravery,
            "startingSpeed": self.starting_speed
        }

# Define specific templates for each aircraft type
# Also, it is a pain getting all the avaivable weapon selections... there should be an easier way...
aircraft_templates = {
    "COIN": {"weapon_selections": [1, 2, 6, 4], "skill_range": (1.0, 5.0), "bravery_range": (0.0, 1.0), "speed_range": (100.0, 150.0)},
    "trainer": {"weapon_selections": [1, 2, 3, 4], "skill_range": (1.0, 5.0), "bravery_range": (0.0, 1.0), "speed_range": (250.0, 400.0)},
    "Multirole1": {"weapon_selections": [1, 3, 5, 7], "skill_range": (1.0, 5.0), "bravery_range": (0.0, 1.0), "speed_range": (400.0, 600.0)},
    "Fighter1": {"weapon_selections": [2, 4, 6, 8], "skill_range": (1.0, 5.0), "bravery_range": (0.0, 1.0), "speed_range": (400.0, 600.0)},
    "AttackHelo1": {"weapon_selections": [0, 1, 2, 3], "skill_range": (1.0, 5.0), "bravery_range": (0.0, 1.0), "speed_range": (100.0, 200.0)},
    "Darkreach": {"weapon_selections": [3, 4, 5, 6], "skill_range": (1.0, 5.0), "bravery_range": (0.0, 1.0), "speed_range": (200.0, 320.0)},
    "EW1": {"weapon_selections": [1, 2, 3, 4], "skill_range": (1.0, 5.0), "bravery_range": (0.0, 1.0), "speed_range": (250.0, 350.0)},
    "QuadVTOL1": {"weapon_selections": [0, 2, 4, 6], "skill_range": (1.0, 5.0), "bravery_range": (0.0, 1.0), "speed_range": (100.0, 150.0)}
}

# Load the mission template
with open("./templates/mission_template.json", "r") as f:
    mission_template = json.loads(f.read())

with open("./templates/ship_template.json", "r") as f:
    ship_templates = json.loads(f.read())


# Create the mission
mission = copy.deepcopy(mission_template)

with open("./templates/objective_templates.json", "r") as f:
    objective_templates = json.load(f)



# Assign airbases.
for airbase in (mission["airbases"]):
    airbase["faction"] = random.choice(FACTIONS)
    #print(f"{airbase["DisplayName"]} was set to faction {airbase["faction"]}.")

# Add fleets
def calculate_endpoint(length, angle):
    # Convert angle to radians if it's in degrees
    # Wibbley wobbley timey wimey trigonometry stuff...
    angle_radians = math.radians(angle)
    x = length * math.cos(angle_radians)
    z = length * math.sin(angle_radians)
    return x, z 

# Add fleets with 4 corvettes and 1 destroyer around each carrier
for i in range(1, 3):  # Assuming 2 carriers, constant it later
    if i % 2 == 0:
        carrier_faction = FACTIONS[0]
    else:
        carrier_faction = FACTIONS[1]
    
    carrier = copy.deepcopy(ship_templates[0])
    random_angle = random.randint(0, 359)
    carrier_x, carrier_z = calculate_endpoint(60000, random_angle)
    carrier["globalPosition"]["x"] = carrier_x
    carrier["globalPosition"]["z"] = carrier_z
    carrier["faction"] = carrier_faction
    carrier["UniqueName"] = "FleetCarrier" + str(i)
    print(carrier["UniqueName"])
    mission["ships"].append(carrier)

    # Place 4 corvettes around the carrier
    for j in range(4):
        angle = random_angle + (j * 90)
        corvette_x, corvette_z = calculate_endpoint(5000, angle)  # 5000 units away from carrier
        corvette = copy.deepcopy(ship_templates[1])
        corvette["globalPosition"]["x"] = carrier_x + corvette_x
        corvette["globalPosition"]["z"] = carrier_z + corvette_z
        corvette["faction"] = carrier_faction
        corvette["UniqueName"] = f"Corvette{i}_{j+1}"
        mission["ships"].append(corvette)
        print(corvette["UniqueName"], "at", corvette["globalPosition"])

    # Place 1 destroyer 10000 units away from the carrier
    destroyer_angle = random_angle + 45  # Place it diagonally
    destroyer_x, destroyer_z = calculate_endpoint(10000, destroyer_angle)
    destroyer = copy.deepcopy(ship_templates[2])
    destroyer["globalPosition"]["x"] = carrier_x + destroyer_x
    destroyer["globalPosition"]["z"] = carrier_z + destroyer_z
    destroyer["faction"] = carrier_faction
    destroyer["UniqueName"] = f"Destroyer{i}"
    mission["ships"].append(destroyer)
    print(destroyer["UniqueName"], "at", destroyer["globalPosition"])


# Add Boscali aircraft
for i in range(1, TEAM_SIZE + 1):
    type_choice = random.choice(list(aircraft_templates.keys()))
    template = aircraft_templates[type_choice]
    aircraft = Aircraft(type=type_choice, 
                        faction="Boscali", 
                        unique_name="Boscali_" + str(i), 
                        x=X_BOSCALI, 
                        y = Y_BOSCALI, 
                        z=Z_BOSCALI, 
                        rotation_y=0, 
                        livery=0, 
                        weapon_selections=template["weapon_selections"],
                        skill_range=template["skill_range"], 
                        bravery_range=template["bravery_range"], 
                        speed_range=template["speed_range"])
    mission["aircraft"].append(aircraft.to_dict())
    X_BOSCALI += 25
    print(i)

# Add Primeva aircraft
for i in range(1, TEAM_SIZE + 1):
    type_choice = random.choice(list(aircraft_templates.keys()))
    template = aircraft_templates[type_choice]
    aircraft = Aircraft(type=type_choice, 
                        faction="Primeva", 
                        unique_name="Primeva_" + str(i), 
                        x=X_PRIMEVA, 
                        y = Y_PRIMEVA,
                        z=Z_PRIMEVA, 
                        rotation_y=1, 
                        livery=3, 
                        weapon_selections=template["weapon_selections"],
                        skill_range=template["skill_range"], 
                        bravery_range=template["bravery_range"], 
                        speed_range=template["speed_range"])
    mission["aircraft"].append(aircraft.to_dict())
    X_PRIMEVA += 25
    print(i)

random.choice(mission["aircraft"])["playerControlled"] = True


def editObjectives():
    allBoscaliAircraft = []
    allPrimevaAircraft = []

    for aircraft in mission["aircraft"]:
        if aircraft["faction"] == "Boscali":
            aircraftObjectiveTemp = {
                "StringValue": aircraft["UniqueName"],
                "FloatValue": 0.0,
                "VectorValue": {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            }
            allBoscaliAircraft.append(aircraftObjectiveTemp)
        
        if aircraft["faction"] == "Primeva":
            aircraftObjectiveTemp = {
                "StringValue": aircraft["UniqueName"],
                "FloatValue": 0.0,
                "VectorValue": {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            }
            allPrimevaAircraft.append(aircraftObjectiveTemp)
    
    # Find the objectives by UniqueName and update their Data.
    for objective in objective_templates[0]["Objectives"]:
        if objective["UniqueName"] == "DestroyBoscali":
            objective["Data"].extend(allBoscaliAircraft)   
        
        if objective["UniqueName"] == "DestroyPrimeva":
            objective["Data"].extend(allPrimevaAircraft)  

    mission["objectives"] = objective_templates[0]
editObjectives()

# Write the mission to the file
with open('C:/Users/ivank/Documents/NO_MIssionGen/mission.json', 'w') as f:
    json.dump(mission, f, indent=4)
    print("Mission generated succsessfully.")
import json
import copy
import random
import math
import os

# CONFIG
TEAM_SIZE = 16
FACTIONS = ["Primeva", "Boscali", "Neutral"]
SAME_TYPE = True  # Set to True for aircraft of the same type
MANUAL_TYPE = "COIN"  # Set to a specific type if SAME_TYPE is True
MANUAL_SPEED = None  # Set to a specific speed to manually assign to all aircraft

# Doesn't work like I wanted to... so best set to False, although it can be fun.
ENABLE_BALANCING = False  # Set to False to disable balancing

# BOSCALI AIRCRAFT PLACEMENT
X_BOSCALI = 0
Y_BOSCALI = 300  # Height above sea level
Z_BOSCALI = 0

# PRIMEVA AIRCRAFT PLACEMENT
X_PRIMEVA = 0
Y_PRIMEVA = 300
Z_PRIMEVA = 10000

# Group spacing offsets
GROUP_OFFSET_X = 500
GROUP_OFFSET_Z = 500
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


def copy_mission_file_to_game(mission):
    try:
        local_low_path = os.path.expandvars("%USERPROFILE%/AppData/LocalLow/Shockfront/NuclearOption/Missions/QuickGenMission")
        
        if not os.path.exists(local_low_path):
            return print("Please make a mission titled 'QuickGenMission'!")
        with open(local_low_path + "/QuickGenMission.json", "w") as f:
            json.dump(mission, f, indent=4)
        print("Mission files ported to game successfully.")
    except IOError as e:
        print(e)

def load_json(json_path):
    with open(json_path, "r") as f:
        return json.loads(f.read())

def assign_airbases(mission):
    for airbase in (mission["airbases"]):
        airbase["faction"] = random.choice(FACTIONS)

def add_fleets(ship_templates, mission):
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

def balance_teams_by_role(aircraft_templates, team_size):
    roles = ["interceptor", "multirole", "ground-attack", "bomber", "electronic-warfare", "transport"]
    team1 = []
    team2 = []

    for role in roles:
        role_aircraft = [atype for atype, details in aircraft_templates.items() if details["role"] == role]
        if role_aircraft:
            random.shuffle(role_aircraft)
            for i in range(min(team_size // len(roles), len(role_aircraft))):
                if i % 2 == 0:
                    team1.append(role_aircraft[i % len(role_aircraft)])
                else:
                    team2.append(role_aircraft[i % len(role_aircraft)])

    return team1, team2

def place_aircraft(x_pos, y_pos, z_pos, rot_y, team_faction, aircraft_templates, aircraft_types, formation_positions):
    # Add aircraft
    aircraft_list = []
    group_count = 0
    for i in range(1, TEAM_SIZE + 1):
        if ENABLE_BALANCING:
            type_choice = aircraft_types[i % len(aircraft_types)]
        else:
            if SAME_TYPE:
                type_choice = MANUAL_TYPE
            else:
                type_choice = random.choice(list(aircraft_templates.keys()))
        template = aircraft_templates[type_choice]
        aircraft_speed = MANUAL_SPEED if MANUAL_SPEED is not None else random.uniform(*template["speed_range"])
        position = formation_positions[template["role"]]
        aircraft = Aircraft(type=type_choice, 
                            faction=team_faction, 
                            unique_name=f"{team_faction}_" + str(i), 
                            x = x_pos + (group_count * GROUP_OFFSET_X if ENABLE_BALANCING else i * 50),
                            y = y_pos,
                            z = z_pos + (group_count * GROUP_OFFSET_Z if ENABLE_BALANCING else 0),
                            rotation_y = rot_y, 
                            livery = 3, 
                            weapon_selections = template["weapon_selections"],
                            skill_range = (1.0, 5.0),  # Default skill range
                            bravery_range = (0.0, 1.0),  # Default bravery range
                            speed_range = (aircraft_speed, aircraft_speed))
        aircraft_list.append(aircraft.to_dict())
        if ENABLE_BALANCING and i % len(formation_positions) == 0:
            group_count += 1

    return aircraft_list

def edit_objectives(mission, objective_templates):
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

def main():
    mission_template = load_json("./templates/mission_template.json")
    ship_templates = load_json("./templates/ship_template.json")
    objective_templates = load_json("./templates/objective_templates.json")
    
    # It is a pain getting all the avaivable weapon selections... there should be an easier way...
    aircraft_templates = {
        "COIN": {"role": "ground-attack", "weapon_selections": list(range(0, 16)), "speed_range": (100.0, 150.0)},
        "trainer": {"role": "multirole", "weapon_selections": list(range(0, 16)), "speed_range": (250.0, 400.0)},
        "Multirole1": {"role": "multirole", "weapon_selections": list(range(0, 16)), "speed_range": (400.0, 600.0)},
        "Fighter1": {"role": "interceptor", "weapon_selections": list(range(0, 16)), "speed_range": (400.0, 600.0)},
        "AttackHelo1": {"role": "ground-attack", "weapon_selections": list(range(0, 16)), "speed_range": (100.0, 200.0)},
        "Darkreach": {"role": "bomber", "weapon_selections": list(range(0, 16)), "speed_range": (200.0, 320.0)},
        "EW1": {"role": "electronic-warfare", "weapon_selections": list(range(0, 16)), "speed_range": (250.0, 350.0)},
        "QuadVTOL1": {"role": "transport", "weapon_selections": list(range(0, 16)), "speed_range": (100.0, 150.0)}
    }

    formation_positions = {
        "interceptor": {"x_offset": 50, "z_offset": 90},
        "multirole": {"x_offset": 90, "z_offset": 90},
        "ground-attack": {"x_offset": 80, "z_offset": 20},
        "bomber": {"x_offset": 180, "z_offset": 100},
        "electronic-warfare": {"x_offset": 150, "z_offset": 150},
        "transport": {"x_offset": 200, "z_offset": 150}
    }


    if not mission_template or not ship_templates or not objective_templates:
        return

    mission = copy.deepcopy(mission_template)

    assign_airbases(mission)

    add_fleets(ship_templates, mission)
    rotation_y_boscali = 0.0
    rotation_y_primeva = 1.0

    if ENABLE_BALANCING:
        # Balance teams by roles
        team1_types, team2_types = balance_teams_by_role(aircraft_templates, TEAM_SIZE)
    else:
        # Randomize aircraft types if balancing is disabled
        all_aircrafts = list(aircraft_templates.keys())
        random.shuffle(all_aircrafts)
        team1_types = [all_aircrafts[i % len(all_aircrafts)] for i in range(1, TEAM_SIZE + 1)]
        team2_types = [all_aircrafts[i % len(all_aircrafts)] for i in range(1, TEAM_SIZE + 1)]

    boscali_aircraft = place_aircraft(X_BOSCALI, Y_BOSCALI, Z_BOSCALI, rotation_y_boscali, FACTIONS[1], aircraft_templates, team1_types, formation_positions)
    primeva_aircraft = place_aircraft(X_PRIMEVA, Y_PRIMEVA, Z_PRIMEVA, rotation_y_primeva, FACTIONS[0], aircraft_templates, team2_types, formation_positions)
    mission["aircraft"].extend(boscali_aircraft)
    mission["aircraft"].extend(primeva_aircraft)
    
    # Choose a random aircraft for a player to control. 
    # I have priorities listed out for later use.
    random.choice(mission["aircraft"])["playerControlled"] = True

    edit_objectives(mission, objective_templates)

    try:
        with open('C:/Users/ivank/Documents/NO_MIssionGen/mission.json', 'w') as f:
            json.dump(mission, f, indent=4)
            print("Mission generated successfully.")
            copy_mission_file_to_game(mission)
    except IOError as e:
        print("Error: Failed to write mission to file.")
        print(e)

if __name__ == "__main__":
    main()
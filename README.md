# Nuclear Option Mission Generator

This is a mission generator for the game "Nuclear Option".

## Description

"Nuclear Option" is a game where you fly near-future aircraft with immersive physics on intense battlefields, facing land, air, and sea threats. Wage war against AI or other players with an array of potent weapons. Wield tactical and strategic nuclear weapons, capable of annihilating anything in their path.

This repository utilizes the game's flexible .json structure of missions, to create quick missions from scratch.

## Features

- Generate missions with custom parameters.
- Create diverse scenarios involving aircraft and naval vessels.
- Set faction-specific aircraft and ship placements.
- Modify mission objectives. Soon... 

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/VelonacepsCalyxEggs/NO_MissionGen.git
   ```
2. Navigate to project directory:
    ```sh
    cd NO_MissionGen
    ```


## Usage
Run the missionGen.py file:
   1. Create an empty mission named "QuickGenMission" in the game.
   2.  Run the script:
    ```
    python missionGen.py
    ```
## Configuration
Currently the script can be configured by modifying constants in the beginning of the [missionGen.py](https://github.com/VelonacepsCalyxEggs/NO_MissionGen/blob/main/missionGen.py) file.
```py
TEAM_SIZE = 4
PLAYER_TEAM = ""
FACTIONS = ["Primeva", "Boscali", "Neutral"]

SAME_TYPE = True  # Set to True for aircraft of the same type
MANUAL_TYPE = "COIN"  # Set to a specific type if SAME_TYPE is True
MANUAL_SPEED = 300  # Set to a specific speed to manually assign to all aircraft

# BOSCALI AIRCRAFT PLACEMENT
X_BOSCALI = 0
Y_BOSCALI = 300 # Height above sea level.
Z_BOSCALI = 0

# PRIMEVA AIRCRAFT PLACEMENT
X_PRIMEVA = 0
Y_PRIMEVA = 300
Z_PRIMEVA = 10000
```
### P.S.
This code may break something because it is using the file system to update the mission in the NO folder.
Anything can happen. You have been warned.

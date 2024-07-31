# Cascade Tile Scanner  
This is a simple script to help you figure out exactly what tiles you have upon loading into a mission to help save time while rerolling.  
Simply launch the script and the overlay will appear to the top left, with red text reading "Awaiting Cascade..." and the current Zariman faction cycle.  
When loading in to a mission, it will display the 3 main rooms in the map, along with how many exolizers will spawn in that room.    
Depending on the total amount of exolizers, the color of the HUD will change.  
![image](https://github.com/user-attachments/assets/91a5d367-398e-4fd3-b5d5-f6a9ea9712ea)  
10 or less Exolizers = Red  
11 Exolizers = Green  
12 Exolizers = Cyan  
13 Exolizers = Magenta  

Additionally, if a Void Fissure appears on SP Void Cascade it will show a label with the remaining time  
![image](https://github.com/user-attachments/assets/205fbe93-84bb-4b35-9911-f6f6d7eb0e22)


### Installation
Download EXE from [releases]() or clone this repository and run it yourself through Python.

### Compiling / Running it yourself
if this doesn't work, feel free to ask about it
1. Install python
2. Open up the folder in a terminal
3. Run `pip install -r requirements.txt`
4. Run `py CascadeTileScanner.py` to launch it  
   or run `pip install pyinstaller` then `pyinstaller CascadeTileScanner.py` to compile the script to an EXE.  
   The compiled .exe should be inside the `dist` folder

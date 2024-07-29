import os
import sys
import time
import tkinter as tk
import threading
import win32con
import win32gui
import requests
from datetime import datetime

connectors = {
    "test": "bwah"
}

# Constants
LOG_FILE_PATH = os.getenv('LOCALAPPDATA') + r'\Warframe\EE.log'
API_URL = "https://api.warframestat.us/pc/"
TILE_COLORS = ["red", "green", "cyan", "magenta"]
ARROW_CHARACTER = "→" if sys.getdefaultencoding() in {"utf-8", "utf-16"} else "->"

# Defaults
loadedMessage = True # set to true if you're an alt tab gamer
default_fissures = {
    "active": False,
    "node": "unknown",
    "missionType": "unknown",
    "expired": False,
    "eta": "unkown",
    "isHard": False
}
default_zariman_cycle = {
    "state": "unknown",
    "timeLeft": "unknown",
    "shortString": "unknown"
}
original_tilesets = {
    "IntHydroponics": "Dogshit (3)",
    "IntLivingQuarters": "Ramp (3)",
    "IntCargoBay": "Cargo Bay (3)",
    "IntAmphitheatre": "Amphitheatre (3)",
    "IntIndoctrinationHall": "Hall (3)",
    "IntLunaroCourt": "Lunaro (3)",
    "IntCellBlockA": "Brig (3)",
    "IntSchool": "Schoolyard (4)",
    "IntPark": "Statue (4)",
    "IntParkB": "Park (4)",
    "IntParkC": "Roost (4)",
    "IntShuttleBay": "Shipyard (5)"
}
tilesets = original_tilesets.copy()

def get_fissure_state(retry_delay=5, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            return response.json().get("fissures", default_fissures)
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching fissures data: {e}")
            if attempt < max_retries + 1:
                print(f"Rtrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                
    print("Failed to fetch fissure data after several attempts.")
    return default_fissures

def get_zariman_cycle(retry_delay=5, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.json().get("zarimanCycle", default_zariman_cycle)
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching Zariman cycle data: {e}")
            if attempt < max_retries + 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    print("Failed to fetch Zariman cycle data after several attempts.")
    return default_zariman_cycle

def follow(thefile):
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

class Overlay:
    def __init__(self):
        self.path = None
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")
        self.root.attributes("-alpha", 0.5) # Transparency

        # Define the labels
        # Tiles
        self.label_cascade = tk.Label(self.root, text="i stole this from wally :D", fg="red", bg="black", font=("Times New Roman", 15, ""))

        # Faction State
        self.state_frame = tk.Frame(self.root, bg="black")
        self.label_state_prefix = tk.Label(self.state_frame, text="State: ", fg="white", bg="black", font=("Times New Roman", 10, ""))
        self.label_state_value = tk.Label(self.state_frame, text="", fg="white", bg="black", font=("Times New Roman", 10, ""))
        self.label_short = tk.Label(self.state_frame, text="", fg="white", bg="black", font=("Times New Roman", 10, ""))
        
        # Fissure
        self.fissure_frame = tk.Frame(self.root, bg="black")
        self.label_fissure_state = tk.Label(self.fissure_frame, text="", fg="white", bg="black", font=("Times New Roman", 10, ""))
        self.label_fissure_eta = tk.Label(self.fissure_frame, text="", fg="white", bg="black", font=("Times New Roman", 10, "")) 

        # Grid configuration
        # Tiles
        self.label_cascade.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Faction State
        self.state_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=0, sticky="w")
        self.label_state_prefix.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        self.label_state_value.grid(row=0, column=1, padx=0, pady=0, sticky="w")
        self.label_short.grid(row=0, column=2, padx=2, pady=0, sticky="w")
         
        # Fissure
        self.fissure_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=0, sticky="w")
        self.label_fissure_state.grid(row=0, column=0, padx=(10, 0), pady=0, sticky="w")
        self.label_fissure_eta.grid(row=0, column=1, padx=(0, 5), pady=0, sticky="w")         

        # Configure grid to expand with content
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        
        self.fissure_frame.grid_forget() # Immediately hide the fissure frame since it will show if there's any fissures active
        
        self.root.update_idletasks() # Making sure overlay is fully initialized
        self.make_clickthrough()

    def make_clickthrough(self):
        # Obtain the window handle
        hwnd = win32gui.GetParent(self.root.winfo_id())
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        
        # http://msdn.microsoft.com/en-us/library/windows/desktop/ff700543(v=vs.85).aspx
        # The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
        exStyle = style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle)
        
        # Apply the new window style
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE | win32con.SWP_NOACTIVATE | win32con.SWP_NOREDRAW)
    
    def update_cascade_label(self, text, text_color):
        self.label_cascade.config(text=text, fg=text_color)
        self.root.update_idletasks()
    
    def update_fissure_data(self):
        fissure_data = get_fissure_state()
        show_fissure_frame = False
        
        for sol_node in fissure_data:
            node = sol_node["node"]
            expired = sol_node["expired"]
            eta = sol_node["eta"]
            is_steel_path = sol_node["isHard"]
            # mission_type = fissure_data["missionType"] # Maybe some day this will be useful? :Prayge: DE

            if ("Tuvul Commons" in node) and (is_steel_path == True) and (expired != True):
                self.label_fissure_state.config(text="Omnia Fissure", fg="gold")
                self.label_fissure_eta.config(text=f"expires in {eta}")
                show_fissure_frame = True

        if show_fissure_frame:
            self.fissure_frame.grid()
        else:
            self.fissure_frame.grid_forget()
        
    def update_zariman_cycle(self):
        zariman_cycle = get_zariman_cycle()
        time_left = zariman_cycle["timeLeft"]
        state = zariman_cycle["state"]
        short_string = zariman_cycle["shortString"]
        state_color = "cyan" if state == "corpus" else "red"
        
        # API endpoint can sometimes take up to 5m to update Zariman faction state for some reason :P
        if '-' in time_left:
            if 'm' in time_left:
                minutes = int(time_left.split('m')[0])
            else:
                minutes = 0  # No minutes part, just handle as 0
            remaining_minutes = 30 + minutes
            short_string = f"2h {remaining_minutes}m to " + ("corpus" if state == "grineer" else "grineer")
            state = "corpus" if state == "grineer" else "grineer"
            self.label_state_value.config(text=state.capitalize(), fg=state_color)
            self.label_short.config(text=short_string)    
        
        self.label_state_value.config(text=state.capitalize(), fg=state_color)
        self.label_short.config(text=short_string)

    def run(self):
        threading.Thread(target=self.track_tiles).start()
        threading.Thread(target=self.periodic_update).start()
        
        self.update_cascade_label("Awaiting Cascade...", "red")
        self.root.mainloop()

    def periodic_update(self):
        while True:
            self.update_fissure_data()
            self.update_zariman_cycle()
            time.sleep(30) # API endpoint seems to update about once every 2m

    def track_tiles(self):
        global loadedMessage, tilesets
        with open(LOG_FILE_PATH, encoding="utf8", errors="ignore") as logfile:
            loglines = follow(logfile)
            searching = False
            tiles = ""
            exocount = 0
            tilecount = 0
            buffer = ""
            attempts = 0
            
            for line in loglines:
                now = datetime.now()
                milliseconds = now.microsecond // 1000
                timestamp = now.strftime(f'%H:%M:%S.{milliseconds:03d}')
                
                if not line:
                    continue
                
                buffer += line
                
                # Check if the buffer contains a new line character, which should be the end of a line
                if "\n" in buffer:
                    lines = buffer.split("\n")
                    buffer = lines.pop()
                    
                    for line in lines:
                        if loadedMessage:
                            if "Play()" in line and "Layer255" in line and not "LotusCinematic" in line:
                                self.update_cascade_label(tiles, TILE_COLORS[max(0, (exocount - 10))])
                                tiles = ""
                                exocount = 0

                        if "/Lotus/Levels/Proc/Zariman/ZarimanDirectionalSurvival generating layout" in line:
                            searching = True
                            attempts += 1
                            print(f"[Attempt {attempts}]")
                            
                        if not searching and ("/Lotus/Levels/Proc/TheNewWar/PartTwo/TNWDrifterCampMain" in line or "/Lotus/Levels/Proc/PlayerShip" in line):
                            self.update_cascade_label("Awaiting Cascade...", "red")
                            
                        if "TacticalAreaMap::AddZone /Lotus/Levels/Zariman/" in line:
                            for key in sorted(tilesets.keys(), key=len, reverse=True):
                                if key in line:
                                    tilecount += 1
                                    
                                    if tilecount < 3:
                                        tiles = tiles + tilesets.get(key) + f" {ARROW_CHARACTER} "
                                    if tilecount == 3:
                                        tiles = tiles + tilesets.get(key)
                                        
                                    exocount += int(tilesets.get(key).split("(")[1][0])
                                    
                                    print(f"[{timestamp}] - Key: {key!r} | Tile: {tilesets[key]!r} | Tile #{tilecount!r} \n{line!r}")
                                    
                                    del tilesets[key]  # Remove the found tile
                                    break     
                        elif searching and "ResourceLoader" in line:
                            self.update_cascade_label(tiles, TILE_COLORS[max(0, (exocount - 10))])
                                
                            searching = False
                            tilecount = 0
                            
                            if not loadedMessage:
                                tiles = ""
                                exocount = 0
                            tilesets = original_tilesets.copy() # Reset the tilesets after 3 tiles found
                    
if __name__ == '__main__':
    overlay = Overlay()
    overlay.run()

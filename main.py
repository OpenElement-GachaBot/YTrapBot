import json
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from pynput.keyboard import Key, Listener
import ytrap
import threading
import ark
from tkinter import ttk
from ttkthemes import ThemedTk


with open('settings.json') as json_file:
    data = json.load(json_file)

r = ThemedTk(theme="equilux")

r.title('Gacha Bot')
r.iconphoto(True, tk.PhotoImage(file='icon.png'))
ytrap.setStatusText("Ready. Press F1 to start.")

writeJson = False
fillingUI = False


def updateStatus():
    global writeJson
    statusLabel['text'] = ytrap.getStatus()
    if(writeJson):
        file = open("settings.json", "w")
        file.write(json.dumps(data, indent=4, sort_keys=True))
        file.close()
        writeJson = False

    r.after(200, updateStatus)

def onKeyPress(key):
    if(key == Key.f1):
        x = threading.Thread(target=ytrap.start, args=([getThisLocation()]), daemon=True)
        x.start()
    if(key == Key.f2):
        ytrap.stop()
        ytrap.setStatusText("Ready. Press F1 to start.")
    if(key == Key.f3):
        ark.pause(not ark.getPaused())
        if(ark.getPaused()):
            ytrap.setStatusText("Paused")
        else:
            ytrap.setStatusText("Resumed")


def onKeyRelease(key):
    pass
    
listener = Listener(on_press=onKeyPress, on_release=onKeyRelease)
listener.start()

def getThisLocation():
    for i in data["locations"]:
        if(i["name"] == locationVariable.get()):
            return i


def saveJson():
   global writeJson
   writeJson = True

def fillUI():
    global fillingUI
    location = locationVariable.get()
    try:
        for i in data["locations"]:
            if(i["name"] == location):
                fillingUI = True
                if(i["aberrationMode"] == True):
                    mapVariable.set("Aberration")
                elif(i["dropGen2Suits"] == True):
                    mapVariable.set("Gen2")
                else:
                    mapVariable.set("Other")
    
                if(i["turnDirection"] == "left"):
                    cropVariable.set("Left")
                elif(i["turnDirection"] == "right"):
                    cropVariable.set("Right")
                else:
                    cropVariable.set("360")
    
                if(i["pickupMethod"] == "fspam"):
                    pickupMethodSv.set("F Spam")
                elif(i["pickupMethod"] == "whip"):
                    pickupMethodSv.set("Whip")
    
                if(i["numDedis"] == 2):
                    numDediSv.set("2")
                elif(i["numDedis"] == 4):
                    numDediSv.set("4")

                defaultXEntry.delete(0, tk.END)
                defaultXEntry.insert(0, str(i["bedX"]))
    
                defaultYEntry.delete(0, tk.END)
                defaultYEntry.insert(0, str(i["bedY"]))
    
                crystalBedsEntry.delete(0, tk.END)
                crystalBedsEntry.insert(0, str(i["crystalBeds"]))
    
                seedBedsEntry.delete(0, tk.END)
                seedBedsEntry.insert(0, str(i["seedBeds"]))
    
                pickupIntervalEntry.delete(0, tk.END)
                pickupIntervalEntry.insert(0, str(i["crystalInterval"]))
                
                suicideFrequencyEntry.delete(0, tk.END)
                suicideFrequencyEntry.insert(0, str(i["suicideFrequency"]))
    
                suicideBedEntry.delete(0, tk.END)
                suicideBedEntry.insert(0, str(i["suicideBed"]))
    
                gachaItems = ", ".join(i["keepItems"])
                gachaItemsEntry.delete(0, tk.END)
                gachaItemsEntry.insert(0, gachaItems)

                gachaItems = ", ".join(i["dropItems"])
                gachaDropItemsEntry.delete(0, tk.END)
                gachaDropItemsEntry.insert(0, gachaItems)
    
                crystalPrefixEntry.delete(0, tk.END)
                crystalPrefixEntry.insert(0, i["crystalBedPrefix"])
    
                seedPrefixEntry.delete(0, tk.END)
                seedPrefixEntry.insert(0, i["seedBedPrefix"])
                
                sideVaultVar.set(i["sideVaults"])

                showLogVar.set(i["openTribeLog"])
                
                showLogIntervalEntry.delete(0, tk.END)
                showLogIntervalEntry.insert(0, str(i["showLogInterval"]))
                
                singlePlayerVar.set(i["singlePlayer"])
            
                fillingUI = False
    except KeyError as err:
        tk.messagebox.showinfo("Settings file error", "The field " + str(err) + " is missing")


def locationChanged(*args):
    fillUI()

def reloadLocations():
    # Reset var and delete all old options
    locationVariable.set('')
    locationMenu['menu'].delete(0, 'end')

    # Insert list of new options (tk._setit hooks them up to var)
    for location in data["locations"]:
        locationMenu['menu'].add_command(label=location["name"], command=tk._setit(locationVariable, location["name"]))
    if(len(data["locations"]) > 0):
        locationVariable.set(data["locations"][0]["name"])
        

def addLocation():
    answer = tk.simpledialog.askstring("Input", "What do you want to call this gacha location?",
            parent=r)
    if answer is not None and answer != "":
        data["locations"].append({ 
            "name": answer,
            "bedX": 0,
            "bedY": 0,
            "crystalBeds": 1,
            "seedBeds": 12,
            "showLogInterval": 300,
            "crystalInterval": 600,
            "pickupMethod": "fspam",
            "dropGen2Suits": False,
            "aberrationMode": False,
            "keepItems": ["fab", "riot", "pump", "ass"],
            "dropItems": ["prim", "rams"],
            "suicideBed": "suicide bed",
            "suicideFrequency": 3,
            "turnDirection": "right",
            "seedBedPrefix": "seed",
            "crystalBedPrefix": "crystal",
            "openTribeLog": False,
            "numDedis": 2,
            "singlePlayer": False,
            "sideVaults": False
        })
        reloadLocations()
    else:
        tk.messagebox.showinfo( "No location name", "You must enter a name for your gacha tower.")

def deleteLocation():
    if(len(data["locations"]) > 0):
        count = 0
        for i in data["locations"]:
            if(i["name"] == locationVariable.get()):
                del data["locations"][count]
                break
            count += 1
        reloadLocations()
    else:
        tk.messagebox.showinfo("No locations", "There are no locations to delete.")


def onMapChange(*args):
    loc = getThisLocation()
    if(mapVariable.get() == "Aberration"):
        loc["aberrationMode"] = True
        loc["dropGen2Suits"] = False
    if(mapVariable.get() == "Gen2"):
        loc["aberrationMode"] = False
        loc["dropGen2Suits"] = True
    if(mapVariable.get() == "Other"):
        loc["aberrationMode"] = False
        loc["dropGen2Suits"] = False
    saveJson()

def onCropDirectionChange(*args):
    loc = getThisLocation()
    if(cropVariable.get() == "Left"):
        loc["turnDirection"] = "left"
    elif(cropVariable.get() == "Right"):
        loc["turnDirection"] = "right"
    else:
        loc["turnDirection"] = "360"
    saveJson()    

def onPickupMethodChange(*args):
    loc = getThisLocation()
    if(pickupMethodSv.get() == "F Spam"):
        loc["pickupMethod"] = "fspam"
    if(pickupMethodSv.get() == "Whip"):
        loc["pickupMethod"] = "whip"
    saveJson()    

def onNumDediChange(*args):
    loc = getThisLocation()
    if(numDediSv.get() == "2"):
        loc["numDedis"] = 2
    if(numDediSv.get() == "4"):
        loc["numDedis"] = 4
    saveJson()    

def onEntryChanged(*args):
    if(fillingUI == False):
        loc = getThisLocation()
        loc["bedX"] = int(defaultXEntry.get())
        loc["bedY"] = int(defaultYEntry.get())
        loc["crystalBeds"] = int(crystalBedsEntry.get())
        loc["seedBeds"] = int(seedBedsEntry.get())
        loc["crystalInterval"] = int(pickupIntervalEntry.get())
        gachaItems = gachaItemsEntry.get()
        if(gachaItems == ""):
            loc["keepItems"] = []
        elif(gachaItems == "*"):
            loc["keepItems"] = [""]
        else:    
            loc["keepItems"] = gachaItemsEntry.get().split(", ") 

        gachaDropItems = gachaDropItemsEntry.get()
        if(gachaDropItems == ""):
            loc["dropItems"] = []
        elif(gachaDropItems == "*"):
            loc["dropItems"] = [""]
        else:    
            loc["dropItems"] = gachaDropItemsEntry.get().split(", ")

        loc["suicideBed"] = suicideBedEntry.get()
        loc["suicideFrequency"] = int(suicideFrequencyEntry.get())
        loc["seedBedPrefix"]= seedPrefixEntry.get()
        loc["crystalBedPrefix"] = crystalPrefixEntry.get()

        if(sideVaultVar.get() == 0):
            loc["sideVaults"] = False
        else:
            loc["sideVaults"] = True

        if(showLogVar.get() == 0):
            loc["openTribeLog"] = False
        else:
            loc["openTribeLog"] = True

        loc["showLogInterval"] = int(showLogIntervalEntry.get())

        if(singlePlayerVar.get() == 0):
            loc["singlePlayer"] = False
        else:
            loc["singlePlayer"] = True
        saveJson()


frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
label = ttk.Label(frame, text="Plant Y Gacha Bot")
label.config(font=("Courier", 22))
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
locationVariable = tk.StringVar(frame)
locationVariable.set("Spider Cave") # default value

label = ttk.Label(frame, text="Location")
label.pack(side=tk.LEFT)
locationMenu = ttk.OptionMenu(frame, locationVariable, "")
locationMenu.pack(side=tk.LEFT)

reloadLocations()

button = ttk.Button(frame, text='Delete', command = deleteLocation)
button.pack(side=tk.RIGHT)
button = ttk.Button(frame, text="Add", command = addLocation)
button.pack(side=tk.RIGHT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
mapVariable = tk.StringVar(frame)
mapVariable.set("Other") # default value

label = ttk.Label(frame, text="Map")
label.pack(side=tk.LEFT)
mapMenu = ttk.OptionMenu(frame, mapVariable, "", "Other", "Aberration", "Gen2")
mapMenu.pack(side=tk.LEFT)

label = ttk.Label(frame, text="Single player")
label.pack(side=tk.LEFT, fill=tk.BOTH)

singlePlayerVar = tk.IntVar()
singlePlayerCheck = ttk.Checkbutton(frame, variable=singlePlayerVar)
singlePlayerCheck.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)


frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Bed pixel coords")
label.pack(side=tk.LEFT)

label = ttk.Label(frame, text="X")
label.pack(side=tk.LEFT)

defaultXSv = tk.StringVar()
defaultXEntry = ttk.Entry(frame, textvariable=defaultXSv)
defaultXEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="Y")
label.pack(side=tk.LEFT)

defaultYSv = tk.StringVar()
defaultYEntry = ttk.Entry(frame, textvariable=defaultYSv)
defaultYEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Crystal bed prefix")
label.pack(side=tk.LEFT)

crystalPrefixSv = tk.StringVar()
crystalPrefixEntry = ttk.Entry(frame, textvariable=crystalPrefixSv)
crystalPrefixEntry.pack(side=tk.LEFT)


label = ttk.Label(frame, text="# of beds")
label.pack(side=tk.LEFT)

crystalBedsSv = tk.StringVar()
crystalBedsEntry = ttk.Entry(frame, textvariable=crystalBedsSv)
crystalBedsEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Seed bed prefix")
label.pack(side=tk.LEFT)

seedPrefixSv = tk.StringVar()
seedPrefixEntry = ttk.Entry(frame, textvariable=seedPrefixSv)
seedPrefixEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="# of beds")
label.pack(side=tk.LEFT)

seedBedsSv = tk.StringVar()
seedBedsEntry = ttk.Entry(frame, textvariable=seedBedsSv)
seedBedsEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Crystal pickup interval")
label.pack(side=tk.LEFT)

pickupIntervalSv = tk.StringVar()
pickupIntervalEntry = ttk.Entry(frame, textvariable=pickupIntervalSv)
pickupIntervalEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Crystal pick up method")
label.pack(side=tk.LEFT)

pickupMethodSv= tk.StringVar(frame)
pickupMethodSv.set("F spam") # default value

pickupMethodMenu = ttk.OptionMenu(frame, pickupMethodSv, "", "F Spam", "Whip")
pickupMethodMenu.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Vaults on the side")
label.pack(side=tk.LEFT)

sideVaultVar = tk.IntVar()
sideVaultCheck = ttk.Checkbutton(frame, variable=sideVaultVar)
sideVaultCheck.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)


frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Number of dedis")
label.pack(side=tk.LEFT)

numDediSv = tk.StringVar(frame)
numDediSv.set("2") # default value

numDediMenu = ttk.OptionMenu(frame, numDediSv, "", "2", "4")
numDediMenu.pack(side=tk.LEFT)


frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Suicide frequency")
label.pack(side=tk.LEFT)

suicideFrequencySv = tk.StringVar()
suicideFrequencyEntry = ttk.Entry(frame, textvariable=suicideFrequencySv)
suicideFrequencyEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Suicide bed name")
label.pack(side=tk.LEFT)

suicideBedSv = tk.StringVar()
suicideBedEntry = ttk.Entry(frame, textvariable=suicideBedSv)
suicideBedEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Gacha items to drop (separate by comma)")
label.pack(side=tk.LEFT)

gachaDropItemsSv = tk.StringVar()
gachaDropItemsEntry = ttk.Entry(frame, textvariable=gachaDropItemsSv)
gachaDropItemsEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Gacha items to keep (separate by comma)")
label.pack(side=tk.LEFT)

gachaItemsSv = tk.StringVar()
gachaItemsEntry = ttk.Entry(frame, textvariable=gachaItemsSv)
gachaItemsEntry.pack(side=tk.LEFT)


frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
cropVariable = tk.StringVar(frame)
cropVariable.set("Left") # default value

label = ttk.Label(frame, text="Crop harvest turn direction")
label.pack(side=tk.LEFT)
cropMenu = ttk.OptionMenu(frame, cropVariable, "", "Left", "Right", "360")
cropMenu.pack(side=tk.LEFT)


frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
label = ttk.Label(frame, text="Open tribe log after spawning")
label.pack(side=tk.LEFT, fill=tk.BOTH)

showLogVar = tk.IntVar()
showLogCheck = ttk.Checkbutton(frame, variable=showLogVar)
showLogCheck.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Tribe log open interval")
label.pack(side=tk.LEFT)

showLogIntervalSv = tk.StringVar()
showLogIntervalEntry = ttk.Entry(frame, textvariable=showLogIntervalSv)
showLogIntervalEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
statusLabel = ttk.Label(frame, text="Press F1 to start the bot")
statusLabel.pack(side=tk.LEFT, fill=tk.BOTH)

fillUI()

locationVariable.trace("w", locationChanged)
mapVariable.trace("w", onMapChange)
cropVariable.trace("w", onCropDirectionChange)
pickupMethodSv.trace("w", onPickupMethodChange)
numDediSv.trace("w", onNumDediChange)

defaultXSv.trace_add("write", onEntryChanged)
defaultYSv.trace_add("write", onEntryChanged)
crystalBedsSv.trace_add("write", onEntryChanged)
seedBedsSv.trace_add("write", onEntryChanged)
pickupIntervalSv.trace_add("write", onEntryChanged)
suicideFrequencySv.trace_add("write", onEntryChanged)
suicideBedSv.trace_add("write", onEntryChanged)
gachaItemsSv.trace_add("write", onEntryChanged)
gachaDropItemsSv.trace_add("write", onEntryChanged)
crystalPrefixSv.trace_add("write", onEntryChanged)
seedPrefixSv.trace_add("write", onEntryChanged)
sideVaultVar.trace_add("write", onEntryChanged)
showLogVar.trace_add("write", onEntryChanged)
showLogIntervalSv.trace_add("write", onEntryChanged)
singlePlayerVar.trace_add("write", onEntryChanged)

updateStatus()
r.mainloop()

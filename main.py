import json
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from pynput.keyboard import Key, Listener
import ytrap
import arkMonitoring
import threading
import ark
from tkinter import ttk
from ttkthemes import ThemedTk

version = "v1.0.01b"

with open('settings.json') as json_file:
    data = json.load(json_file)

r = ThemedTk(theme="radiance")

r.title('Gacha Log Bot ' + version)
r.iconphoto(True, tk.PhotoImage(file='media/icon.png'))
#r.geometry('500x650')
r.resizable(0,0)
ytrap.setStatusText("Ready. Press F1 to start.")

writeJson = False
fillingUI = False

# botStatus used to track what the bot is doing:
# 0 = off
# 1 = on
# 2 = paused
botStatus = 0


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
    global botStatus

    if(key == Key.f1):
        if(botStatus == 0):
            monitoring = threading.Thread(target=arkMonitoring.start, args=([getThisLocation()]), daemon=True)
            monitoring.start()
            
            x = threading.Thread(target=ytrap.start, args=([getThisLocation()]), daemon=True)
            x.start()
            
            botStatus = 1
    if(key == Key.f2):
        if(botStatus == 1):
            ytrap.stop()
            ytrap.setStatusText("Ready. Press F1 to start.")
            
            botStatus = 0
    if(key == Key.f3):
        if(botStatus == 1):
            ark.pause(not ark.getPaused())
            if(ark.getPaused()):
                arkMonitoring.pause(True)
                ytrap.setStatusText("Paused")
            else:
                arkMonitoring.pause(False)
                ytrap.setStatusText("Resumed")
    if(key == Key.f4):
        if(botStatus == 1):
            ytrap.setStatusText("Unstucking bot...")
            ytrap.botUnstuck()
            x = threading.Thread(target=ytrap.start, args=([getThisLocation()]), daemon=True)
            x.start()


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

                if(i["loadGachaMethod"] == "ytrap"):
                    loadGachaMethodSv.set("YTrap")
                elif(i["loadGachaMethod"] == "none"):
                    loadGachaMethodSv.set("None")

                if(i["gameLauncher"] == "steam"):
                    gameLauncherSv.set("Steam")
                elif(i["gameLauncher"] == "epic"):
                    gameLauncherSv.set("Epic Games")
                    
                if(i["suicideMethod"] == "suicide"):
                    suicideMethodSv.set("Suicide")
                elif(i["suicideMethod"] == "tekpod"):
                    suicideMethodSv.set("Tek Pod")

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
                
                accountNameEntry.delete(0, tk.END)
                accountNameEntry.insert(0, str(i["accountName"]))
                
                serverNameEntry.delete(0, tk.END)
                serverNameEntry.insert(0, str(i["serverName"]))
                
                serverSearchEntry.delete(0, tk.END)
                serverSearchEntry.insert(0, str(i["serverSearch"]))
                
                webhookGachaEntry.delete(0, tk.END)
                webhookGachaEntry.insert(0, str(i["webhookGacha"]))
                
                webhookTribeLogEntry.delete(0, tk.END)
                webhookTribeLogEntry.insert(0, str(i["webhookTribeLog"]))
                
                webhookAlertEntry.delete(0, tk.END)
                webhookAlertEntry.insert(0, str(i["webhookAlert"]))
                
                tagLevel0Entry.delete(0, tk.END)
                tagLevel0Entry.insert(0, str(i["tagLevel0"]))
                
                tagLevel1Entry.delete(0, tk.END)
                tagLevel1Entry.insert(0, str(i["tagLevel1"]))
                
                tagLevel2Entry.delete(0, tk.END)
                tagLevel2Entry.insert(0, str(i["tagLevel2"]))
                
                tagLevel3Entry.delete(0, tk.END)
                tagLevel3Entry.insert(0, str(i["tagLevel3"]))
                
                tagLevel4Entry.delete(0, tk.END)
                tagLevel4Entry.insert(0, str(i["tagLevel4"]))
                
                tagLevel5Entry.delete(0, tk.END)
                tagLevel5Entry.insert(0, str(i["tagLevel5"]))
                
                towertokenEntry.delete(0, tk.END)
                towertokenEntry.insert(0, str(i["towertoken"]))
                
                tesseractpathEntry.delete(0, tk.END)
                tesseractpathEntry.insert(0, str(i["tesseractpath"]))
                
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
            "loadGachaMethod": "ytrap",
            "suicideMethod": "suicide",
            "name": answer,
            "bedX": 795,
            "bedY": 537,
            "crystalBeds": 1,
            "seedBeds": 24,
            "showLogInterval": 300,
            "crystalInterval": 600,
            "pickupMethod": "fspam",
            "dropGen2Suits": False,
            "aberrationMode": False,
            "keepItems": ["fab", "riot", "pump", "ass"],
            "dropItems": ["prim", "rams"],
            "suicideBed": "suicide bed",
            "suicideFrequency": 1,
            "turnDirection": "right",
            "seedBedPrefix": "seed",
            "crystalBedPrefix": "crystal",
            "openTribeLog": True,
            "numDedis": 2,
            "singlePlayer": False,
            "sideVaults": False,
            "gameLauncher": "steam",
            "accountName": "Gacha Bot",
            "serverName": "",
            "serverSearch": "",
            "webhookGacha": "",
            "webhookTribeLog": "",
            "webhookAlert": "",
            "tagLevel0": "",
            "tagLevel1": "",
            "tagLevel2": "",
            "tagLevel3": "@here",
            "tagLevel4": "@everyone",
            "tagLevel5": "",
            "towertoken": "",
            "tesseractpath": ""
        })
        reloadLocations()
        locationVariable.set(answer) # change to the newly created location
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

def onLoadGachaMethodChange(*args):
    loc = getThisLocation()
    if(loadGachaMethodSv.get() == "YTrap"):
        loc["loadGachaMethod"] = "ytrap"
    if(loadGachaMethodSv.get() == "None"):
        loc["loadGachaMethod"] = "none"
    saveJson()

def onGameLauncherChange(*args):
    loc = getThisLocation()
    if(gameLauncherSv.get() == "Steam"):
        loc["gameLauncher"] = "steam"
    if(gameLauncherSv.get() == "Epic Games"):
        loc["gameLauncher"] = "epic"
    saveJson()

def onSuicideMethodChange(*args):
    loc = getThisLocation()
    if(suicideMethodSv.get() == "Suicide"):
        loc["suicideMethod"] = "suicide"
    if(suicideMethodSv.get() == "Tek Pod"):
        loc["suicideMethod"] = "tekpod"
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
        loc["accountName"] = accountNameEntry.get()
        loc["serverName"] = serverNameEntry.get()
        loc["serverSearch"] = serverSearchEntry.get()
        loc["webhookGacha"] = webhookGachaEntry.get()
        loc["webhookTribeLog"] = webhookTribeLogEntry.get()
        loc["webhookAlert"] = webhookAlertEntry.get()
        loc["tagLevel0"] = tagLevel0Entry.get()
        loc["tagLevel1"] = tagLevel1Entry.get()
        loc["tagLevel2"] = tagLevel2Entry.get()
        loc["tagLevel3"] = tagLevel3Entry.get()
        loc["tagLevel4"] = tagLevel4Entry.get()
        loc["tagLevel5"] = tagLevel5Entry.get()
        loc["towertoken"] = towertokenEntry.get()
        loc["tesseractpath"] = tesseractpathEntry.get()

        if(singlePlayerVar.get() == 0):
            loc["singlePlayer"] = False
        else:
            loc["singlePlayer"] = True
        saveJson()

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
label = ttk.Label(frame, text="Gacha Log Bot " + version)
label.config(font=("Verdana", 22, 'bold'))
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
label = ttk.Label(frame, text="Make heaps of element while you sleep! ")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
locationVariable = tk.StringVar(frame)
locationVariable.set("My Gacha Tower") # default value

label = ttk.Label(frame, text="Location")
label.pack(side=tk.LEFT)
locationMenu = ttk.OptionMenu(frame, locationVariable, "")
locationMenu.pack(side=tk.LEFT)

reloadLocations()

button = ttk.Button(frame, text='Delete', command = deleteLocation)
button.pack(side=tk.RIGHT)
button = ttk.Button(frame, text="Add", command = addLocation)
button.pack(side=tk.RIGHT)

label = ttk.Label(frame, text="")
label.pack(side=tk.LEFT)
frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
label = ttk.Label(frame, text="Gacha Tower Settings")
label.config(font=("Verdana", 14, 'bold'))
label.pack(side=tk.LEFT)

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
defaultXEntry = ttk.Entry(frame, textvariable=defaultXSv, width=5)
defaultXEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="Y")
label.pack(side=tk.LEFT)

defaultYSv = tk.StringVar()
defaultYEntry = ttk.Entry(frame, textvariable=defaultYSv, width=5)
defaultYEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
label = ttk.Label(frame, text="Gacha Stations:")
label.config(font=("Verdana", 12, 'bold'))
label.pack(side=tk.LEFT)
frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Gacha load method")
label.pack(side=tk.LEFT)

loadGachaMethodSv= tk.StringVar(frame)
loadGachaMethodSv.set("YTrap") # default value

loadGachaMethodMenu = ttk.OptionMenu(frame, loadGachaMethodSv, "", "YTrap", "None")
loadGachaMethodMenu.pack(side=tk.LEFT)

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
seedBedsEntry = ttk.Entry(frame, textvariable=seedBedsSv, width=4)
seedBedsEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
cropVariable = tk.StringVar(frame)
cropVariable.set("Left") # default value

label = ttk.Label(frame, text="Crop harvest turn direction")
label.pack(side=tk.LEFT)
cropMenu = ttk.OptionMenu(frame, cropVariable, "", "Left", "Right", "360")
cropMenu.pack(side=tk.LEFT)

label = ttk.Label(frame, text="")
label.pack(side=tk.LEFT)
frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
label = ttk.Label(frame, text="Crystal Collection:")
label.config(font=("Verdana", 12, 'bold'))
label.pack(side=tk.LEFT)
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
crystalBedsEntry = ttk.Entry(frame, textvariable=crystalBedsSv, width=4)
crystalBedsEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Crystal pickup interval")
label.pack(side=tk.LEFT)

pickupIntervalSv = tk.StringVar()
pickupIntervalEntry = ttk.Entry(frame, textvariable=pickupIntervalSv, width=5)
pickupIntervalEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(seconds)")
label.pack(side=tk.LEFT)

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

label = ttk.Label(frame, text="Number of dedis")
label.pack(side=tk.LEFT)

numDediSv = tk.StringVar(frame)
numDediSv.set("2") # default value

numDediMenu = ttk.OptionMenu(frame, numDediSv, "", "2", "4")
numDediMenu.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Poly Vault Position")
label.pack(side=tk.LEFT)

sideVaultVar = tk.IntVar()
sideVaultCheck = ttk.Checkbutton(frame, variable=sideVaultVar)
sideVaultCheck.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)


frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Gacha items to drop")
label.pack(side=tk.LEFT)

gachaDropItemsSv = tk.StringVar()
gachaDropItemsEntry = ttk.Entry(frame, textvariable=gachaDropItemsSv)
gachaDropItemsEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(separate by comma)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Gacha items to keep")
label.pack(side=tk.LEFT)

gachaItemsSv = tk.StringVar()
gachaItemsEntry = ttk.Entry(frame, textvariable=gachaItemsSv)
gachaItemsEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(separate by comma)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)
label = ttk.Label(frame, text="Suicide:")
label.config(font=("Verdana", 12, 'bold'))
label.pack(side=tk.LEFT)
frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Suicide method")
label.pack(side=tk.LEFT)

suicideMethodSv= tk.StringVar(frame)
suicideMethodSv.set("Suicide") # default value

suicideMethodMenu = ttk.OptionMenu(frame, suicideMethodSv, "", "Suicide", "Tek Pod")
suicideMethodMenu.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Suicide bed name")
label.pack(side=tk.LEFT)

suicideBedSv = tk.StringVar()
suicideBedEntry = ttk.Entry(frame, textvariable=suicideBedSv)
suicideBedEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Suicide frequency")
label.pack(side=tk.LEFT)

suicideFrequencySv = tk.StringVar()
suicideFrequencyEntry = ttk.Entry(frame, textvariable=suicideFrequencySv, width=3)
suicideFrequencyEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(# of collections until suicide)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Monitoring Settings")
label.config(font=("Verdana", 14, 'bold'))
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Game Launcher")
label.pack(side=tk.LEFT)
gameLauncherSv= tk.StringVar(frame)
gameLauncherSv.set("Steam") # default value
gameLauncherMenu = ttk.OptionMenu(frame, gameLauncherSv, "", "Steam", "Epic Games")
gameLauncherMenu.pack(side=tk.LEFT)
frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

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
showLogIntervalEntry = ttk.Entry(frame, textvariable=showLogIntervalSv, width=4)
showLogIntervalEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(seconds)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Account name")
label.pack(side=tk.LEFT)

accountNameSv = tk.StringVar()
accountNameEntry = ttk.Entry(frame, textvariable=accountNameSv)
accountNameEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(name of Game Account)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)



label = ttk.Label(frame, text="Server name")
label.pack(side=tk.LEFT)

serverNameSv = tk.StringVar()
serverNameEntry = ttk.Entry(frame, textvariable=serverNameSv)
serverNameEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Server search")
label.pack(side=tk.LEFT)

serverSearchSv = tk.StringVar()
serverSearchEntry = ttk.Entry(frame, textvariable=serverSearchSv)
serverSearchEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(used to reconnect)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Gacha Webhook")
label.pack(side=tk.LEFT)

webhookGachaSv = tk.StringVar()
webhookGachaEntry = ttk.Entry(frame, textvariable=webhookGachaSv)
webhookGachaEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Tribe Log Webhook")
label.pack(side=tk.LEFT)

webhookTribeLogSv = tk.StringVar()
webhookTribeLogEntry = ttk.Entry(frame, textvariable=webhookTribeLogSv)
webhookTribeLogEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Alert Webhook")
label.pack(side=tk.LEFT)

webhookAlertSv = tk.StringVar()
webhookAlertEntry = ttk.Entry(frame, textvariable=webhookAlertSv)
webhookAlertEntry.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Tag Level 0")
label.pack(side=tk.LEFT)

tagLevel0Sv = tk.StringVar()
tagLevel0Entry = ttk.Entry(frame, textvariable=tagLevel0Sv)
tagLevel0Entry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(info messages)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Tag Level 1")
label.pack(side=tk.LEFT)

tagLevel1Sv = tk.StringVar()
tagLevel1Entry = ttk.Entry(frame, textvariable=tagLevel1Sv)
tagLevel1Entry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(start/stop messages)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Tag Level 2")
label.pack(side=tk.LEFT)

tagLevel2Sv = tk.StringVar()
tagLevel2Entry = ttk.Entry(frame, textvariable=tagLevel2Sv)
tagLevel2Entry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(maintenance messages)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Tag Level 3")
label.pack(side=tk.LEFT)

tagLevel3Sv = tk.StringVar()
tagLevel3Entry = ttk.Entry(frame, textvariable=tagLevel3Sv)
tagLevel3Entry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(tek sensor pings)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Tag Level 4")
label.pack(side=tk.LEFT)

tagLevel4Sv = tk.StringVar()
tagLevel4Entry = ttk.Entry(frame, textvariable=tagLevel4Sv)
tagLevel4Entry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(destroyed pings)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Tag Level 5")
label.pack(side=tk.LEFT)

tagLevel5Sv = tk.StringVar()
tagLevel5Entry = ttk.Entry(frame, textvariable=tagLevel5Sv)
tagLevel5Entry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(critical errors)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Stonks Tower Token")
label.pack(side=tk.LEFT)

towertokenSv = tk.StringVar()
towertokenEntry = ttk.Entry(frame, textvariable=towertokenSv)
towertokenEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(leave blank for now)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="Tesseract Path")
label.pack(side=tk.LEFT)

tesseractpathSv = tk.StringVar()
tesseractpathEntry = ttk.Entry(frame, textvariable=tesseractpathSv)
tesseractpathEntry.pack(side=tk.LEFT)

label = ttk.Label(frame, text="(leave blank for now)")
label.pack(side=tk.LEFT)

frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)


label = ttk.Label(frame, text="")
label.pack(side=tk.LEFT)
frame = ttk.Frame(r)
frame.pack(fill=tk.BOTH, expand=True)

statusLabel = ttk.Label(frame, text="Press F1 to start the bot")
statusLabel.config(font=('Verdana', 12, 'bold'))
statusLabel.pack(side=tk.LEFT, fill=tk.BOTH)


fillUI()


locationVariable.trace("w", locationChanged)
mapVariable.trace("w", onMapChange)
loadGachaMethodSv.trace("w", onLoadGachaMethodChange)
suicideMethodSv.trace("w", onSuicideMethodChange)
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
accountNameSv.trace_add("write", onEntryChanged)
serverNameSv.trace_add("write", onEntryChanged)
serverSearchSv.trace_add("write", onEntryChanged)
webhookGachaSv.trace_add("write", onEntryChanged)
webhookTribeLogSv.trace_add("write", onEntryChanged)
webhookAlertSv.trace_add("write", onEntryChanged)
tagLevel0Sv.trace_add("write", onEntryChanged)
tagLevel1Sv.trace_add("write", onEntryChanged)
tagLevel3Sv.trace_add("write", onEntryChanged)
tagLevel3Sv.trace_add("write", onEntryChanged)
tagLevel4Sv.trace_add("write", onEntryChanged)
tagLevel5Sv.trace_add("write", onEntryChanged)
towertokenSv.trace_add("write", onEntryChanged)
tesseractpathSv.trace_add("write", onEntryChanged)
singlePlayerVar.trace_add("write", onEntryChanged)

updateStatus()

r.mainloop()

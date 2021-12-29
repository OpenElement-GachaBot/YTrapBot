import json         # required to read the config file
import time         # required to sleep between monitoring checks
import cv2          # required to compare images
import numpy as np  # required for image manipulation
import os           # required to check if a file exists
import pyautogui    # required to get screenshots
import requests     # required for posting to Discord via Webhooks
import webbrowser   # required to launch Ark via browser link
import pytesseract  # required to OCR the tribe log
import re           # required for regex searches

# All the settings for this location - passed from main.py
settings = {}

# Allows arkMonitoring to be used in a thread
terminated = False
paused = False

# Track time since last task started
timeLastTaskStarted = 0
timeLastTaskName = ""

# Track progression through the notification process
outageLevel0 = False
outageLevel1 = False
outageLevel2 = False
outageLevel3 = False

#passing this function True will cause most functions in this script to throw an exception
#useful to terminate a thread in a multithreaded environment
def terminate(t):
    global terminated
    terminated = t

#passing this function True will cause the bot to halt until it is passed False again
#note that terminate(True) will still kill the bot
def pause(p):
    global paused
    
    # Unpausing so reset variables
    if(p == False):
        trackTaskStarted("Resumed Ark Monitoring")
    
    paused = p

#returns the paused state
def getPaused():
    global paused
    return paused

#internal functino, don't use it
#throws an exception if terminated is True
def checkTerminated():
    global paused
    global terminated

    if(terminated):
        raise Exception("Monitoring thread terminated.")

    #if paused, halt but also die if terminated 
    while(paused):
        time.sleep(0.1)
        if(terminated):
            raise Exception("Monitoring thread terminated.")

# Screenshot the whole screen
def screenshotScreen():
    tribeLog = pyautogui.screenshot()
    tribeLog.save(r'screenshots\screen-latest.png')
    postScreenToDiscord()

# Post image to Discord
def postScreenToDiscord():
    global settings
    
    url = settings["webhookGacha"]
    
    if(url == ""):
        #print("Monitoring: Screenshot not posted to Discord as Webhook is blank.")
        return

    message = ""
    message = addDiscordTag(message)

    data = {
        "content": message,
        "avatar_url": "https://i.imgur.com/cMBnUQo.png"
    }
    
    files = {
        "file" : ("./screenshots/screen-latest.png", open("./screenshots/screen-latest.png", 'rb'))
    }

    result = requests.post(url, data = data, files=files)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postScreenToDiscord() had an error:")
        print(err)

# Screenshot the current tribe log
def screenshotTribeLog():
    tribeLog = pyautogui.screenshot(region=(1342, 183, 438, 815))
    tribeLog.save('screenshots/tribelog-latest.png')
    tribePlayers = pyautogui.screenshot(region=(889, 197, 346, 30))
    tribePlayers = tribePlayers.resize((438,38))
    tribeLog.paste(tribePlayers, (0,777))
    tribeLog.save('screenshots/tribelogplayers-latest.png')
    checkTribeLogEvents()

def checkTribeLogEvents():
    global settings
    
    tesseractpath = settings["tesseractpath"]
    
    # If tesseractpath is undefined use the Image Template matching
    if(tesseractpath == ""):
        checkTribeLogEventsImageTemplate()
        return

    # default to nothing detected
    alert_triggered = False
    alert_destroyed = False
    alert_found = False
    tribelogdaynew = ""

    pytesseract.pytesseract.tesseract_cmd = tesseractpath

    # Read the tribe log as input
    tribeLog = cv2.imread("./screenshots/tribelog-latest.png")

    # Prepare the tribe log for OCR
    tribeLog = prepareTesseractImage(tribeLog)

    # Use Tesseract to get the tribe log as text
    tribeLog = pytesseract.image_to_string(tribeLog)

    # Do our best to make what tesseract gave us human readable
    tribeLog = parseTesseractText(tribeLog)

    # Try to get the file with daytime of last tribe log event or make it if it doesn't exist
    if(os.path.exists("screenshots/tribelog-latestday.txt")):
        # Get daytime of last tribe log event
        f = open("./screenshots/tribelog-latestday.txt", "r")
        lasttribelogday = f.read()
        f.close()
    else:
        f = open("./screenshots/tribelog-latestday.txt", "w")
        lasttribelogday = "xxx"
        f.write(lasttribelogday)
        f.close()

    tribeLog = tribeLog.splitlines()
    for tribelogline in tribeLog:
        # Get the tribe log day for the current line
        tribelogday = tribelogline[0:20]
        
        # Check if it matches the last time we detected an event
        if(lasttribelogday == tribelogday):
            # Stop checking the logs - we are up to where we were before
            break

        alerttext = ""
        # Check if an event has occurred
        if "destroyed" in tribelogline:
            if "auto-decay" not in tribelogline: # ignore auto-decay destroyed
                if "C4 Charge" not in tribelogline: # ignore C4 Charge was destroyed
                    alert_destroyed = True
                    alerttext += tribelogline + "\n"
                    # Update tribelogdaynew with the first alert found
                    if(alert_found == False):
                        tribelogdaynew = tribelogday
                        alert_found = True
        elif "triggered" in tribelogline:
            alert_triggered = True
            # Update tribelogdaynew with the first alert found
            if(alert_found == False):
                alerttext += tribelogline + "\n"
                tribelogdaynew = tribelogday
                alert_found = True

    # Write the latest tribelog day to a file if an alert found
    if(alert_found == True):
        f = open("./screenshots/tribelog-latestday.txt", "w")
        f.write(tribelogdaynew)
        f.close()

    # Post the alert to Discord
    if(alert_destroyed == True and alert_triggered == True):
        postAlertToDiscord("**Something Destroyed and Tek Sensor Triggered!**\n" + alerttext,4)
    elif(alert_destroyed == True and alert_triggered == False):
        postAlertToDiscord("**Something Destroyed!**\n" + alerttext,4)
    elif(alert_destroyed == False and alert_triggered == True):
        postAlertToDiscord("**Tek Sensor Triggered!**\n" + alerttext,3)
    
    # Also post tribe log to Discord as normal
    postTribeLogToDiscord()

def prepareTesseractImage(image, brightness = 150):
    # Make the image larger
    scale_percent = 5 # how much to enlarge the image
    image = cv2.resize(image, (int(image.shape[1] * scale_percent), int(image.shape[0] * scale_percent)), interpolation = cv2.INTER_LINEAR)

    # Convert green of tek sensors to white
    #background = np.where(image == (63, 127, 0))
    #image[background[0], background[1], :] = [255, 255, 255]
    # Note: While this kind of works it is NOT optimal and makes the OCR significantly worse

    # Make the image much darker to remove the background (will go mostly black)
    M = np.ones(image.shape, dtype="uint8") * brightness
    image = cv2.subtract(image, M)

    # Set anywhere that isn't background (i.e. the text) to solid white
    background = np.where(image != 0)
    image[background[0], background[1], :] = [255, 255, 255]

    # Convert anywhere with text to a solid white
    background = np.where(image != 0)
    image[background[0], background[1], :] = [255, 255, 255]

    # Invert the image (now white background with black text)
    image = 255 - image
    
    # Return the prepared version of the tribe log
    return image

def tesseractAddSpaces(result, message):
    result = result.replace(message, " " + message + " ")
    result = result.replace("  " + message, " " + message)
    result = result.replace(message + "  ", message + " ")
    result = result.replace(message + " !", message + "!")
    return result

def parseTesseractText(result):
    # Use replace to make results more human readable
    result = result.replace("\n", "")
    result = result.replace("Dav ", "Day ")
    result = result.replace("Day,", "Day")
    result = result.replace("Day", "\nDay")
    result = re.sub("Day (\d+).", r"Day \1,", result)
    result = result.replace("destroved", "destroyed")
    result = result.replace("bv", "by")
    result = tesseractAddSpaces(result, "triggered")
    result = result.replace("eneny", "enemy")
    result = result.replace("ememyv", "enemy")
    result = result.replace("anenemy", "an enemy")
    result = result.replace("enemy dio", "enemy dino")
    result = result.replace("enemy ding", "enemy dino")
    result = result.replace("byah", "by an")
    result = result.replace("byan", "by an")
    result = result.replace("Sutwiwor", "survivor")
    result = result.replace("‘", "'")
    result = result.replace("’", "'")
    result = result.replace("\"", "'")
    result = result.replace("{", "(")
    result = result.replace("}", ")")
    result = result.replace(")))", ")!")
    result = tesseractAddSpaces(result, "was")
    result = tesseractAddSpaces(result, "killed")
    result = tesseractAddSpaces(result, "Adolescent")
    result = tesseractAddSpaces(result, "-")
    result = result.replace("Starved", "starved")
    result = tesseractAddSpaces(result, "starved")
    result = result.replace("LvI", "Lvl")
    result = result.replace("Lvi", "Lvl")
    result = result.replace("Lvl", " Lvl ")
    result = result.replace("  Lvl", " Lvl")
    result = result.replace("Lvl  ", "Lvl ")
    result = result.replace("[Clonel", "[Clone]")
    result = tesseractAddSpaces(result, "[Clone]")
    result = result.replace("Charae", "Charge")
    result = result.replace("Charoe", "Charge")
    result = result.replace("Chasae", "Charge")
    result = result.replace("decav", "decay")
    result = result.replace("destroyedl", "destroyed!")
    result = result.replace("Steaosaurus", "Stegosaurus")
    result = result.replace("Steaqosaurus", "Stegosaurus")
    result = result.replace("Stedaosaurus", "Stegosaurus")
    result = result.replace("Astradelohis", "Astrodelphis")
    result = result.replace("Astrodelohis", "Astrodelphis")
    result = result.replace("Astrodelbhis", "Astrodelphis")
    result = result.replace("Giaanotosaurus", "Giganotosaurus")
    result = result.replace("iTek", "(Tek")
    result = result.replace("Ceilina", "Ceiling")
    result = tesseractAddSpaces(result, "Ceiling")
    result = result.replace("Trianale", "Triangle")
    result = tesseractAddSpaces(result, "Triangle")
    result = result.replace("Manaaarmr", "Managarmr")
    result = result.replace("  (", "(")
    result = result.replace(" (", "(")
    result = result.replace("(", " (")
    result = result.replace("'l", "'!")
    result = result.replace("“", "")
    result = result.replace("''", "'")
    result = result.replace("auto - decay", "auto-decay")
    result = result.replace("MetalDouble", "Metal Double")
    result = result.replace("TekDouble", "Tek Double")
    result = result[:result.rfind('\n')]
    result = result.replace("\n", "", 1)
    
    return result

def checkTribeLogEventsImageTemplate():
    tribeLog_entry_y = 9999
    threshold = 0.9
    alert_triggered = False
    alert_destroyed = False
    alert_triggered_y = 9999
    alert_destroyed_y = 9999

    tribeLog = cv2.imread('screenshots/tribelogplayers-latest.png', cv2.IMREAD_UNCHANGED)
    # Try to open the daytime png and make it if necessary
    if(os.path.exists('screenshots/tribelog-daytime.png')):
        tribeLog_daytime_old = cv2.imread('screenshots/tribelog-daytime.png', cv2.IMREAD_UNCHANGED)
    else:
        cv2.imwrite('screenshots/tribelog-daytime.png', np.zeros((10,160,3), dtype=np.uint8))
        tribeLog_daytime_old = cv2.imread('screenshots/tribelog-daytime.png', cv2.IMREAD_UNCHANGED)
    template_triggered = cv2.imread('templates/tribelog-triggered.png', cv2.IMREAD_UNCHANGED)
    template_destroyed = cv2.imread('templates/tribelog-destroyed.png', cv2.IMREAD_UNCHANGED)

    result_triggered = cv2.matchTemplate(tribeLog, template_triggered, cv2.TM_CCOEFF_NORMED)
    result_destroyed = cv2.matchTemplate(tribeLog, template_destroyed, cv2.TM_CCOEFF_NORMED)

    result_destroyed_locations = np.where( result_destroyed >= threshold)
    for result in zip(*result_destroyed_locations[::-1]):
        alert_destroyed = True
        if(result[1] < tribeLog_entry_y):
            tribeLog_entry_y = result[1]
            alert_destroyed_y = result[1]

    result_triggered_locations = np.where( result_triggered >= threshold)
    for result in zip(*result_triggered_locations[::-1]):
        alert_triggered = True
        if(result[1] < tribeLog_entry_y):
            tribeLog_entry_y = result[1]
            alert_triggered_y = result[1]

    # It will only be under 9999 if one of the templates was detected
    if(tribeLog_entry_y < 9999):
        # Get a crop of the day/time at this Y coord
        tribeLog_daytime_new = tribeLog[tribeLog_entry_y:tribeLog_entry_y + 10, 0:160]

        # Check if tribeLog_daytime_new matches tribeLog_daytime_old
        result_tribeLog_daytime = cv2.matchTemplate(tribeLog_daytime_old, tribeLog_daytime_new, cv2.TM_CCOEFF_NORMED)
        result_tribeLog_daytime_locations = np.where( result_tribeLog_daytime >= threshold)
        result_tribeLog_daytime_match = False
        for result in zip(*result_tribeLog_daytime_locations[::-1]):
            result_tribeLog_daytime_match = True

        if(result_tribeLog_daytime_match == False):
            # Something triggered!
            if(alert_triggered or alert_destroyed):
                if(alert_triggered_y > alert_destroyed_y):
                    postAlertToDiscord("Something Destroyed!",4)
                else:
                    postAlertToDiscord("Tek Sensor Triggered!",3)
            # Save this daytime info for future checks
            cv2.imwrite('screenshots/tribelog-daytime.png', tribeLog_daytime_new)

    # Also post tribe log to Discord as normal
    postTribeLogToDiscord()

# Post tribe log to Discord
def postTribeLogToDiscord():
    global settings
    
    url = settings["webhookTribeLog"]

    if(url == ""):
        #print("Monitoring: Tribe log not posted to Discord as Webhook is blank.")
        return

    message = "Latest tribe logs"
    message = addDiscordTag(message)

    data = {
        "content": message,
        "avatar_url": "https://i.imgur.com/cMBnUQo.png"
    }
    
    files = {
        "file" : ("./screenshots/tribelog-latest.png", open("./screenshots/tribelogplayers-latest.png", 'rb'))
    }

    result = requests.post(url, data = data, files=files)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postTribeLogToDiscord() had an error:")
        print(err)

# Post tribe log to Discord
def postAlertToDiscord(message = "Alert", priority = 0):
    global settings
    
    url = settings["webhookAlert"]

    if(url == ""):
        #print("Monitoring: Alert not posted to Discord as Webhook is blank.")
        return

    message = addDiscordTag(message, priority)

    data = {
        "content": message,
        "avatar_url": "https://i.imgur.com/cMBnUQo.png"
    }
    
    files = {
        "file" : ("./screenshots/tribelog-latest.png", open("./screenshots/tribelogplayers-latest.png", 'rb'))
    }

    result = requests.post(url, data = data, files=files)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postAlertToDiscord() had an error:")
        print(err)

# Post text message to Discord
def postMessageToDiscord(message, priority = 0):
    global settings
    
    url = settings["webhookGacha"]

    if(url == ""):
        print("Monitoring: " + message + " (Priority " + str(priority) + ")")
        return

    message = addDiscordTag(message, priority)

    data = {
        "content": message,
        "avatar_url": "https://i.imgur.com/cMBnUQo.png"
    }

    result = requests.post(url, data = data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postMessageToDiscord() had an error:")
        print(err)

# Report to Stonks API: Message
def postToStonksMessage(title, content, messagetype = "info"):
    # title: "Message title text",
    # type: "error",
    # description: "Can't reach gacha at bed seed12"

    global settings
    
    towertoken = settings["towertoken"]

    if(towertoken == ""):
        #print("Stonks API: No tower token found. Skipped reporting to the Stonks API.")
        return

    url = "https://hlia.xyz/stonksapi/msg/" + towertoken

    data = {
        "title": title,
        "type": messagetype,
        "content": content
    }

    try:
        result = requests.post(url, data = data)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postToStonksMessage() had an error:")
        print(err)

# Report to Stonks API: Lap Summary
def postToStonksLapSummary(time, towerStations):
    # time: 60 (number of seconds as an integer),
    # avg_bed_time: 100 (seconds as an integer)
    
    global settings
    
    towertoken = settings["towertoken"]

    if(towertoken == ""):
        #print("Stonks API: No tower token found. Skipped reporting to the Stonks API.")
        return

    url = "https://hlia.xyz/stonksapi/lap_summary/" + towertoken

    data = {
        "time": time,
        "tower_stations": towerStations
    }

    try:
        result = requests.post(url, data = data)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postToStonksLapSummary() had an error:")
        print(err)

# Report to Stonks API: Crystal Summary
def postToStonksCrystalSummary(bedNumber, elementDust, blackPearls, numCrystals, polyFreeSlots, time):
    # bed_number: the bed number as an int
    # element: amount of element dust collected as an integer,
    # pearls: amount of black pearls collected as an integer,
    # num_crystals: number of gacha crystals cracked,
    # poly_free_slots: free slots left in the poly vault,
    # time: number of seconds spent at the bed

    global settings
    
    towertoken = settings["towertoken"]

    if(towertoken == ""):
        #print("Stonks API: No tower token found. Skipped reporting to the Stonks API.")
        return

    url = "https://hlia.xyz/stonksapi/crystal_summary/" + towertoken

    data = {
        "bed_number": bedNumber,
        "element": elementDust,
        "pearls": blackPearls,
        "num_crystals": numCrystals,
        "poly_free_slots": polyFreeSlots,
        "time": time
    }

    try:
        result = requests.post(url, data = data)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postToStonksCrystalSummary() had an error:")
        print(err)

# Report to Stonks API: Seed Summary
def postToStonksSeedSummary(bedNumber, cropsAccessed, totalTraps, gachaPellets, cropPellets, tekPower, greenhouse, time):
    # bed_number: the bed number as an int
    # crops_accessed: the number of crop plots accessed as an int
    # total_traps: the number of y traps removed from the crop plots
    # gacha_pellets: number of pellets in the gacha,
    # crop_pellets: average number of pellets per crop plot,
    # tek_power: true/false boolean value
    # greenhouse: greenhouse % as an integer,
    # time: number of seconds spent at the bed

    global settings
    
    towertoken = settings["towertoken"]

    if(towertoken == ""):
        #print("Stonks API: No tower token found. Skipped reporting to the Stonks API.")
        return

    url = "https://hlia.xyz/stonksapi/seed_summary/" + towertoken

    data = {
        "bed_number": bedNumber,
        "crops_accessed": cropsAccessed,
        "total_traps": totalTraps,
        "gacha_pellets": gachaPellets,
        "crop_pellets": cropPellets,
        "tek_power": tekPower,
        "greenhouse": greenhouse,
        "time": time
    }

    try:
        result = requests.post(url, data = data)
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("---- ERROR: postToStonksSeedSummary() had an error:")
        print(err)

# Used to tag people with each message according to settings.json
def addDiscordTag(message, priority = 0):
    global settings
    
    if(priority == 5):
        message = message + " " + settings["tagLevel5"]
    elif(priority == 4):
        message = message + " " + settings["tagLevel4"]
    elif(priority == 3):
        message = message + " " + settings["tagLevel3"]
    elif(priority == 2):
        message = message + " " + settings["tagLevel2"]
    elif(priority == 1):
        message = message + " " + settings["tagLevel1"]
    else:
        message = message + " " + settings["tagLevel0"]

    # Add footer to Discord message
    message = message + "\nServer: " + settings["serverName"] + " on [" + settings["accountName"] + "] Account"
    
    return message

# Tracks that a new task has been started for the purpose of detecting downtime
def trackTaskStarted(name):
    global timeLastTaskStarted
    global timeLastTaskName
    global outageLevel0
    global outageLevel1
    global outageLevel2
    global outageLevel3
    
    # set the started time to now
    timeLastTaskStarted = time.time()
    
    # set the task name to the name provided
    timeLastTaskName = name
    
    # reset the outage levels to signify nothing reported
    outageLevel0 = False
    outageLevel1 = False
    outageLevel2 = False
    outageLevel3 = False

# Useful for clicking the menus when connecting to an Ark Server
def arkClickUI(x, y, delay):
    pyautogui.moveTo(x, y, duration=0.1)
    pyautogui.click()
    time.sleep(delay)

# Uses pixel color to detect what is visible on screen
def checkArkScreen():
    # Pixel coordinates for text
    gameTextExit = pyautogui.pixel(49,824)
    gameTextSession = pyautogui.pixel(148,138)
    
    if(gameTextExit == (135, 233, 255)):
        return "mainmenu"
    elif(gameTextSession == (136, 233, 255)):
        return "sessionlist"
    else:
        return "unknown"

# Launches Ark based on the gameLauncher specified in the config
def arkLaunch():
    global settings
    
    trackTaskStarted("Connecting: Launching Ark")

    # Launch Ark
    if(settings["gameLauncher"] == "steam"):
        # Steam Launch Ark:
        webbrowser.open_new("steam://rungameid/346110")
    elif(settings["gameLauncher"] == "epic"):
        # Epic Games Launch Ark:
        webbrowser.open_new("com.epicgames.launcher://apps/ark%3A743e47ee84ac49a1a49f4781da70e0d0%3Aaafc587fbf654758802c8e41e4fb3255?action=launch")
    time.sleep(15)

# From the Ark Main Menu searches for the server to join
def arkSearchForServer():
    global settings
    
    trackTaskStarted("Connecting: Searching for server")
    
    # Wait for color of E in EXIT
    count = 0
    while(checkArkScreen() != "mainmenu"):
        time.sleep(1)
        count += 1
        if(count > 100):
            print("---- ERROR: arkSearchForServer() had an error:")
            print("Couldn't detect Ark main menu")
            count = 0

    # Wait for join button on epic
    if(settings["gameLauncher"] == "epic"):
        time.sleep(5)

    # Click Join Ark
    pyautogui.moveTo(103, 523)
    pyautogui.click()

    # Get color of E in SESSION LIST
    count = 0
    while(checkArkScreen() != "sessionlist"):
        time.sleep(1)
        count += 1
        if(count > 100):
            print("---- ERROR: arkSearchForServer() had an error:")
            print("Couldn't detect Session List page")
            break

    time.sleep(0.5)

    # Click MAP drop down
    arkClickUI(914, 136, 1.5)

    # Click ALL MAPS from MAP drop down
    arkClickUI(914, 158, 1.5)

    # Click NAME FILTER search box
    arkClickUI(590, 140, 1.5)

    # Search for server name
    pyautogui.keyDown('ctrl')
    pyautogui.press('a')
    pyautogui.keyUp('ctrl')
    pyautogui.press('backspace')
    pyautogui.typewrite(settings["serverSearch"], interval=0.05)
    time.sleep(1.5)

    # Click SESSION FILTER drop down
    arkClickUI(330, 950, 1.5)

    # Click OFFICIAL from SESSION FILTER drop down
    if(settings["gameLauncher"] == "epic"):
        arkClickUI(330, 864, 1.5)
    else:
        arkClickUI(330, 819, 1.5)
    
    # Wait
    time.sleep(5)

# From the Ark Session List clicks refresh/join until connected
def arkJoinServer():
    # Get color of E in SESSION LIST
    while(checkArkScreen() == "sessionlist"):
        # Click REFRESH button
        arkClickUI(1229, 943, 2)

        # Wait
        time.sleep(3)

        # Click on the top server in the list
        arkClickUI(338, 242, 1.5)
        arkClickUI(338, 242, 0)

        # Click the JOIN button
        arkClickUI(1000, 940, 1.5)

        # Wait
        time.sleep(10)

# A function that connects to the ark server
def launchArk():
    arkLaunch()
    arkSearchForServer()
    arkJoinServer()

# Stops the monitoring thread
def stop():
    terminate(True)

# Main thread for monitoring the health of the gacha bot
def start(locationSettings):
    global settings
    global timeLastTaskStarted
    global timeLastTaskName
    global outageLevel0
    global outageLevel1
    global outageLevel2
    global outageLevel3

    settings = locationSettings

    pause(False)
    terminate(False)

    try:
        trackTaskStarted("Started Ark Monitoring")
        while(True):
            # Make sure the bot isn't paused
            checkTerminated()
            
            # Bot hasn't gone to a new task for 4min...
            if( outageLevel0 == False and ((time.time() - timeLastTaskStarted) > 240) ):
                screenshotScreen()
                errorMessage = "**MONITORING:** Possible crash?!? It has been over 4min since starting the task: " + timeLastTaskName
                postMessageToDiscord(errorMessage, 1)
                outageLevel0 = True
            # Bot hasn't gone to a new task for 5min...
            if( outageLevel1 == False and ((time.time() - timeLastTaskStarted) > 300) ):
                screenshotScreen()
                errorMessage = "**MONITORING:** Likely crash detected! It has been over 5min since starting the task: " + timeLastTaskName + "\n**PLEASE CHECK ON THE BOT!**"
                postMessageToDiscord(errorMessage, 1)
                errorMessage = "**MONITORING:** Attempting to unstuck the bot..."
                postMessageToDiscord(errorMessage, 0)
                pyautogui.press('F4')
                outageLevel1 = True
            # Bot hasn't gone to a new task for 7min...
            if( outageLevel2 == False and ((time.time() - timeLastTaskStarted) > 420) ):
                screenshotScreen()
                errorMessage = "**MONITORING:** Crash detected! It has been over 7min since starting the task: " + timeLastTaskName + "\n**PLEASE CHECK ON THE BOT!**"
                postMessageToDiscord(errorMessage, 2)
                outageLevel2 = True
            # Bot hasn't gone to a new task for 10min...
            if( outageLevel3 == False and ((time.time() - timeLastTaskStarted) > 600) ):
                screenshotScreen()
                errorMessage = "**MONITORING: CRASH DETECTED!** Bot has been stopped. It has been over 10min since starting the task: " + timeLastTaskName + "\nBot will require a manual restart."
                postMessageToDiscord(errorMessage, 1)
                pyautogui.press('F2')
                outageLevel3 = True
            # Now wait 15 seconds before we check the bot again...
            time.sleep(15)
    except Exception as e:
        print("Monitoring thread terminated.")
        errorMessage = "Monitoring thread terminated!"
        postMessageToDiscord(errorMessage, 0)
        print(str(e))
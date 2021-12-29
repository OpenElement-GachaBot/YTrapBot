import pyautogui
import ark
import json
import time
import cv2
import numpy as np
import screen
import arkMonitoring


crystal_template = cv2.imread("templates/gacha_crystal.png", cv2.IMREAD_GRAYSCALE)
gen2suit_template = cv2.imread("templates/gen2suit.png", cv2.IMREAD_GRAYSCALE)
deposit_all_template = cv2.imread("templates/deposit_all.png", cv2.IMREAD_COLOR)
tooltips_template = cv2.imread("templates/tool_tips_enabled.png", cv2.IMREAD_GRAYSCALE)
added_template = cv2.imread("templates/added_template.png", cv2.IMREAD_GRAYSCALE)
vault_full_template = cv2.imread("templates/vault_full.png", cv2.IMREAD_GRAYSCALE)

lower_cyan = np.array([90,255,255])
upper_cyan = np.array([110,255,255])

hsv = cv2.cvtColor(deposit_all_template, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
masked_template = cv2.bitwise_and(deposit_all_template, deposit_all_template, mask= mask)
deposit_all_gray_template = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)


beds = {}


lapCounter = 0
seedLapCounter = 0

fillCropsInterval = 28800
fillCropsLastFilled = 0
fillCropsLap = 0
tribeLogOpenInterval = 0
tribeLogLastOpened = 0
tribeLogIsOpen = False

suicideBed = ""

ark.setParams(1.45, 1.45, 10)
statusText = ""

def setStatusText(txt):
    global statusText
    statusText = txt

def setBeds(b):
    beds = b;

def disableToolTips():
    roi = screen.getScreen()[164:210,623:668]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, tooltips_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 4000000):
        pyautogui.press('g')

def checkVaultFull():
    roi = screen.getScreen()[505:517,1092:1129]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, vault_full_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 480000):
        return True
    return False


def canDeposit():
    roi = screen.getScreen()
    screen_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(screen_hsv, lower_cyan, upper_cyan)
    masked_screen = cv2.bitwise_and(roi, roi, mask= mask)
    gray_screen = cv2.cvtColor(masked_screen, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, deposit_all_gray_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 10000000):
        return True
    return False


def checkWeWearingSuit():
    roi = screen.getScreen()[150:440,740:1170]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, gen2suit_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 1000000):
        return True
    return False


def checkWeHoldingSuit():
    roi = screen.getScreen()[230:330,110:680]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, gen2suit_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 1000000):
        return True
    return False

def checkWeGotRowOfCrystals():
    roi = screen.getScreen()[323:423,111:213]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, crystal_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if(max_val > 5500000):
        return True
    return False

def checkWeGotCrystals():
    roi = screen.getScreen()[230:330,120:210]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, crystal_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if(max_val > 5500000):
        return True
    return False

def waitForAddedGraphic():
    counter = 0
    while(counter < 10):
        roi = screen.getScreen()[1030:1070, 37:142]
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        res = cv2.matchTemplate(gray_roi, added_template, cv2.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if(max_val > 3000000):
            return True

        time.sleep(0.1)
        counter += 1
    return False


def dropGen2Suit(popcorn = False):
    pyautogui.press('i')
    time.sleep(2.0)
    while(ark.inventoryIsOpen() == False):
        pyautogui.press('i')
        ark.sleep(2.0)
    
    while(checkWeWearingSuit()):
        pyautogui.moveTo(800, 200)
        pyautogui.dragTo(450, 275, 0.2)

        pyautogui.moveTo(800, 300)
        pyautogui.dragTo(450, 275, 0.2)

        pyautogui.moveTo(800, 400)
        pyautogui.dragTo(450, 275, 0.2)

        pyautogui.moveTo(1100, 200)
        pyautogui.dragTo(450, 275, 0.2)

        pyautogui.moveTo(1100, 400)
        pyautogui.dragTo(450, 275, 0.2)
        pyautogui.moveTo(800, 200)

        ark.sleep(2.0)

    
    if(popcorn):
        ark.searchMyStacks("fed")
        pyautogui.moveTo(165, 280)
        pyautogui.click()
        while(checkWeHoldingSuit()):
            pyautogui.press('o')
    else:
        ark.dropItems("fed")
        ark.dropItems("")

    ark.closeInventory()


def loadGacha(gachaseed):
    global seedLapCounter
    global fillCropsInterval
    global fillCropsLastFilled
    global fillCropsLap
    
    if((beds["aberrationMode"] == False)):
        fillCropsTimeSinceFilled = time.time() - fillCropsLastFilled
        if(fillCropsTimeSinceFilled > fillCropsInterval):
            fillCropsLap = seedLapCounter
            fillCropsLastFilled = time.time()

        if(seedLapCounter == fillCropsLap):
            ableToFillCrops = False
            
            for i in range(6):
                if(ark.openInventory() == True):
                    ableToFillCrops = True
                    break
            if(ark.inventoryIsOpen() == False):
                ableToFillCrops = False

            # Check inventory is open before trying to collect pellets
            if(ableToFillCrops == True):
                ark.takeAll("ll")
                ark.searchMyStacks("ll")
                if(beds["turnDirection"] == "360"):
                    ark.tTransferTo(10)
                else:
                    ark.tTransferTo(5)
                ark.closeInventory()

    if(beds["turnDirection"] == "360"):
        ark.step('right', 1.0)
        ark.harvestCropStack("trap")
        pyautogui.press('c')

        ark.lookUp()
        ark.lookDown()

        ark.step('right', 1.0)
        ark.harvestCropStack("trap", 1.2)
        pyautogui.press('c')

        ark.lookUp()
        ark.lookDown()
        ark.step('right', 1.0)
        ark.harvestCropStack("trap")
        pyautogui.press('c')

        ark.step('right', 1.0)

    else:
        if(beds["turnDirection"] == "left"):
            ark.step('left', 1.0)
        else:
            ark.step('right', 1.0)
    
        ark.harvestCropStack("trap")
        pyautogui.press('c')
        if(beds["turnDirection"] == "left"):
            ark.step('left', 1.0)
        else:
            ark.step('right', 1.0)
    
        ark.lookDown()
        ark.step('up', 0.1)
        ark.harvestCropStack("trap", 1.2)
        pyautogui.press('c')
        if(beds["turnDirection"] == "left"):
            ark.step('right', 2.0)
        else:
            ark.step('left', 2.0)
    
    ark.lookUp()
    ark.lookDown()

    # Try to open the gacha inventory for 10 seconds
    for i in range(5):
        if(ark.openInventory() == True):
            ark.takeAll("ll")
            ark.transferAll("trap")
            ark.transferAll()
            ark.dropItems("")
            ark.closeInventory()
            return
        else:
            ark.sleep(2)

    # Stand up if can't access the gacha after 10 seconds
    pyautogui.press('c')

    # Try to open the gacha inventory for another 10 seconds
    for i in range(5):
        if(ark.openInventory() == True):
            ark.takeAll("ll")
            ark.transferAll("trap")
            ark.transferAll()
            ark.dropItems("")
            ark.closeInventory()
            return
        else:
            ark.sleep(2)
    
    arkMonitoring.screenshotScreen()
    errorMessage = "Failed to access gacha inventory at " + gachaseed
    arkMonitoring.postMessageToDiscord(errorMessage, 0)
    arkMonitoring.postToStonksMessage("Cannot Access Gacha", errorMessage, "error")

    pyautogui.press('i')
    time.sleep(2.0)
    while(ark.inventoryIsOpen() == False):
        pyautogui.press('i')
        ark.sleep(2.0)
    
    ark.searchMyStacks("trap")
    pyautogui.moveTo(165, 280)
    pyautogui.click()
    for i in range(40):
        pyautogui.press('o')
        ark.sleep(0.5)
    ark.dropItems("")
    ark.closeInventory()

    
def pickupWithFSpam():
    pyautogui.press('c')
    ark.lookDown()
    ark.step('s', 1.5)
    for i in range(6):
        pyautogui.press('f')
        ark.sleep(0.2)
        ark.step('w', 0.1)
    ark.step('w', 1.0)

    pyautogui.press('f')
        
def pickupWithWhip():
    pyautogui.press('c')
    if(beds["sideVaults"]):
        ark.step('left', 1.0)
    else:
        ark.lookUp()

    if(ark.openInventory()):
        ark.takeAll("broken")
        ark.searchStructureStacks("whip")
        pyautogui.moveTo(1295, 283);
        pyautogui.dragTo(690, 1050, 0.5, button='left')
        waitForAddedGraphic()
        ark.closeInventory()

        if(beds["sideVaults"]): 
            ark.step('right', 1.2)    
        else:
            ark.lookDown()
        ark.step('right', 2.1)
        pyautogui.press('1')
        ark.sleep(2.0)
        pyautogui.click()
        ark.sleep(5.0)
        pyautogui.click()
        ark.sleep(2.0)
        pyautogui.press('1')
        ark.step('left', 2.1)
        ark.lookDown()
    else:
        if(beds["sideVaults"]):
            ark.step('right', 1.2)
        else:
            ark.lookDown()
        pyautogui.press('c')
        pickupWithFSpam()

   
def depositInDedi():   
    for i in range(8):
        pyautogui.press('e')
        ark.sleep(0.2)
        while(ark.getBedScreenCoords() != None):
            pyautogui.press('esc')
            ark.sleep(2.0)

def whipCrystals():
    for i in range(beds["crystalBeds"]):
        runTime = time.time()
        arkMonitoring.trackTaskStarted("Collecting at gachacrystal" + str(i).zfill(2))
        setStatusText("Picking up crystals")
        ark.bedSpawn(beds["crystalBedPrefix"] + str(i).zfill(2), beds["bedX"], beds["bedY"], beds["singlePlayer"])
        openTribeLog()

        if(beds["pickupMethod"] == "whip"):
            pickupWithWhip()
        else:
            pickupWithFSpam()

        pyautogui.press('c')
        ark.step('up', 0.9)
    
        canDepositAttempts = 0
        while(canDeposit() == False):
            ark.step('w', 0.4)
            ark.sleep(0.2)
            if(canDepositAttempts == 25):
                ark.step('d', 0.02)
            elif(canDepositAttempts > 30):
                break
            canDepositAttempts += 1
        
        ark.sleep(5)

        canDepositAttempts = 0
        while(canDeposit() == False):
            ark.step('w', 0.4)
            ark.sleep(0.2)
            if(canDepositAttempts == 25):
                ark.step('d', 0.02)
            elif(canDepositAttempts > 30):
                break
            canDepositAttempts += 1

        pyautogui.press('i')
        ark.sleep(2.0)
        while(ark.inventoryIsOpen() == False):
            pyautogui.press('i')
            ark.sleep(2.0)

        disableToolTips()
        
        ark.searchMyStacks("gacha")
        pyautogui.moveTo(167, 280, 0.1)
        pyautogui.click()
        ark.sleep(1.0)
    
        crystalOpenAttempts = 0
        crystalHotbarOpens = 0
        while(checkWeGotRowOfCrystals()):
            ark.crystalHotBarUse()
            ark.sleep(0.3)
            # Make sure we don't get stuck here forever
            crystalOpenAttempts += 1
            # Count how many times we opened crystals
            crystalHotbarOpens += 1
            if(crystalOpenAttempts == 60):
                errorMessage = "Bot wasn't able to open gacha crystals within normal amount of attempts. It might be stuck! Trying to manually put the crystals on the hotbar."
                arkMonitoring.postMessageToDiscord(errorMessage, 0)
                arkMonitoring.postToStonksMessage("Crystal Opening Error", errorMessage, "error")
                arkMonitoring.trackTaskStarted("Putting gacha crystals onto hotbar")
                ark.crystalHotBarSetup()
                # Reset opens to zero as nothing opened yet
                crystalHotbarOpens = 0
            elif(crystalOpenAttempts > 120):
                # welp, time to giveup I guess
                # Reset opens to zero as nothing probably opened
                crystalHotbarOpens = 0
                break

        ark.crystalHotBarUse()
        ark.crystalHotBarUse()
        crystalHotbarOpens += 1

        ark.closeInventory()
            
        if(beds["numDedis"] == 2):
            depositInDedi()
            ark.step('up', 0.7)
            depositInDedi()
    
        if(beds["numDedis"] == 4):
            ark.step("right", 0.3)
            depositInDedi()
            ark.step('up', 0.7)
            depositInDedi() 

            ark.step("left", 0.6)
            depositInDedi()
            ark.step("down", 0.7)
            depositInDedi()
            ark.lookUp()

        if(beds["sideVaults"]):
            ark.lookUp()
            ark.lookDown()
            ark.step('left', 1.0)
        else:
            ark.lookUp()

        if(ark.openInventory()):
        
            # Only transfer the whip if whip pickup method selected
            if(beds["pickupMethod"] == "whip"):
                time.sleep(0.5)
                pyautogui.moveTo(690, 1050)
                pyautogui.click()
                pyautogui.press('t')
                time.sleep(0.5)
                ark.transferAll("whip")
            
            """
            if(checkVaultFull()):
                arkMonitoring.screenshotScreen()
                errorMessage = "Please empty the gacha vault! No room left in the vault for more gacha items."
                arkMonitoring.postMessageToDiscord(errorMessage, 1)
            else:
                for item in beds["dropItems"]:
                    ark.dropItems(item)
                for item in beds["keepItems"]:
                    ark.transferAll(item)
            """
            
            for item in beds["dropItems"]:
                ark.dropItems(item)
            for item in beds["keepItems"]:
                ark.transferAll(item)
            
            ark.dropItems("")
            ark.closeInventory()
        if(beds["sideVaults"]):
            ark.step('right', 1.2)
        else:
            ark.lookDown()
        if(beds["dropGen2Suits"]):
            dropGen2Suit(False)
        pyautogui.press('x')
        while(ark.accessBed() == False):
            ark.sleep(10)
        runTime = time.time() - runTime
        runTimeMessage = "Time taken at gachacrystal" + str(i).zfill(2) + " was " + str(int(round(runTime))) + " seconds.\nOpened approximately " + str((crystalHotbarOpens * 9)) + " crystals."
        if(runTime < 60 or runTime > 160):
            runTimeMessage += "\n**Might be an issue with this crystal area due to time taken!**"
            arkMonitoring.postMessageToDiscord(runTimeMessage, 0)
        else:
            arkMonitoring.postMessageToDiscord(runTimeMessage, 0)
        
        arkMonitoring.postToStonksCrystalSummary(i, 0, 0, (crystalHotbarOpens * 9), 0, int(round(runTime)))
        
    
def openTribeLog():
    global tribeLogOpenInterval
    global tribeLogLastOpened

    if(beds["openTribeLog"]):
        tribeLogTimeSinceOpened = time.time() - tribeLogLastOpened
        if(tribeLogTimeSinceOpened > tribeLogOpenInterval):
            ark.openTribeLog()
            arkMonitoring.screenshotTribeLog()
            ark.sleep(1)
            ark.closeTribeLog()
            ark.sleep(2)
            tribeLogLastOpened = time.time()

def openTribeLogTekPod():
    global tribeLogOpenInterval
    global tribeLogLastOpened
    global tribeLogIsOpen

    if(beds["openTribeLog"]):
        # Always open the tribe log in tek pod
        if(tribeLogIsOpen == False):
            ark.openTribeLog()
            tribeLogIsOpen = True

        # Only screenshot the tribe log if enough time has passed based on the settings
        tribeLogTimeSinceOpened = time.time() - tribeLogLastOpened
        if(tribeLogTimeSinceOpened > tribeLogOpenInterval):
            arkMonitoring.screenshotTribeLog()
            ark.sleep(1)
            tribeLogLastOpened = time.time()

def closeTribeLogTekPod():
    global tribeLogIsOpen
    
    if(beds["openTribeLog"]):
        ark.closeTribeLog()
        tribeLogIsOpen = False
        ark.sleep(2)

def suicideAndRespawn(alreadyAccessingBed = True, trackTask = True):
    global beds

    if(alreadyAccessingBed == False):
        ark.checkTerminated()
        ark.lookDown()
        pyautogui.press('x')
        while(ark.accessBed() == False):
            ark.sleep(10)

    runTime = time.time()
    if(trackTask): # Track this by default - optional for when suiciding is being done to unstuck the bot
        arkMonitoring.trackTaskStarted("Suiciding")
    ark.bedSpawn(beds["suicideBed"], beds["bedX"], beds["bedY"])
    if(beds["dropGen2Suits"]):
        dropGen2Suit(False)
    
    if(beds["suicideMethod"] == "tekpod"):
        # Use the tek pod to recharge food/water
        ark.tekPodEnter()
        openTribeLogTekPod()
        ark.sleep(60)
        closeTribeLogTekPod()
        ark.tekPodLeave()

    while(ark.getBedScreenCoords() == None):
        ark.sleep(0.5)

    runTime = time.time() - runTime
    runTimeMessage = "Time taken suiciding was " + str(int(round(runTime))) + " seconds."
    arkMonitoring.postMessageToDiscord(runTimeMessage, 0)
    arkMonitoring.postToStonksMessage("Suicide", runTimeMessage, "info")

def botUnstuck():
    arkMonitoring.postMessageToDiscord("Bot attempting to unstuck itself...", 0)
    arkMonitoring.postToStonksMessage("Unstucking", "Bot attempting to unstuck itself...", "info")
    ark.terminate(True)         # terminate will stop whatever the bot was doing
    time.sleep(10)              # wait for the bot to finish
    ark.terminate(False)        # set terminate to False so the commands work
    ark.openConsole()           # try to open the console, press ESCAPE if console won't open then tries again
    ark.closeConsole()          # close the console
    ark.sleep(2)
    
    # Drop all so when we fast travel it doesn't leave a 30min bag
    pyautogui.press('i')
    time.sleep(2.0)
    while(ark.inventoryIsOpen() == False):
        ark.checkTerminated()
        pyautogui.press('i')
        ark.sleep(2.0)
    ark.dropItems("")
    ark.closeInventory()

    # Suicide and respawn
    suicideAndRespawn(False, True)
    ark.sleep(20)
    ark.terminate(True)

def getStatus():
    return statusText
    
def stop():
    ark.terminate(True)
    arkMonitoring.postMessageToDiscord("GachaLogBot has been stopped.", 0)
    arkMonitoring.postToStonksMessage("Stopped", "OpenElement has been stopped.", "info")
    arkMonitoring.stop()

def start(b):
    global beds
    global lapCounter
    global seedLapCounter
    global tribeLogOpenInterval

    inTekPod = False
    beds = b
    tribeLogOpenInterval = beds["showLogInterval"]
    ark.pause(False)
    ark.terminate(False)
    ark.setFirstRun(True)
    setStatusText("Starting. F2 to stop. Alt tab back into the game NOW.")
    arkMonitoring.postMessageToDiscord("GachaLogBot is starting...", 0)
    arkMonitoring.postToStonksMessage("Started", "OpenElement has been started.", "info")
    try:
        ark.sleep(8)
        setStatusText("spawning in...")
        start = time.time()
        while(True):
            lapTime = time.time()
            for i in range(beds["seedBeds"]):
                duration = time.time() - start
                if(duration > beds["crystalInterval"]):
                    if(inTekPod == True):
                        closeTribeLogTekPod()
                        ark.tekPodLeave()
                        inTekPod = False
                    start = time.time()
                    whipCrystals()
                    lapCounter += 1
                    if(lapCounter >= beds["suicideFrequency"]):
                        lapCounter = 0
                        setStatusText("Suiciding . . .")
                        suicideAndRespawn()
                
                if(beds["loadGachaMethod"] == "ytrap"):
                    runTime = time.time()
                    arkMonitoring.trackTaskStarted("Seeding at gachaseed" + str(i).zfill(2))
                    setStatusText("Seeding at gachaseed" + str(i).zfill(2))
                    ark.bedSpawn(beds["seedBedPrefix"] + str(i).zfill(2), beds["bedX"], beds["bedY"], beds["singlePlayer"])
                    openTribeLog()
                    loadGacha("gachaseed" + str(i).zfill(2))
                    if(beds["dropGen2Suits"]):
                        dropGen2Suit(False)
                    ark.lookDown()
                    pyautogui.press('x')
                    while(ark.accessBed() == False):
                        ark.sleep(10)
                    runTime = time.time() - runTime
                    runTimeMessage = "Time taken at gachaseed" + str(i).zfill(2) + " was " + str(int(round(runTime))) + " seconds."
                    if(runTime > 180 or runTime < 100):
                        runTimeMessage += " **Likely an issue with this station!**"
                        arkMonitoring.postMessageToDiscord(runTimeMessage, 0)
                    else:
                        arkMonitoring.postMessageToDiscord(runTimeMessage, 0)
                    
                    arkMonitoring.postToStonksSeedSummary(i, 0, 0, 0, 0, False, 0, int(round(runTime)))
                elif(beds["loadGachaMethod"] == "none"):
                    # Check if they are in a tek pod or not
                    if(inTekPod == False):
                        ark.bedSpawn(beds["suicideBed"], beds["bedX"], beds["bedY"])
                        ark.tekPodEnter()
                        inTekPod = True
                        time.sleep(5)
                    else:
                        arkMonitoring.trackTaskStarted("Lying in Tek Pod")
                        openTribeLogTekPod()
                        ark.sleep(10)
                
            seedLapCounter += 1
            
            lapTime = time.time() - lapTime
            lapTimeMinutes = lapTime / 60
            lapTimeStationAvg = lapTime / int(beds["seedBeds"])
            lapMessage = " **Lap #" + str(seedLapCounter) + " completed!** This lap of the full tower was " + str(int(round(lapTime))) + " seconds (" + str(int(round(lapTimeMinutes))) + " minutes).\nThis is an average of **" + str(int(round(lapTimeStationAvg))) + " seconds** per each of the " + str(beds["seedBeds"]) + " seed beds."
            arkMonitoring.postMessageToDiscord(lapMessage, 0)
            arkMonitoring.postToStonksLapSummary(int(round(lapTime)), beds["seedBeds"])

            time.sleep(0.1)
    except Exception as e:
        print("YTrap thread terminated.")
        print(str(e))
        errorMessage = "YTrap thread terminated!"
        arkMonitoring.postMessageToDiscord(errorMessage, 1)
        arkMonitoring.postToStonksMessage("Stopped", "OpenElement has been stopped (or crashed).", "info")

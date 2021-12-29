import pyautogui
import ark
import json
import time
import cv2
import numpy as np
import screen


crystal_template = cv2.imread("templates/gacha_crystal.png", cv2.IMREAD_GRAYSCALE)
gen2suit_template = cv2.imread("templates/gen2suit.png", cv2.IMREAD_GRAYSCALE)
deposit_all_template = cv2.imread("templates/deposit_all.png", cv2.IMREAD_COLOR)
tooltips_template = cv2.imread("templates/tool_tips_enabled.png", cv2.IMREAD_GRAYSCALE)
added_template = cv2.imread("templates/added_template.png", cv2.IMREAD_GRAYSCALE)

lower_cyan = np.array([90,255,255])
upper_cyan = np.array([110,255,255])

hsv = cv2.cvtColor(deposit_all_template, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
masked_template = cv2.bitwise_and(deposit_all_template, deposit_all_template, mask= mask)
deposit_all_gray_template = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)


beds = {}


lapCounter = 0
seedLapCounter = 0

fillCropsInterval = 43200
fillCropsLastFilled = 0
fillCropsLap = 0
tribeLogOpenInterval = 0
tribeLogLastOpened = 0

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

    print(max_val)
    if(max_val > 1000000):
        return True
    return False


def checkWeHoldingSuit():
    roi = screen.getScreen()[230:330,110:680]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_roi, gen2suit_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    print(max_val)
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


def loadGacha():
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
            for i in range(6):
                if(ark.openInventory() == True):
                    break
            if(ark.inventoryIsOpen() == False):
                return
            
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

    for i in range(10):
        if(ark.openInventory() == True):
            ark.takeAll("ll")
            ark.transferAll("trap")
            ark.transferAll()
            ark.dropItems("")
            ark.closeInventory()
            return
        else:
            ark.sleep(2)

    pyautogui.press('i')
    time.sleep(2.0)
    while(ark.inventoryIsOpen() == False):
        pyautogui.press('i')
        ark.sleep(2.0)
    

    ark.searchMyStacks("trap")
    pyautogui.moveTo(165, 280)
    pyautogui.click()
    for i in range(30):
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
        setStatusText("Picking up crystals")
        ark.bedSpawn(beds["crystalBedPrefix"] + str(i).zfill(2), beds["bedX"], beds["bedY"], beds["singlePlayer"])
        openTribeLog()

        if(beds["pickupMethod"] == "whip"):
            pickupWithWhip()
        else:
            pickupWithFSpam()

        pyautogui.press('c')
        ark.step('up', 0.9)
    
        while(canDeposit() == False):
            ark.step('w', 0.4)
            ark.sleep(0.2)
        
        ark.sleep(5)

        while(canDeposit() == False):
            ark.step('w', 0.4)
            ark.sleep(0.2)
        ark.step('w', 0.4)
        
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
    
        count = 0
        while(checkWeGotRowOfCrystals()):
            """
            pyautogui.moveTo(167, 280)
            pyautogui.click()
            for i in range(6):
                pyautogui.moveTo(167+(i*95), 280, 0.1)
                pyautogui.press('e')
    
            ark.sleep(0.8)
            count += 6
            """
            ark.crystalHotBarUse()
            ark.sleep(0.3)
    
        pyautogui.moveTo(165, 280)
        pyautogui.click()
        while(checkWeGotCrystals()):
            """
            pyautogui.press('e')
            ark.sleep(0.2)
            count += 1
            if(count > 300):
                break
            """
            ark.crystalHotBarUse()
            ark.sleep(0.3)

        ark.crystalHotBarUse()
        ark.crystalHotBarUse()

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
            time.sleep(0.5)
            pyautogui.moveTo(690, 1050)
            pyautogui.click()
            pyautogui.press('t')
            time.sleep(0.5)

            ark.transferAll("whip")

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
    
def openTribeLog():
    global tribeLogOpenInterval
    global tribeLogLastOpened

    if(beds["openTribeLog"]):
        tribeLogTimeSinceOpened = time.time() - tribeLogLastOpened
        if(tribeLogTimeSinceOpened > tribeLogOpenInterval):
            ark.openTribeLog()
            ark.sleep(4)
            ark.closeTribeLog()
            ark.sleep(2)
            tribeLogLastOpened = time.time()
            
def getStatus():
    return statusText
    
def stop():
    ark.terminate(True)

def start(b):
    global beds
    global lapCounter
    global seedLapCounter
    global tribeLogOpenInterval

    beds = b
    tribeLogOpenInterval = beds["showLogInterval"]
    ark.pause(False)
    ark.terminate(False)
    setStatusText("Starting. F2 to stop. Alt tab back into the game NOW.")
    try:
        ark.sleep(8)
        setStatusText("spawning in...")
        start = time.time()
        while(True):
            for i in range(beds["seedBeds"]):
                duration = time.time() - start
                if(duration > beds["crystalInterval"]):
                    start = time.time()
                    whipCrystals()
                    lapCounter += 1
                    if(lapCounter > beds["suicideFrequency"]):
                        setStatusText("Suiciding . . .")
                        lapCounter = 0
                        suicideBed = beds["suicideBed"]
                        ark.bedSpawn(suicideBed, beds["bedX"], beds["bedY"])
                        if(beds["dropGen2Suits"]):
                            dropGen2Suit(False)
                        while(ark.getBedScreenCoords() == None):
                            ark.sleep(0.5)

                setStatusText("Seeding at gachaseed" + str(i).zfill(2))

                ark.bedSpawn(beds["seedBedPrefix"] + str(i).zfill(2), beds["bedX"], beds["bedY"], beds["singlePlayer"])
                openTribeLog()
                loadGacha()
                if(beds["dropGen2Suits"]):
                    dropGen2Suit(False)
                ark.lookDown()
                pyautogui.press('x')
                while(ark.accessBed() == False):
                    ark.sleep(10)
                
            seedLapCounter += 1

            time.sleep(0.1)
    except:
        print("Bot thread terminated.")

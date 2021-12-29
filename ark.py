"""
This is an API for ark GUI related functions.

"""

import time
import pyautogui
import screen
import cv2
import numpy as np

inventory_template = cv2.imread("templates/inventory_template.png", cv2.IMREAD_COLOR)
invHsvLower = np.array([86,117,255])
invHsvUpper = np.array([106,137,255])
hsv = cv2.cvtColor(inventory_template, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, invHsvLower, invHsvUpper)
masked_template = cv2.bitwise_and(inventory_template, inventory_template, mask= mask)
inventory_template = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)


rr_inventory = cv2.imread("templates/receiving_remote_inventory.png", cv2.IMREAD_COLOR)
hsv = cv2.cvtColor(rr_inventory, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, invHsvLower, invHsvUpper)
masked_template = cv2.bitwise_and(rr_inventory, rr_inventory, mask= mask)
rr_inventory = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)


tribelog_template = cv2.imread("templates/tribe_log.png", cv2.IMREAD_COLOR)

img = cv2.imread("templates/bed_button_corner.png", cv2.IMREAD_GRAYSCALE)
bed_button_edge = cv2.Canny(img,100,200)

lookUpDelay = 3
lookDownDelay = 1.75

setFps = 25
firstRun = True
terminated = False
paused = False

hsvLower = np.array([86, 109, 255]) 
hsvUpper = np.array([106, 129, 255])

hsv = cv2.cvtColor(tribelog_template, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, hsvLower, hsvUpper)
masked_template = cv2.bitwise_and(tribelog_template, tribelog_template, mask= mask)
tribelog_template = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)



#passing this function True will cause most functions in this script to throw an exception
#useful to terminate a thread in a multithreaded environment
def terminate(t):
    global terminated
    terminated = t

#passing this function True will cause the bot to halt until it is passed False again
#note that terminate(True) will still kill the bot
def pause(p):
    global paused
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
        raise Exception("Bot thread terminated.")

    #if paused, halt but also die if terminated 
    while(paused):
        time.sleep(0.1)
        if(terminated):
            raise Exception("Bot thread terminated.")

#internal function, don't use. sleeps for a period of time
def sleep(s):
    checkTerminated()
    if(s > 5):
        elapsed = 0
        while(elapsed < s):
            time.sleep(1)
            elapsed += 1
            checkTerminated()
    else:
        time.sleep(s)
    checkTerminated()

#types t.maxfps xx into the in-game console
def limitFps():
    global setFps
    checkTerminated()
    pyautogui.press("tab")
    sleep(0.5)
    pyautogui.typewrite("t.maxfps " + str(setFps), interval=0.02)
    pyautogui.press("enter")

#type gamma 5 into the console
def setGamma():
    checkTerminated()
    pyautogui.press("tab")
    sleep(0.5)
    pyautogui.typewrite("gamma 5", interval=0.02)
    pyautogui.press("enter")


#sets the look up/down delays plus the FPS which affects turning speed
def setParams(up, down, fps):
    global lookUpDelay
    global lookDownDelay
    global setFps
    lookUpDelay = up
    lookDownDelay = down
    setFps = fps

#looks up 90 degrees
def lookUp():
    global lookUpDelay
    checkTerminated()
    pyautogui.keyDown('up')
    sleep(lookUpDelay)
    pyautogui.keyUp('up')

#looks down 90 degrees
def lookDown():
    global lookDownDelay
    checkTerminated()
    pyautogui.keyDown('down')
    sleep(lookDownDelay)
    pyautogui.keyUp('down')

#types a bed name into the search entry on the respawn screen
def enterBedName(name):
    checkTerminated()
    pyautogui.moveTo(336, 986, duration=0.1)
    pyautogui.click()
    pyautogui.keyDown('ctrl')
    pyautogui.press('a')
    pyautogui.keyUp('ctrl')
    pyautogui.press('backspace')
    pyautogui.typewrite(name, interval=0.05)
    sleep(0.5)

#returns true if there is a button to respawn next to the bed name entry
def checkBedButtonEdge():
    checkTerminated()
    img = screen.getGrayScreen()[950:1100,580:620]
    img = cv2.Canny(img, 100, 200)
    res = cv2.matchTemplate(img, bed_button_edge, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print(max_val)
    if(max_val > 2500000):
        return True
    return False

def detectWhiteFlash():
    roi = screen.getScreen()[700:900,0:1920]
    res1 = np.all([roi == 255])
    return res1
 
#spawns on a bed named bedName at click coords x, y
#requires the player to have opened a bed to fast travel first
def bedSpawn(bedName, x, y, singlePlayer = False):
    global firstRun
    checkTerminated()
    sleep(1.5)
    enterBedName(bedName)
    sleep(0.25)
    pyautogui.moveTo(x, y)
    sleep(0.25)
    pyautogui.click()
    sleep(0.25)
    if(checkBedButtonEdge):
        pyautogui.moveTo(755, 983)
        sleep(0.25)
        pyautogui.click()
        count = 0
        while(detectWhiteFlash() == False):
            time.sleep(0.1)
            count += 1
            if(count > 200):
                break

        sleep(13)
        if(firstRun == True):
            firstRun = False
            limitFps()
            setGamma()
        if(singlePlayer):
            sleep(1.0)
            lookDown()
            pyautogui.keyDown('e')
            sleep(1.0)
            pyautogui.moveTo(1250, 550)
            sleep(1.0)
            pyautogui.keyUp('e')
            sleep(1.0)
            pyautogui.press('e')
            sleep(1.0)
            step('left', 1.0)


        pyautogui.press('c')
        return True
    else:
        return False

#returns true if an inventory is open
def inventoryIsOpen():# {{{
    checkTerminated()
    roi = screen.getScreen()[90:150,100:300]
    screen_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(screen_hsv, invHsvLower, invHsvUpper)
    masked_screen = cv2.bitwise_and(roi, roi, mask= mask)
    gray_screen = cv2.cvtColor(masked_screen, cv2.COLOR_BGR2GRAY)

    cv2.imwrite("dump.png", gray_screen)

    res = cv2.matchTemplate(gray_screen, inventory_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if(max_val > 50000000.0):
        return True
    return False



def receivingRemoteInventory():
    checkTerminated()
    roi = screen.getScreen()[230:940,1240:1820]
    screen_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(screen_hsv, invHsvLower, invHsvUpper)
    masked_screen = cv2.bitwise_and(roi, roi, mask= mask)
    gray_screen = cv2.cvtColor(masked_screen, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, rr_inventory, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if(max_val > 30000000.0):
        return True
    return False


#returns true if the tribe log is open
def tribelogIsOpen():
    checkTerminated()
    roi = screen.getScreen()[80:150,1320:1510]
    screen_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(screen_hsv, hsvLower, hsvUpper)
    masked_screen = cv2.bitwise_and(roi, roi, mask= mask)
    gray_screen = cv2.cvtColor(masked_screen, cv2.COLOR_BGR2GRAY)

    res = cv2.matchTemplate(gray_screen, tribelog_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print(max_val)

    if(max_val > 50000000):
        return True
    return False


#closes an inventory
def closeInventory():# {{{
    checkTerminated()
    while(inventoryIsOpen() == True):
        pyautogui.moveTo(1816, 37)
        pyautogui.click()
        count = 0
        while(inventoryIsOpen()):
            count += 1
            if(count > 20):
                break
            sleep(0.1)
    time.sleep(0.2)

def openTribeLog():
    checkTerminated()
    pyautogui.press('l')
    sleep(2.0)
    while(tribelogIsOpen() == False):
        pyautogui.press('l')
        sleep(2.0)

def closeTribeLog():
    checkTerminated()
    while(tribelogIsOpen() == True):
        pyautogui.press('escape')
        count = 0
        while(tribelogIsOpen()):
            count += 1
            if(count > 20):
                break
            sleep(0.2)
        
#crafts an item in a remote inventory (not the player inventory)
def craft(item, timesToPressA):
    checkTerminated()
    searchStructureStacks(item)
    pyautogui.moveTo(1290, 280)
    pyautogui.click()
    for i in range(0, timesToPressA):
        pyautogui.press('a')
        sleep(0.25)

#searches the players ivnventory
def searchMyStacks(thing):# {{{
    checkTerminated()
    pyautogui.moveTo(144, 191)
    pyautogui.click()
    sleep(0.1)
    pyautogui.keyDown('ctrl')
    sleep(0.1)
    pyautogui.press('a')
    pyautogui.keyUp('ctrl')
    pyautogui.typewrite(thing, interval=0.02)
    sleep(0.1)


#searches a remote inventory
def searchStructureStacks(thing):
    checkTerminated()
    pyautogui.moveTo(1322, 191)
    pyautogui.click()
    sleep(0.1)
    pyautogui.keyDown('ctrl')
    sleep(0.1)
    pyautogui.press('a')
    pyautogui.keyUp('ctrl')
    pyautogui.typewrite(thing, interval=0.02)
    sleep(0.1)

def takeStacks(thing, count):# {{{
    checkTerminated()
    searchStructureStacks(thing)
    pyautogui.moveTo(1287, 290)
    pyautogui.click()
    for i in range(count):
        pyautogui.press('t')
        sleep(1)
# }}}
def takeAll(thing = ""):
    checkTerminated()
    if(thing != ""):
        sleep(0.1)
        pyautogui.moveTo(1285, 180)
        pyautogui.click()
        sleep(0.1)
        pyautogui.keyDown('ctrl')
        pyautogui.press('a')
        pyautogui.keyUp('ctrl')
        pyautogui.typewrite(thing, interval=0.01)
    pyautogui.moveTo(1424, 190)
    pyautogui.click()
    sleep(0.5)

def transferAll(thing = ""):# {{{
    checkTerminated()
    if(thing != ""):
        pyautogui.moveTo(198, 191)
        pyautogui.click()
        sleep(0.2)
        pyautogui.keyDown('ctrl')
        pyautogui.press('a')
        pyautogui.keyUp('ctrl')
        pyautogui.typewrite(thing, interval=0.005)
        sleep(0.1)
    pyautogui.moveTo(351, 186)
    pyautogui.click()
    sleep(0.1)

def transferStacks(thing, count):# {{{
    checkTerminated()
    pyautogui.moveTo(198, 191)
    pyautogui.click()
    sleep(0.1)
    pyautogui.keyDown('ctrl')
    pyautogui.press('a')
    pyautogui.keyUp('ctrl')
    pyautogui.typewrite(thing, interval=0.005)
    sleep(0.1)
    counter = 0
    pyautogui.moveTo(170, 280)
    pyautogui.click()
    sleep(0.2)
    while(counter < count):
        pyautogui.press('t')
        sleep(0.5)
        counter += 1

def openInventory(retries = 20):
    checkTerminated()
    pyautogui.press('f')
    sleep(0.2)
    count = 0
    while(inventoryIsOpen() == False):
        count += 1
        if(count > retries):
            return False
        sleep(0.1)
    while(receivingRemoteInventory()):
        time.sleep(0.5)

    return True


def tTransferTo(nRows):
    checkTerminated()
    sleep(0.5)
    pyautogui.moveTo(167, 280, 0.1)
    pyautogui.click()
    for j in range(nRows): #transfer a few rows back to the gacha
        for i in range(6):
            pyautogui.moveTo(167+(i*95), 280, 0.1)
            pyautogui.press('t')
            checkTerminated()

def tTransferFrom(nRows):
    checkTerminated()
    pyautogui.moveTo(1288, 280, 0.1)
    pyautogui.click()
    for j in range(nRows):
        for i in range(6):
            pyautogui.moveTo(1288+(i*95), 280, 0.05)
            pyautogui.press('t')
            checkTerminated()

def getBedScreenCoords():
    checkTerminated()
    roi = screen.getScreen()

    lower_blue = np.array([90,200,200])
    upper_blue = np.array([100,255,255])


    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    masked_template = cv2.bitwise_and(roi, roi, mask= mask)
    gray_roi = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)

    bed_template = cv2.imread('templates/bed_icon_template.png', cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(bed_template, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    masked_template = cv2.bitwise_and(bed_template, bed_template, mask= mask)
    bed_template = cv2.cvtColor(masked_template, cv2.COLOR_BGR2GRAY)


    res = cv2.matchTemplate(gray_roi, bed_template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if(max_val > 8000000):
        return (max_loc[0]+14, max_loc[1]+14)
    return None

def dropItems(thing):
    checkTerminated()
    pyautogui.moveTo(198, 191)
    pyautogui.click()
    sleep(0.2)
    pyautogui.keyDown('ctrl')
    pyautogui.press('a')
    pyautogui.keyUp('ctrl')
    if(thing == ""):
        pyautogui.press("backspace")
    else:
        pyautogui.typewrite(thing, interval=0.02)
    sleep(0.5)
    pyautogui.moveTo(412, 190)
    pyautogui.click()


def accessBed():
    checkTerminated()
    count = 0
    while(getBedScreenCoords() == None):
        lookDown()
        pyautogui.press('e')
        sleep(1.5)
        if(inventoryIsOpen()):
            closeInventory()
        count += 1
        if(count > 5):
            return False
    return True

def takeAllOverhead():
    checkTerminated()
    lookUp()
    openInventory()
    takeAll()
    closeInventory()
    lookDown()

def depositOverhead():
    checkTerminated()
    lookUp()
    pyautogui.press('e')
    lookDown()

def step(key, delay):
    checkTerminated()
    pyautogui.keyDown(key)
    sleep(delay)
    pyautogui.keyUp(key)

def crystalHotBarUse():
    for i in range(2, 10):
        pyautogui.press(str(i))
        sleep(0.05)
    pyautogui.press("0")
    sleep(0.1)

def harvestCropStack(fruit, lookUpTime=1.0):
    checkTerminated()
    lookDown()
    step('up', lookUpTime)

    for i in range(4):
        if(openInventory(80)):
            takeAll(fruit)
            transferAll()
            sleep(0.2)
            closeInventory()
        step('up', 0.09)

    pyautogui.press('c')
    step('down', 0.4)

    for i in range(3):
        if(openInventory(80)):
            takeAll(fruit)
            transferAll()
            sleep(0.2)
            closeInventory()
        step('up', 0.09)
    
    
            
    

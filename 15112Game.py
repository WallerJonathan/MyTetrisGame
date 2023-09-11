# Documentation: https://academy.cs.cmu.edu/docs
# Class syllabus: https://www.cs.cmu.edu/~112/syllabus.html
# Tetris pieces png: https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F5ca4b334-84bc-4c1d-abe6-c55b171c3fc5_689x362.png
from cmu_graphics import *
import random
import time # May not be used
import shelve

# Window settup
app.width = 4 * 150
app.height = 3 * 150
d = shelve.open("data")
app.background = d["background"]
d.close()
app.stepsPerSecond = 0.0000000000000000000000000000001 # Game won't start until start is clicked (0 doesn't work)
stepCounter = 0 # Counts the total number of steps taken
canUseButtons = False # Can the buttons be used (off when game is not playing)
noBugLineClear = True # Turns False to prevent any movement/bugs during line clearing

# Makes the game board, holds methods for the game board, stores basic game info
class gameBoard:
    grid = makeList(20, 10) # grid uses grid[y][x]
    nextBox = makeList(2, 4) # nextBox uses nextBox[y][x]
    level = 1 # The level the player is on (Levels 1 - 10)
    levelDisp = None # The level's display object
    scoreDisp = None # The score's display object
    highScoreDisp = None # The highscore's display object
    endScreen = None # The end screen object
    sButtonWord = None # The word in the start button
    score = 0 # The score of the player
    highScore = 0 # The highscore of the player
    lineCounter = 0 # Keeps track of the total lines cleared
    projectAuthor = None # The display for my name (Hooray!!!)
    directions = None # The game directions
    dropSpeed = [100, 85, 70, 60, 50, 40, 30, 20, 10, 7] # Contains the numbers that the stepCounter is modulated by
    bag = ["I", "T", "O", "Z", "S", "L", "J", "I", "T", "O", "Z", "S", "L", "J"] # The "bag" of tiles that can be drawn from

    def __init__(self):
        pass

    # Creates the board and returns the clickable buttons
    def create(self):
        # Creates the game's grid
        for row in range(len(self.grid)):  
            for col in range(len(self.grid[row])):
                self.grid[row][col] = Rect(col*20+25, row*20+25, 20, 20, fill="grey", border="black", borderWidth=0.5)
        
        # Creates the next box
        nextDisp = Group(
            Label("Next:", 245, 30, size=20, font="montserrat", fill="white", border="black", borderWidth=0.5, align="left-top"),
            Rect(240, 25, 100, 70, fill="white", border="black", borderWidth=0.5, opacity=20)
        )
        for row in range(len(self.nextBox)):
            for col in range(len(self.nextBox[row])):
                self.nextBox[row][col] = Rect(col*20+245, row*20+50, 20, 20, fill="white", border="black", borderWidth=0.5, opacity=0)
                nextDisp.add(self.nextBox[row][col])
        
        # Creates the start button
        sButton = Rect(525, 50, 100, 50, fill="steelBlue", border="black", borderWidth=1, align="center")
        self.sButtonWord = Label("Start", 525, 50, size=20, font="montserrat", fill="white", border="black", borderWidth=0.5)

        # Creates background buttons
        Group(
            Rect(240, 155, 335, 100, fill="white", opacity=20),
            Label("Backdrop Select", 245, 160, size=18, font="montserrat", fill="white", border="black", borderWidth=0.5, align="left-top") # Says backdrop to make the word fit
        )
        bButtA = Rect(245, 175, 4*25, 3*25, fill=gradient("navy", "indigo", "purple", start="left-top"), border="black")
        bButtB = Rect(357.5, 175, 4*25, 3*25, fill=gradient("darkRed", "orangeRed", "darkOrange", start="left-top"), border="black")
        bButtC = Rect(470, 175, 4*25, 3*25, fill=gradient("darkOliveGreen", "oliveDrab", "darkKhaki", start="left-top"), border="black")
        if app.background == bButtA.fill:
            bButtA.border = "white"
        elif app.background == bButtB.fill:
            bButtB.border = "white"
        else:
            bButtC.border = "white"

        # Creates the highscore display
        Label("Highscore:", 475, 80, size=18, font="montserrat", fill="white", italic=True, border="black", borderWidth=0.5, align="left-top")
        d = shelve.open("data")
        self.highScoreDisp = Label(str(d["hScore"]), 475, 100, size=18, font="montserrat", fill="white", italic=True, border="black", borderWidth=0.5, align="left-top")
        d.close()

        # Creates the directions
        self.directions = Group(
            Label("Directions:", 245, 325, size=18, font="montserrat", fill="white", border="black", borderWidth=0.5, align="left-top"),
            Label("Use the arrow keys to move and rotate the piece", 245, 345, size=14, font="montserrat", fill="white", border="black", bold=True, borderWidth=0.5, align="left-top"),
            Label("The level indicates the drop speed (up to 10)", 245, 365, size=14, font="montserrat", fill="white", border="black", bold=True, borderWidth=0.5, align="left-top"),
            Label("More lines cleared per turn means a higher score", 245, 385, size=14, font="montserrat", fill="white", border="black", bold=True, borderWidth=0.5, align="left-top"),
            Label("Try to reach a highscore; it will save!", 245, 405, size=14, font="montserrat", fill="white", border="black", bold=True, borderWidth=0.5, align="left-top")
        )

        # The displays for any misc items
        self.levelDisp = Label("Level "+str(self.level), 245, 100, size=24, font="montserrat", bold=True, fill="white", border="black", borderWidth=0.7, align="left-top")
        self.scoreDisp = Label("Score: "+str(self.score), 245, 130, size=18, font="montserrat", fill="white", italic=True, border="black", borderWidth=0.5, align="left-top")
        self.endScreen = Label("You Lose!", 125, 185, size=40, font="montserrat", fill="white", bold=True, border="black", borderWidth=1.2, align="center", opacity=0)
        self.projectAuthor = Group(
            Circle(407.5, 80, 50),
            Circle(407.5, 80, 42, fill="white"),
            Arc(407.5, 80, 68, 68, 135, 270),
            Circle(407.5, 80, 26, fill="white"),
            Label("2023", 440, 74, size=12, font="montserrat", fill="black", bold=True, align="right-bottom"),
            Label("Jonathan", 440, 80, size=12, font="montserrat", fill="black", align="right"),
            Label("Waller", 440, 86, size=12, font="montserrat", fill="black", align="right-top")
        )

        return sButton, bButtA, bButtB, bButtC

    # Displays the current piece position on the board (use this ONLY for the current piece)
    def display(self, thisBlock):
        # Sets the new sections of the block based on the center and get the old section positions
        oldSections = thisBlock.sections.copy()
        thisBlock.setSections()
        
        # Gets rid of the old spaces on the display
        for coord in oldSections:
            if coord[1] >= 0:
                self.grid[coord[1]][coord[0]].fill = "grey"
        
        # Displays the piece
        for coord in thisBlock.sections:
            if coord[1] >= 0:
                self.grid[coord[1]][coord[0]].fill = thisBlock.color # Grid uses grid[y][x]

    # Displays the next block in the next position
    def displayNext(self, thisBlock):
        for row in self.nextBox:
            for space in row:
                space.opacity = 0
        for coord in thisBlock.nextPosSections:
            self.nextBox[coord[1]][coord[0]].fill = thisBlock.color
            self.nextBox[coord[1]][coord[0]].opacity = 100

    # Updates level and score displays
    def displayUpdatedInfo(self):
        # For level updates
        self.levelDisp.opacity = 0
        self.levelDisp = Label("Level "+str(self.level), 245, 100, size=24, font="montserrat", bold=True, fill="white", border="black", borderWidth=0.7, align="left-top")
        # For score updates
        self.scoreDisp.opacity = 0
        self.scoreDisp = self.scoreDisp = Label("Score: "+str(self.score), 245, 130, size=18, font="montserrat", fill="white", italic=True, border="black", borderWidth=0.5, align="left-top")

    # Takes in how many lines were cleared and adds score based on that
    def updateScore(self, lineNum):
        if lineNum == 1:
            self.score = self.score + 100
        elif lineNum == 2:
            self.score = self.score + 250
        elif lineNum == 3:
            self.score = self.score + 500
        else:
            self.score = self.score + 1000

    # Updates the bag, resets if needed, and returns the tile it takes out
    def updateBag(self):
        # Refills the bag if needed
        if len(self.bag) == 0:
            self.bag = ["I", "T", "O", "Z", "S", "L", "J", "I", "T", "O", "Z", "S", "L", "J"].copy()
            print("New bag!!!") # REMOVE LATER!!!

        randInt = random.randint(0, len(self.bag)-1)
        return self.bag.pop(randInt)
    
    # Returns an array of row numbers if a line is full and must clear, returns an array with -1 otherwise
    def checkForLineClear(self):
        rowNum = 0
        lines = []

        for row in self.grid:
            count = 0
            for space in row:
                if space.fill != "grey":
                    count = count + 1
            if count == 10:
                lines.append(rowNum)
            rowNum = rowNum + 1
        if len(lines) > 0:
            return lines
        else:
            return [-1]

    # Clears the all lines (based on index) from lineNums and moves all other placed sections down
    def clearLines(self, lineNums):
        # No animation because time does not work with the app :(
        """for line in lineNums:
            for i in range(5):
                Rect(100, 100, 100, 100, fill="blue")
                self.grid[line][5+i].fill = "grey"
                self.grid[line][4-i].fill = "grey"
                now = time.time()
                later = now + 0.2
                print("now:", now, "\nlater:", later)
                while now < later:
                    now = time.time()"""

        # Moves all other lines down
        for line in lineNums:
            if line > 0:
                moving = line - 1
                while moving >= 0:
                    for mSection in range(10):
                        self.grid[moving+1][mSection].fill = self.grid[moving][mSection].fill
                        self.grid[moving][mSection].fill = "grey"
                    moving = moving - 1
    
    # Restarts everything controlled by the game board
    def resetBoard(self):
        # Resets vars
        self.level = 1
        self.score = 0
        self.levelDisp.value = "Level " + str(self.level)
        self.scoreDisp.value = "Score: " + str(self.score)
        self.endScreen.opacity = 0
        self.lineCounter = 0
        self.bag = ["I", "T", "O", "Z", "S", "L", "J", "I", "T", "O", "Z", "S", "L", "J"].copy()

        # Resets grid
        for row in self.grid:
            for box in row:
                box.fill = "grey"

# The parent block object (general block info, collision detection, and movement)
class block:
    rotation = 0 # 0 for original, 1 for 90 deg, 2 for 180 deg, 3 for 270 deg (using polar)
    centerX = 5 # 10 columns (0-9)
    centerY = 0 # 20 rows (0-19)
    sections = [[], [], [], []] # Sections of each block
    pieceSet = [[], [], [], []] # Contains the coordinates of the sections based on the rotation
    color = "NA" # The color of the block
    nextPosSections = [[], [], [], []] # Contains the coordinates if the block is in the next position
    hasMoved = False # Turns true if the block has moved (used to end the game)

    def __init__(self):
        pass

    # Checks if the NEXT move will be a hit, returns True if it is a hit
    def checkForHit(self, gameGrid):
        mustCheck = [] # Sections that are on the bottom and must have collision check

        # What sections have to check for hits?
        for i in range(4):
            current = self.sections[i]
            below = current.copy()
            below[1] = below[1] + 1
            isGood = True
            for comparison in self.sections:
                if comparison == below:
                    isGood = False
            if isGood:
                mustCheck.append(current)
        print("mustCheck (DOWN):", mustCheck) # REMOVE LATER!!!

        # Checks only the required sections for hits
        for sec in mustCheck:
            if sec[1] == 19: # Is any part at the bottom?
                return True
            if gameGrid[sec[1]+1][sec[0]].fill != "grey": # Checks if there is any placed blocks below ** Grid uses grid[y][x]
                return True
        return False

    # Checks if the next horizontal move is possible, returns True if it cannot move
    # OR if the key being checked IS NOT left or right
    def checkForSide(self, gameGrid, key):
        mustCheck = [] # Sections that are on a certain side and must have collision check

        # Prevents the method from running further if the key pressed is not right or left
        if key != "right" and key != "left":
            return True

        # What sections have to check for hits?
        if key == "right":
            directionVal = 1
        elif key == "left":
            directionVal = -1
        for i in range(4):
            current = self.sections[i]
            side = current.copy()
            side[0] = side[0] + directionVal
            isGood = True
            for comparison in self.sections:
                if comparison == side:
                    isGood = False
            if isGood:
                mustCheck.append(current)
        print("mustCheck (SIDE):", mustCheck) # REMOVE LATER!!!

        # Checking if the specific sections in mustCheck allow the piece to move
        for coord in mustCheck:
            if key == "left":
                if coord[0] == 0:
                    print(coord, 1)
                    return True
                elif gameGrid[coord[1]][coord[0]-1].fill != "grey" and coord[1] != -1:
                    print(coord, 3)
                    return True
            elif key == "right":
                if coord[0] == 9:
                    print(coord, 2)
                    return True
                elif gameGrid[coord[1]][coord[0]+1].fill != "grey" and coord[1] != -1:
                    print(coord, 4)
                    return True
            else:
                print(coord, "GOOD!")
        return False

    # Returns True if the piece can rotate based on the right side of the board without causing an error or bug
    def canRotateOnRight(self):
        if self.centerX == 9:
            return False
        else:
            return True
        
    # Returns True if the piece can rotate based on the left side of the board without causing an error or bug
    def canRotateOnLeft(self):
        if self.centerX == 0:
            return False
        elif self.centerX == 1 and self.color == "deepSkyBlue": # Moves it again if it is an I piece
            return False
        else:
            return True
        
    # Does the entire rotation sequence (rotation checks, corrections, and actual movement)
    def rotationSequence(self):
        currentSection = self.sections.copy() # A copy of the current sections
        nextSection = getNextRotationCoords() # The next section coordinates after the possible rotation
        # Makes nextSection into a list that only contains the spaces that will be filled (are not currently filled)
        for coordinate in currentSection:
            if coordinate in nextSection:
                nextSection.remove(coordinate)

        # Does all of the rotation checking
        print("For rotation checking (old centerX):", self.centerX) # REMOVE LATER!!!
        print("For rotation checking (new next coords if rotated):", nextSection) # REMOVE LATER!!!
        canRotate = True
        for coord in nextSection:
            try:
                if board.grid[coord[1]][coord[0]].fill != "grey" and coord[1] >= 0:
                    canRotate = False
            except:
                nextSection.remove(coord)
            print("canRotate:", canRotate)

        # Moves the block and rotates it so the game is easier and doesn't break
        if canRotate == True:
            print("ROTATES!") # REMOVE LATER!!!
            while not self.canRotateOnRight():
                self.moveLeft()
            while not self.canRotateOnLeft():
                self.moveRight()
            self.rotate()
        #elif :
        #    print("ROTATES!") # REMOVE LATER!!!
        else:
            print("DOESN'T ROTATE!") # REMOVE LATER!!!

    def moveDown(self):
        self.centerY = self.centerY + 1
        self.hasMoved = True

    def moveLeft(self):
        self.centerX = self.centerX - 1
        self.hasMoved = True
    
    def moveRight(self):
        self.centerX = self.centerX + 1
        self.hasMoved = True

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4
        self.hasMoved = True

# I piece object
class I(block):
    color = "deepSkyBlue"
    nextPosSections = [[0, 0], [1, 0], [2, 0], [3, 0]]

    def __init__(self):
        super().__init__()        
        self.setSections()

    # Sets all sections based on the current center
    def setSections(self):
        tempX = self.centerX
        tempY = self.centerY
        self.pieceSet = [
            [[tempX-2, tempY], [tempX-1, tempY], [tempX, tempY], [tempX+1, tempY]], # Horizontal
            [[tempX, tempY-1], [tempX, tempY], [tempX, tempY+1], [tempX, tempY+2]] # Vertical
        ]
        self.sections = self.pieceSet[self.rotation]
    
    def rotate(self):
        self.rotation = (self.rotation + 1) % 2

# T piece object
class T(block):
    color = "fuchsia"
    nextPosSections = [[1, 0], [0, 1], [1, 1], [2, 1]]

    def __init__(self):
        super().__init__()
        self.centerY = self.centerY + 1
        self.setSections()

    # Sets all sections based on the current center
    def setSections(self):
        tempX = self.centerX
        tempY = self.centerY
        self.pieceSet = [
            [[tempX, tempY-1], [tempX-1, tempY], [tempX, tempY], [tempX+1, tempY]], # Original
            [[tempX, tempY-1], [tempX, tempY], [tempX+1, tempY], [tempX, tempY+1]], # 90 deg
            [[tempX-1, tempY], [tempX, tempY], [tempX+1, tempY], [tempX, tempY+1]], # 180 deg
            [[tempX, tempY-1], [tempX-1, tempY], [tempX, tempY], [tempX, tempY+1]] # 270 deg
        ]
        self.sections = self.pieceSet[self.rotation]

# O piece object
class O(block):
    color = "gold"
    nextPosSections = [[0, 0], [1, 0], [0, 1], [1, 1]]

    def __init__(self):
        super().__init__()
        self.setSections()

    # Sets all sections based on the current center
    def setSections(self):
        tempX = self.centerX
        tempY = self.centerY
        self.sections = [[tempX-1, tempY], [tempX, tempY], [tempX-1, tempY+1], [tempX, tempY+1]]

    def rotate(self):
        pass

# Z piece object
class Z(block):
    color = "crimson"
    nextPosSections = [[0, 0], [1, 0], [1, 1], [2, 1]]

    def __init__(self):
        super().__init__()
        self.setSections()

    # Sets all sections based on the current center
    def setSections(self):
        tempX = self.centerX
        tempY = self.centerY
        self.pieceSet = [
            [[tempX-1, tempY], [tempX, tempY], [tempX, tempY+1], [tempX+1, tempY+1]], # Horizontal
            [[tempX, tempY-1], [tempX-1, tempY], [tempX, tempY], [tempX-1, tempY+1]] # Vertical
        ]
        self.sections = self.pieceSet[self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % 2

# S piece object
class S(block):
    color = "limeGreen"
    nextPosSections = [[1, 0], [2, 0], [0, 1], [1, 1]]

    def __init__(self):
        super().__init__()
        self.setSections()

    # Sets all sections based on the current center
    def setSections(self):
        tempX = self.centerX
        tempY = self.centerY
        self.pieceSet = [
            [[tempX+1, tempY], [tempX, tempY], [tempX, tempY+1], [tempX-1, tempY+1]], # Horizontal
            [[tempX, tempY-1], [tempX, tempY], [tempX+1, tempY], [tempX+1, tempY+1]] # Vertical
        ]
        self.sections = self.pieceSet[self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % 2

# L piece object
class L(block):
    color = "darkOrange"
    nextPosSections = [[2, 0], [0, 1], [1, 1], [2, 1]]

    def __init__(self):
        super().__init__()
        self.centerY = self.centerY + 1
        self.setSections()

    # Sets all sections based on the current center
    def setSections(self):
        tempX = self.centerX
        tempY = self.centerY
        self.pieceSet = [
            [[tempX+1, tempY-1], [tempX-1, tempY], [tempX, tempY], [tempX+1, tempY]], # Original
            [[tempX, tempY-1], [tempX, tempY], [tempX, tempY+1], [tempX+1, tempY+1]], # 90 deg
            [[tempX-1, tempY], [tempX, tempY], [tempX+1, tempY], [tempX-1, tempY+1]], # 180 deg
            [[tempX-1, tempY-1], [tempX, tempY-1], [tempX, tempY], [tempX, tempY+1]] # 270 deg
        ]
        self.sections = self.pieceSet[self.rotation]

# J piece object
class J(block):
    color = rgb(0, 70, 255)
    nextPosSections = [[0, 0], [0, 1], [1, 1], [2, 1]]

    def __init__(self):
        super().__init__()
        self.centerY = self.centerY + 1
        self.setSections()

    # Sets all sections based on the current center
    def setSections(self):
        tempX = self.centerX
        tempY = self.centerY
        self.pieceSet = [
            [[tempX-1, tempY-1], [tempX-1, tempY], [tempX, tempY], [tempX+1, tempY]], # Original
            [[tempX, tempY-1], [tempX+1, tempY-1], [tempX, tempY], [tempX, tempY+1]], # 90 deg
            [[tempX-1, tempY], [tempX, tempY], [tempX+1, tempY], [tempX+1, tempY+1]], # 180 deg
            [[tempX, tempY-1], [tempX, tempY], [tempX-1, tempY+1], [tempX, tempY+1]] # 270 deg
        ]
        self.sections = self.pieceSet[self.rotation]

# Picks a random block that is left in the "bag" (2 of each block in a bag) until a new bag is made
def pickRandomBlock():
    randLet = board.updateBag()
    if randLet == "I":
        return I()
    elif randLet == "T":
        return T()
    elif randLet == "O":
        return O()
    elif randLet == "Z":
        return Z()
    elif randLet == "S":
        return S()
    elif randLet == "L":
        return L()
    else:
        return J()

# Places the current block, makes the next block current, and makes a new next block
def placeBlock():
    global currBlock
    global nextBlock

    currBlock = nextBlock
    nextBlock = pickRandomBlock()
    board.displayNext(nextBlock)

# Function to easily clear the lines that must be cleared!
def clearTheLines():
    global board
    global noBugLineClear
    lines = board.checkForLineClear()

    if -1 not in lines:
        noBugLineClear = False
        holdStep = app.stepsPerSecond
        app.stepsPerSecond = 0.0000000000000000000000000000001
        board.clearLines(lines)
        board.lineCounter = board.lineCounter + len(lines)
        board.updateScore(len(lines))
        print("lineCounter:", board.lineCounter) # REMOVE LATER!!!
        print("scoreCounter:", board.score) # REMOVE LATER!!!
        app.stepsPerSecond = holdStep
        noBugLineClear = True

# Updates all relevant info including: score and level
def updateAllInfo():
    # Changes the level based on lines cleared and updates the level display
    if board.lineCounter >= 10 and board.level < 10:
        board.level = board.level + 1
        board.lineCounter = board.lineCounter % 10
    # Displays all updated info
    board.displayUpdatedInfo()

# Returns the piece's next section coordinates after a rotation
def getNextRotationCoords():
        currBlock.setSections() # Making sure pieceSet is updated to the current position
        # O piece is already blocked from anything rotation 
        if currBlock.rotation == 1 and (currBlock.color == "deepSkyBlue" or currBlock.color == "crimson" or currBlock.color == "limeGreen"): # I, Z, and S pieces
            return currBlock.pieceSet[0]
        elif currBlock.rotation == 3 and (currBlock.color == "fuchsia" or currBlock.color == "darkOrange" or currBlock.color == rgb(0, 70, 255)): # T, L, and J pieces
            return currBlock.pieceSet[0]
        else:
            return currBlock.pieceSet[currBlock.rotation+1]

# Returns True if the game should end (also does some of the end actions)
def endCheck():
    global canUseButtons
    global board
    global startButton

    if currBlock.hasMoved == False:
        app.stepsPerSecond = 0.0000000000000000000000000000001
        canUseButtons = False
        board.endScreen.opacity = 100
        board.sButtonWord.value = "Restart"
        startButton.opacity = 100

        # Saves the high score
        d = shelve.open("data")
        if board.score > d["hScore"]:
            d["hScore"] = board.score
            board.highScoreDisp.opacity = 0
            board.highScoreDisp = Label(str(board.score), 475, 100, size=18, font="montserrat", fill="white", italic=True, border="black", borderWidth=0.5, align="left-top")
        d.close()
        return True
    else:
        return False

# Does all placement actions and checks for loss
def placementSequence():
    if not endCheck():
        placeBlock()
        clearTheLines()
        board.display(currBlock)
        updateAllInfo()

# Sets the given background button's outline to white and changes all others back
def setBackgroundButtonOutline(button):
    global backButtonA
    global backButtonB
    global backButtonC

    backButtonA.border = "black"
    backButtonB.border = "black"
    backButtonC.border = "black"
    button.border = "white"

# Restarts the entire game
def restartGame():
    global board
    global currBlock
    global nextBlock
    board.resetBoard()
    currBlock = pickRandomBlock()
    nextBlock = pickRandomBlock()
    board.display(currBlock)
    board.displayNext(nextBlock)

# Code to reset the highscore
"""d = shelve.open("data")
d["hScore"] = 0
d.close()"""

# GAME START
board = gameBoard()
startButton, backButtonA, backButtonB, backButtonC = board.create()
currBlock = pickRandomBlock()
nextBlock = pickRandomBlock()

# Mouse Click
def onMousePress(mouseX, mouseY):
    global canUseButtons
    global noBugLineClear
    global board

    # When a button is clicked, do a thing
    if startButton.contains(mouseX, mouseY) and board.sButtonWord.value == "Start" and noBugLineClear:
        if canUseButtons == False:
            canUseButtons = True
            app.stepsPerSecond = 100
            board.displayNext(nextBlock)
            startButton.opacity = 70
    elif startButton.contains(mouseX, mouseY) and noBugLineClear:
        if canUseButtons == False:
            canUseButtons = True
            restartGame()
            app.stepsPerSecond = 100
            startButton.opacity = 70
    elif backButtonA.contains(mouseX, mouseY):
        app.background = backButtonA.fill
        setBackgroundButtonOutline(backButtonA)
    elif backButtonB.contains(mouseX, mouseY):
        app.background = backButtonB.fill
        setBackgroundButtonOutline(backButtonB)
    elif backButtonC.contains(mouseX, mouseY):
        app.background = backButtonC.fill
        setBackgroundButtonOutline(backButtonC)

    # Saving the perfered background
    d = shelve.open("data")
    d["background"] = app.background
    d.close()
            
# Key Hold (used for down)
# KEEP IN MIND: WILL DETECT OTHER KEY PRESSES EVEN IF THEY ARE NOT USEFUL FOR KEYHOLDING
def onKeyHold(key):
    global stepCounter
    global canUseButtons
    global noBugLineClear

    if canUseButtons and noBugLineClear:
        if "down" in key and stepCounter % 4 == 0:
            if currBlock.checkForHit(board.grid) == False:
                currBlock.moveDown()
                board.display(currBlock)
            else:
                placementSequence()

# Key Press (used for left, right, and rotate)
# KEEP IN MIND: WILL DETECT OTHER KEY PRESSES EVEN IF THEY ARE NOT USED FOR MOVEMENT
def onKeyPress(key):
    global canUseButtons
    global noBugLineClear

    # Block moving and rotating detection and execution
    if canUseButtons and noBugLineClear:
        # Moves blocks laterally if possible
        if not currBlock.checkForSide(board.grid, key):
            if key == "left":
                currBlock.moveLeft()
            elif key == "right":
                currBlock.moveRight()
        # Rotates blocks
        if key == "up" and currBlock.color != "gold":
            #app.stepsPerSecond = 0.00000000000000000000001 # For testing
            currBlock.rotationSequence()
        
        # Displays new board and excludes unwanted key
        if key != "down":
            board.display(currBlock)

# GAME RUN
def onStep():
    global stepCounter
    global board

    # Displays the board at the VERY START of the game
    if stepCounter == 0:
        board.display(currBlock)
    # Checks if the block has landed and moves/displays the piece
    if stepCounter % board.dropSpeed[board.level-1] == 0:
        if currBlock.checkForHit(board.grid):
            placementSequence()
        elif stepCounter != 0:
            currBlock.moveDown()
        board.display(currBlock)
    stepCounter = stepCounter + 1

cmu_graphics.run()

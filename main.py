import os
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import mediapipe as mp
import pyautogui
from utils import Controller


# Initialize mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Variables
width, height = pyautogui.size()
folderPath = "presentation"

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Get list of presentation images and sort them
pathImages = sorted(os.listdir(folderPath), key=lambda x: int(os.path.splitext(x)[0]))

# Variables
imgNumber = 0
hs, ws = int(120*1), int(213*1)
gesture_threshold = int(height / 2.5)
buttonPressed = False
buttonCounter = 0
buttonDelay = 15
annotations = [[]]
annotationNumber = 0
annotationStart = False

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    # Import images
    success, img = cap.read()
    img = cv2.flip(img, 1) # Flip the image in the horizontal direction
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    # Detecting hands
    hands, img = detector.findHands(img)
    cv2.line(img, (0, gesture_threshold), (width, gesture_threshold), (0, 255, 0), 10)

    if hands and buttonPressed is False:
        hand = hands[0] # Getting the first hand
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        lmList=hand['lmList']
 
        # Constrain values for easier drawing
        xVal = int(np.interp(lmList[8][0] , [width//2, width] , [0, w]))
        yVal = int(np.interp(lmList[8][1] , [150, height - 150] , [0, h]))
        indexFinger = xVal, yVal

        if cy <= gesture_threshold: # If hand is at the height of the face
            annotationStart = False

            # Gesture 1: go left 
            if fingers == [1, 0, 0, 0, 0]:
                annotationStart = False
                if imgNumber > 0:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber -= 1
                print("Left")
            
            # Gesture 2: go right 
            if fingers == [0, 0, 0, 0, 1]:
                annotationStart = False
                if imgNumber < len(pathImages) - 1:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgNumber += 1
                    print("Right")

            # Gesture 3: show pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger,12, (0, 0, 255), cv2.FILLED)
            annotationStart = False

            print("Point")

        # Gesture 4: draw pointer
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger,12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
            print("Draw")
        else:
            annotationStart= False

        # Gesture 5: erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                if annotationNumber >=0:
                    annotations.pop(-1) 
                    annotationNumber -=1
                    buttonPressed = True 
    else:
        annotationStart = False

    # Button pressed iterations
    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    for i in range (len(annotations)):
        for j in range(len(annotations[i])):
            if j!=0:
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0,0,200),12)

    # Adding webcam image on the slide
    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w-ws:w] = imgSmall # Overlay the image to fix the camera feed at top-right

    cv2.imshow("Slides", imgCurrent)

    if cv2.waitKey(1) & 0XFF == 27: # Press ESC to abort
        break


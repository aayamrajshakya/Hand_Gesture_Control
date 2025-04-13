import os
import argparse
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import mediapipe as mp
import pyautogui
from utils import Controller


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '--model',
        type=str,
        choices=['part1', 'part2'],
        default=None,
        help='type of gesture recognition model',
    )
    
    args, unknown = parser.parse_known_args()
    if len(unknown) > 0:
        for arg in unknown:
            print(f'Unknown argument: {arg}')
    
    if not args.model:
        parser.error("\033[1;31m You have to specify a model\033[0m")
    
    return args

def main() -> None:
    args = parse_arguments()

    # Global variables
    width, height = pyautogui.size()
    cap = cv2.VideoCapture(-1)      # Picks the first available webcam
    cap.set(cv2.CAP_PROP_FPS, 60)   # Sets the fps of the video input


    if args.model == 'part1':
        folderPath = "presentation"

        # Get list of presentation images and sort them
        pathImages = sorted(os.listdir(folderPath), key=lambda x: int(os.path.splitext(x)[0]))

        # Variables
        imgNumber = 0
        hs, ws = int(height / 10), int(width / 22)  # Webcam feed dimensions
        gestureThreshold = int(height / 5)
        buttonPressed = False
        buttonCounter = 0
        buttonDelay = 30
        annotations = [[]]
        annotationNumber = 0
        annotationStart = False

        # Hand detector
        detector = HandDetector(detectionCon=0.8, maxHands=1)

        while True:
            # Import images
            _, img = cap.read()
            img = cv2.flip(img, 1) # Flip the image in the horizontal direction
            pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
            imgCurrent = cv2.imread(pathFullImage)
            
            # Detecting hands
            hands, img = detector.findHands(img)
            cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

            if hands and buttonPressed is False:
                hand = hands[0]
                fingers = detector.fingersUp(hand)
                cx, cy = hand['center']
                lmList=hand['lmList']
        
                # Constrain values for easier drawing
                xVal = int(np.interp(lmList[8][0] , [width//4, width] , [0, 2.5*width]))
                yVal = int(np.interp(lmList[8][1] , [40, gestureThreshold-10] , [0, height]))
                indexFinger = xVal, yVal

                if cy <= gestureThreshold:
                    annotationStart = False

                    # Gesture 1: Go left 
                    if fingers == [1, 0, 0, 0, 0]:
                        print("Left")
                        annotationStart = False
                        if imgNumber > 0:
                            buttonPressed = True
                            annotations = [[]]
                            annotationNumber = 0
                            imgNumber -= 1
                    
                    # Gesture 2: Go right 
                    if fingers == [0, 0, 0, 0, 1]:
                        print("Right")
                        annotationStart = False
                        if imgNumber < len(pathImages) - 1:
                            buttonPressed = True
                            annotations = [[]]
                            annotationNumber = 0
                            imgNumber += 1

                    # Gesture 3: Show pointer
                if fingers == [0, 1, 1, 0, 0]:
                    print("Point")
                    cv2.circle(imgCurrent, indexFinger, 10, (0, 0, 255), cv2.FILLED)
                    annotationStart = False

                # Gesture 4: Draw pointer
                if fingers == [0, 1, 0, 0, 0]:
                    print("Draw")
                    if annotationStart is False:
                        annotationStart = True
                        annotationNumber += 1
                        annotations.append([])
                    cv2.circle(imgCurrent, indexFinger, 10, (0, 0, 255), cv2.FILLED)
                    annotations[annotationNumber].append(indexFinger)
                else:
                    annotationStart= False

                # Gesture 5: Erase
                if fingers == [0, 1, 1, 1, 0]:
                    if annotations:
                        if annotationNumber >= 0:
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

            # Attaching webcam feed
            webcamFeed = cv2.resize(img, (ws, hs))
            h, w, _ = imgCurrent.shape
            imgCurrent[h-hs:h, w-ws:w] = webcamFeed # Positioned to bottom-right

            # Maximize the screen
            cv2.namedWindow("Part 1", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Part 1", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Part 1", imgCurrent)
            if cv2.waitKey(1) & 0XFF == 27: # Press ESC to abort
                break

    if args.model == 'part2':

        # Initiliaze mediapipe
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        mp_drawing = mp.solutions.drawing_utils

        while True:
            _, img = cap.read()
            img = cv2.flip(img, 1)

            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(imgRGB)

            if results.multi_hand_landmarks:
                    Controller.hand_Landmarks = results.multi_hand_landmarks[0]
                    mp_drawing.draw_landmarks(img, Controller.hand_Landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    Controller.update_fingers_status()
                    Controller.cursor_moving()
                    Controller.detect_scrolling()
                    Controller.detect_zooming()
                    Controller.detect_clicking()
                    Controller.detect_dragging()

            cv2.imshow('Hand Tracker', img)
            if cv2.waitKey(1) & 0XFF == 27:
                break

if __name__ == '__main__':
    main()
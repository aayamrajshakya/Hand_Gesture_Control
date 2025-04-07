import os
import cv2
from cvzone.HandTrackingModule import HandDetector

#variables
width, height = 1280, 720
folderPath = "presentation"

#camera setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

#get list of presentation images and sort them
pathImages = sorted(os.listdir(folderPath), key=lambda x: int(os.path.splitext(x)[0]))

#variables
imgNumber = 0
hs, ws = int(120*1.2), int(213*1.2)
gesture_threshold = 300
buttonPressed = False
buttonCounter = 0
buttonDelay = 30 # 30 frames

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    #import images
    success, img = cap.read()
    img = cv2.flip(img, 1) # flip the image in the horizontal direction
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    # detecing hands
    hands, img = detector.findHands(img)
    cv2.line(img, (0, gesture_threshold), (width, gesture_threshold), (0, 255, 0), 10)

    if hands and buttonPressed is False:
        hand = hands[0] # getting the first hand
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']

        if cy <= gesture_threshold: #if hand is at the height of the face
            # gesture 1 => go left 
            if fingers == [1, 0, 0, 0, 0]:
                if imgNumber > 0:
                    buttonPressed = True
                    imgNumber -= 1
                print("left")
            
            # gesture 2 => go right 
            if fingers == [0, 0, 0, 0, 1]:
                if imgNumber < len(pathImages) - 1:
                    buttonPressed = True
                    imgNumber += 1
                    print("Right")

            # TODO: gesture 3 => show pointer

    #button pressed iterations
    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False


    # adding webcam image on the slide
    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w-ws:w] = imgSmall # Overlay the image to fix the camera feed at top-right

    cv2.imshow("Image", img)
    cv2.imshow("Slides", imgCurrent)

    key = cv2.waitKey(1)
    if key == ord('q'): # we break by pressing 'Q' on keyboard
        break

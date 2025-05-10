from cvzone.SerialModule import SerialObject
import cv2
import numpy

# final-> 1-45, 2-90, 3-135, 4-180, 5-ccw, 6-cw, square-7, circle-8
arduino = SerialObject("COM6")
cap = cv2.VideoCapture(1)
#img = cv2.imread("../TestImg/4objects.png") #remove when using cam
#img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

def empty(a):
    pass

# detection of red plaster to determine the square is flipped or placed correctly ( red plaster indicates the top face of the cube)
def is_red_present(img, contour):
    mask = numpy.zeros_like(img[:, :, 0])
    cv2.drawContours(mask, [contour], -1, 255, -1)

    masked_img = cv2.bitwise_and(img, img, mask=mask)
    hsv = cv2.cvtColor(masked_img, cv2.COLOR_BGR2HSV)

    # Define red ranges in HSV (covers red at 0-10 and 170-180)
    lower_red1 = numpy.array([0, 70, 50])
    upper_red1 = numpy.array([10, 255, 255])
    lower_red2 = numpy.array([170, 70, 50])
    upper_red2 = numpy.array([180, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = red_mask1 + red_mask2

    red_pixels = cv2.countNonZero(red_mask)
    return red_pixels > 200  # Tune this threshold based on test




def getContours(img,imgContour):
    squares=0
    circles=0
    prevarea=0
    px=0
    py=0
    contours,hierarchy = cv2.findContours(img,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area==0 or area<2000:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        objCor = len(approx)
        x, y, w, h = cv2.boundingRect(approx)
        differa=abs(area-prevarea)/area
        differx=abs(x-px)
        differy=abs(y-py)
        if differx<50 and differy<50 and differa<0.4:
            continue
        prevarea = area
        px=x
        py=y
        if x>60 and x<380 and y>60 and y<300:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 3)
            if objCor == 4:
                aspRatio = w / float(h)
                if 0.93 < aspRatio < 1.07:
                    objectType = "Square"
                    # Sort corners to find top edge
                    pts = approx.reshape((4, 2))
                    pts = sorted(pts, key=lambda x: x[1])  # Sort by y value

                    top_pts = sorted(pts[:2], key=lambda x: x[0])  # Left to right top
                    bottom_pts = sorted(pts[2:], key=lambda x: x[0])  # Left to right bottom

                    # Draw red top line
                    cv2.line(imgContour, top_pts[0], top_pts[1], (255, 255, 0), 2)

                    # Create a triangle mask on the top edge
                    triangle = numpy.array(
                        [top_pts[0], top_pts[1], ((top_pts[0][0] + top_pts[1][0]) // 2, top_pts[0][1] - 10)])
                    triangle = triangle.reshape((-1, 1, 2))

                    flipped = not is_red_present(imgContour, triangle)
                    if flipped:
                        print("Upside down square detected!")
                        arduino.sendData([10])  # Or any code you define to mean 'flip'
                else:
                    objectType = "Rectangle"
                squares += 1

            elif objCor>4:
                objectType= "Circle"
                circles=circles+1
            else:objectType="None"
            cv2.putText(imgContour, objectType,
                        (x + (w // 2) - 10, y + (h // 2) - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                        (0, 0, 0), 2)
    idobj = [squares, circles]
    return idobj

def most_frequent(List):
    unique, counts = numpy.unique(List, return_counts=True)
    index = numpy.argmax(counts)
    return unique[index]

def vision():
    counter = 0
    arduinolist = []
    while counter < 8:
        squarevals = []
        circlevals = []
        framesread = 0
        while framesread < 100:
            success, img = cap.read() #add when using cam
            imgContour = img.copy()
            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgBlur = cv2.GaussianBlur(imgGray, (9, 9), 0)
            # threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
            # threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
            threshold1 = 90
            threshold2 = 35
            imgCanny = cv2.Canny(imgBlur, threshold1, threshold2)
            kernel = numpy.ones((3, 3), )
            imgDilation = cv2.dilate(imgCanny, kernel, iterations=2)
            imgErosion = cv2.erode(imgDilation, kernel, iterations=2)
            idobj = getContours(imgErosion, imgContour)
            squarevals.append(idobj[0])
            circlevals.append(idobj[1])
            cv2.imshow("Image", imgContour)
            # cv2.imshow("ImageC", imgCanny)
            cv2.waitKey(1)
            framesread += 1
        cv2.destroyAllWindows()
        sqval = most_frequent(squarevals)
        circval = most_frequent(circlevals)
        if sqval == 2 and circval == 0:
            arduinolist.append("sb")
        elif sqval == 1 and circval == 0:
            arduinolist.append("sl")
        elif sqval == 0 and circval == 2:
            arduinolist.append("cb")
        elif sqval == 0 and circval == 1:
            arduinolist.append("cl")
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        counter += 1
        arduino.sendData([counter])
        cv2.waitKey(5)
        while True:
            go = arduino.getData()
            if go[0] == str(9-counter):
                go[0] = '0'
                break
    return arduinolist

def sorting(arduinolist):
    currentposition = len(arduinolist) - 1
    final = []
    if arduinolist[currentposition] in ("sl", "cl"):
        k = 1
        while k <= len(arduinolist):
            if arduinolist[(currentposition + k) % len(arduinolist)] in ("sb", "cb"):
                final.append(k)
                final.append(5)
                currentposition = (currentposition + k) % len(arduinolist)
                break
            elif arduinolist[(currentposition - (k) + len(arduinolist)) % len(arduinolist)] in ("sb", "cb"):
                final.append(k)
                final.append(6)
                currentposition = (currentposition - (k) + len(arduinolist)) % len(arduinolist)
                break
            k += 1
    else:
        final.append(0)
        final.append(0)
    j = 0
    passed = []
    while j < len(arduinolist) - 1:
        k = 1
        passed.append(currentposition)
        objtype = arduinolist[currentposition][0]
        if arduinolist[currentposition] in ("sb", "cb"):
            while k <= len(arduinolist):
                nextobject = arduinolist[(currentposition + k) % len(arduinolist)]
                if (currentposition + k) % len(arduinolist) in passed:
                    pass
                elif (nextobject == "sl" and objtype == "s") or (nextobject == "cl" and objtype == "c"):
                    final.append(k)
                    final.append(5)
                    if objtype == "s":
                        final.append(7)
                    elif objtype == "c":
                        final.append(8)
                    currentposition = (currentposition + k) % len(arduinolist)
                    break
                nextobject = arduinolist[(currentposition - (k) + len(arduinolist)) % len(arduinolist)]
                if (currentposition - (k) + len(arduinolist)) % len(arduinolist) in passed:
                    pass
                elif (nextobject == "sl" and objtype == "s") or (nextobject == "cl" and objtype == "c"):
                    final.append(k)
                    final.append(6)
                    if objtype == "s":
                        final.append(7)
                    elif objtype == "c":
                        final.append(8)
                    currentposition = (currentposition - (k) + len(arduinolist)) % len(arduinolist)
                    break
                k += 1
        elif arduinolist[currentposition] in ("sl", "cl"):
            while k <= len(arduinolist):
                nextobject = arduinolist[(currentposition + k) % len(arduinolist)]
                if (currentposition + k) % len(arduinolist) in passed:
                    pass
                elif nextobject in ("sb", "cb"):
                    final.append(k)
                    final.append(5)
                    currentposition = (currentposition + k) % len(arduinolist)
                    break
                nextobject = arduinolist[(currentposition - (k) + len(arduinolist)) % len(arduinolist)]
                if (currentposition - (k) + len(arduinolist)) % len(arduinolist) in passed:
                    pass
                elif nextobject in ("sb", "cb"):
                    final.append(k)
                    final.append(6)
                    currentposition = (currentposition - (k) + len(arduinolist) % len(arduinolist))
                    break
                k += 1
        j += 1
    return final

#cv2.namedWindow("Parameters")
#cv2.resizeWindow("Parameters",640,240)
#cv2.createTrackbar("Threshold1","Parameters",130,255,empty)
#cv2.createTrackbar("Threshold2","Parameters",20,255,empty)

while True:
    go = arduino.getData()
    if go[0]=='9':
        arduinolist=vision()
    arduinolist=["cb","sl","sl","cl","cb","sb","cl","sb"]
    print(arduinolist)
    final = sorting(arduinolist)
    print(final)
    cv2.waitKey(3000)
    arduino.sendData(final)
    cv2.waitKey(100)
    print("Done")
    while True:
        print(arduino.getData())
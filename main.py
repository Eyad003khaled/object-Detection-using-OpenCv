import cv2
import numpy as np

# Start webcam
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges
    edged = cv2.Canny(blurred, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # --- Initialize counters ---
    total_objects = 0
    square_count = 0
    circle_count = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 500:
            continue  # Ignore small noise

        # Approximate the contour
        approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
        perimeter = cv2.arcLength(cnt, True)

        if perimeter == 0:
            continue  # avoid division by zero

        # Calculate circularity
        circularity = 4 * np.pi * (area / (perimeter * perimeter))

        # Count this as a detected object
        total_objects += 1

        if len(approx) == 4:
            square_count += 1
            cv2.drawContours(frame, [approx], 0, (0, 255, 0), 3)
            x, y = approx.ravel()[0], approx.ravel()[1]
            cv2.putText(frame, 'Square', (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        elif 0.7 < circularity <= 1.2:
            circle_count += 1
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(frame, center, radius, (255, 0, 0), 3)
            cv2.putText(frame, 'Circle', (center[0] - 20, center[1] - radius - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # --- Display counters on the screen ---
    cv2.putText(frame, f'Total Objects: {total_objects}', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, f'Squares: {square_count}', (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f'Circles: {circle_count}', (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Show the frame
    cv2.imshow('Shapes Detection', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release everything
cap.release()
cv2.destroyAllWindows()

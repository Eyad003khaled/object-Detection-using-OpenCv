# 🎯 Shape Detection for Robotic Manipulation using OpenCV and Arduino

A real-time object detection system in Python using **OpenCV** that identifies and counts geometric shapes—**squares** and **circles**—through a webcam feed. This system is engineered for seamless integration with **Arduino/ESP32** and **PID-controlled robotic arms** for intelligent object manipulation.

---

## 📌 Overview

This project aims to demonstrate how **computer vision**, **embedded control systems**, and **robotic manipulation** can be combined to achieve a functional and intelligent robot capable of:

- Detecting and classifying geometric objects (squares and circles).
- Communicating object detection results to a microcontroller (Arduino or ESP32).
- Controlling a robotic arm with **PID-based precision** to physically interact with the detected objects using an **end-effector** (e.g., gripper or suction).

---

## 📷 Core Features

✅ Real-time webcam feed processing  
✅ Shape recognition via contour approximation and circularity metrics  
✅ Displays counts for total objects, squares, and circles  
✅ Shape annotation and classification in live video  
✅ Designed for integration with serial communication (Arduino/ESP32)  
✅ Intended to control robotic arm motion using PID feedback loop  

---

## 🔧 Technologies Used

| Component        | Description |
|------------------|-------------|
| Python 3.x       | Main development language |
| OpenCV           | Image processing and computer vision |
| NumPy            | Numerical operations and geometry |
| pySerial (optional) | Serial communication with Arduino or ESP32 |
| Arduino/ESP32    | Microcontroller to receive commands and control actuators |
| PID Control      | Ensures accurate arm positioning based on shape detection |

---

## 🤖 Robotic System Integration

This vision system is designed as a component of a **robotic sorting/manipulation system**, where:

- The Python code processes a camera feed and detects objects.
- The coordinates and shape types are sent to an Arduino via **serial communication**.
- The Arduino computes **PID corrections** and moves a **robotic arm** to interact with the object using an **end-effector**.

### 📡 Communication Protocol (example)

- Format: `"<shape>:<x>,<y>\n"`  
  Example: `circle:120,300\n`

- Serial Baud Rate: `9600` or `115200`  
- Python → Arduino via `pyserial`

---

## 🧠 How Detection Works

1. **Preprocessing**  
   - Convert to grayscale  
   - Apply Gaussian blur to reduce noise  
   - Use Canny edge detection for contour extraction

2. **Shape Classification**  
   - **Squares**: Detected using `cv2.approxPolyDP()` to identify 4-vertex polygons  
   - **Circles**: Determined using a circularity metric:  
     \[
     \text{Circularity} = \frac{4 \pi \cdot \text{Area}}{\text{Perimeter}^2}
     \]
     Thresholded to a value between `0.7` and `1.2`

3. **Output & Display**  
   - Each detected shape is outlined and labeled  
   - Total object count and individual shape counts are overlaid on the video feed

---

## 🖥️ System Requirements

- Python 3.7+
- Webcam
- Arduino Uno  (for integration)
- Robotic arm with actuator drivers (servo & stepper)
- End-effector (gripper)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Eyad003khaled/object-Detection-using-OpenCv.git

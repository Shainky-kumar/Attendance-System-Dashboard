import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from sklearn.neighbors import KNeighborsClassifier
from win32com.client import Dispatch
import sys

def speak(text):
    speaker = Dispatch("SAPI.SpVoice")
    speaker.Speak(text)

def log_attendance(name, timestamp, date):
    filename = f"Attendance/Attendance_{date}.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['NAME', 'TIME'])
        writer.writerow([name, timestamp])

# Setup
camera_source = sys.argv[1] if len(sys.argv) > 1 else "0"
video = cv2.VideoCapture(int(camera_source)) if camera_source.isdigit() else cv2.VideoCapture(camera_source)

if not video.isOpened():
    print("Error: Could not access the camera.")
    exit()

facedetect = cv2.CascadeClassifier(r'C:\Users\HP\Documents\Att project\data\haarcascade_frontalface_default.xml')

# Load data
try:
    with open(r'C:\Users\HP\Documents\Att project\data\names.pkl', 'rb') as w:
        LABELS = pickle.load(w)
    with open(r'C:\Users\HP\Documents\Att project\data\faces.pkl', 'rb') as f:
        FACES = pickle.load(f)

    LABELS = np.array(LABELS).flatten()
    if FACES.shape[0] != len(LABELS):
        raise ValueError("Mismatch between number of face samples and labels.")
except FileNotFoundError:
    print("Data files not found.")
    exit()

# Load today's already marked names
date_today = datetime.now().strftime("%d-%m-%Y")
attendance_file = f"Attendance/Attendance_{date_today}.csv"
confirmed_attendance = set()

if os.path.exists(attendance_file):
    with open(attendance_file, "r") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        for row in reader:
            if row:
                confirmed_attendance.add(row[0])

# Train model
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Background image
imgBackground = cv2.imread(r"C:\Users\HP\Videos\Att project\background.jpg")

# Start loop
while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to capture image")
        break

    # ✅ Resize frame to 640x480 to fit background area
    frame = cv2.resize(frame, (640, 480))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    recognized_name = None

    if len(faces) == 0:
        cv2.putText(frame, "Face Not Found", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
    else:
        for (x, y, w, h) in faces:
            crop_img = frame[y:y+h, x:x+w]
            resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)
            output = knn.predict(resized_img)
            recognized_name = output[0]

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
            cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
            cv2.putText(frame, recognized_name, (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)

    imgBackground[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow("Attendance System", imgBackground)

    k = cv2.waitKey(1)
    if k == ord('o') and recognized_name:
        if recognized_name not in confirmed_attendance:
            ts = time.time()
            date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
            timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            log_attendance(recognized_name, timestamp, date)
            confirmed_attendance.add(recognized_name)
            speak("Attendance Taken.")
        else:
            speak("Attendance already taken")
        time.sleep(2)
    elif k == ord('q'):
        break

video.release()
cv2.destroyAll
     
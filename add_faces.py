import cv2
import pickle
import numpy as np
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python add_faces.py <Name_ID> [camera_source]")
    sys.exit()

full_name = sys.argv[1]
camera_source = sys.argv[2] if len(sys.argv) > 2 else "0"
video = cv2.VideoCapture(int(camera_source)) if camera_source.isdigit() else cv2.VideoCapture(camera_source)

if not video.isOpened():
    print("Error: Could not access the camera.")
    sys.exit()

facedetect = cv2.CascadeClassifier(r'C:\Users\HP\Documents\Att project\data\haarcascade_frontalface_default.xml')

faces_data = []
frame_count = 0

while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to capture image")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        crop_img = frame[y:y + h, x:x + w]
        resized_img = cv2.resize(crop_img, (50, 50))

        if len(faces_data) < 100 and frame_count % 10 == 0:
            faces_data.append(resized_img)

        frame_count += 1

        cv2.putText(frame, f"Captured: {len(faces_data)}/100", (50, 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 1)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) == ord('q') or len(faces_data) == 100:
        break

video.release()
cv2.destroyAllWindows()

faces_data = np.asarray(faces_data).reshape(100, -1)
data_dir = r'C:\Users\HP\Documents\Att project\data'
os.makedirs(data_dir, exist_ok=True)

names_file = os.path.join(data_dir, 'names.pkl')
faces_file = os.path.join(data_dir, 'faces.pkl')

if os.path.exists(names_file) and os.path.exists(faces_file):
    with open(names_file, 'rb') as f:
        names = pickle.load(f)
    with open(faces_file, 'rb') as f:
        faces = pickle.load(f)

    names.extend([full_name] * 100)
    faces = np.append(faces, faces_data, axis=0)
else:
    names = [full_name] * 100
    faces = faces_data

with open(names_file, 'wb') as f:
    pickle.dump(names, f)
with open(faces_file, 'wb') as f:
    pickle.dump(faces, f)            
import cv2
import face_recognition
import pickle
import os
import sqlite3
from datetime import datetime
import pytz  # For timezone support

# Load known faces
known_encodings = []
known_roll_nos = []

for file in os.listdir('face_data'):
    if file.endswith('.pkl'):
        roll_no = file.replace('.pkl', '')
        with open(f'face_data/{file}', 'rb') as f:
            encoding = pickle.load(f)
            known_encodings.append(encoding)
            known_roll_nos.append(roll_no)

# Connect to database
conn = sqlite3.connect('database/attendance.db')
c = conn.cursor()

# Fetch roll_no to student_id mapping
c.execute("SELECT id, roll_no FROM students")
roll_to_id = {row[1]: row[0] for row in c.fetchall()}

# Timezone for correct time
tz = pytz.timezone('Asia/Kolkata')  # IST Time

# Start webcam
cap = cv2.VideoCapture(0)
marked_today = set()
today = datetime.now(tz).strftime("%Y-%m-%d")

print("Press 'q' to exit.")

while True:
    ret, frame = cap.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(rgb_frame)
    encodings = face_recognition.face_encodings(rgb_frame, faces)

    for face_encoding, face_location in zip(encodings, faces):
        # Compare with controlled tolerance
        tolerance = 0.45  
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=tolerance)
        distances = face_recognition.face_distance(known_encodings, face_encoding)

        if True in matches:
            best_match_index = distances.argmin()
            if matches[best_match_index]:
                roll_no = known_roll_nos[best_match_index]
                student_id = roll_to_id[roll_no]

                if (student_id, today) not in marked_today:
                    time_now = datetime.now(tz).strftime("%H:%M:%S")
                    c.execute("INSERT INTO attendance (student_id, date, time) VALUES (?, ?, ?)",
                              (student_id, today, time_now))
                    conn.commit()
                    marked_today.add((student_id, today))
                    print(f" Attendance marked for {roll_no} at {time_now}")

                # Draw rectangle and label
                top, right, bottom, left = face_location
                cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
                cv2.putText(frame, roll_no, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    cv2.imshow("Attendance System - Press 'q' to exit", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()

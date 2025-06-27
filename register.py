import cv2
import face_recognition
import pickle
import os
import sqlite3

# Ensure face_data folder exists
if not os.path.exists('face_data'):
    os.makedirs('face_data')

# Database connection
conn = sqlite3.connect('database/attendance.db')
c = conn.cursor()

# Get user details
name = input("Enter student's full name: ").strip()
roll_no = input("Enter roll number: ").strip()

# Check if roll number already exists
c.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,))
if c.fetchone():
    print("Roll number already exists. Use a different one.")
    conn.close()
    exit()

# Capture face
cap = cv2.VideoCapture(0)
print("Press 's' to capture face, 'q' to quit.")
face_encoding = None

while True:
    ret, frame = cap.read()
    cv2.imshow("Register - Press 's' to capture", frame)

    key = cv2.waitKey(1)
    if key == ord('s'):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb_frame)

        if faces:
            face_encoding = face_recognition.face_encodings(rgb_frame, faces)[0]
            print("Face captured.")
            break
        else:
            print("No face detected, try again.")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Save data
if face_encoding is not None:
    with open(f'face_data/{roll_no}.pkl', 'wb') as f:
        pickle.dump(face_encoding, f)

    c.execute("INSERT INTO students (name, roll_no) VALUES (?, ?)", (name, roll_no))
    conn.commit()
    print(f"Student '{name}' registered successfully.")
else:
    print("Face not captured, registration failed.")

conn.close()

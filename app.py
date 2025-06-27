from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import face_recognition
import sqlite3
import os
import pickle
import base64
from datetime import datetime

app = Flask(__name__)

if not os.path.exists('face_data'):
    os.makedirs('face_data')

DB_PATH = 'attendance.db'

# Ensure tables exist
with sqlite3.connect(DB_PATH) as conn:
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    roll_no TEXT UNIQUE NOT NULL
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    roll_no TEXT,
                    name TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )""")
    conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        name = request.form['name']
        roll_no = request.form['roll_no']
        img_data = request.form['image'].split(',')[1]

        # Check for existing roll number
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,))
            if c.fetchone():
                return jsonify({'status': 'fail', 'message': 'Roll number already exists. Use a different one.'})

        img_bytes = base64.b64decode(img_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, faces)

        if not encodings:
            return jsonify({'status': 'fail', 'message': 'No face detected. Try again.'})

        encoding = encodings[0]
        with open(f'face_data/{roll_no}.pkl', 'wb') as f:
            pickle.dump(encoding, f)

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO students (name, roll_no) VALUES (?, ?)", (name, roll_no))
            conn.commit()

        return jsonify({'status': 'success', 'message': 'Registration successful!'})

    except Exception as e:
        return jsonify({'status': 'fail', 'message': str(e)})

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.get_json()
        img_data = data['image'].split(',')[1]
        img_bytes = base64.b64decode(img_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, faces)

        if not encodings:
            return jsonify({'status': 'fail', 'message': 'No face detected. Please try again.'})

        known_encodings, known_names = [], []
        for file in os.listdir('face_data'):
            roll_no = os.path.splitext(file)[0]
            with open(f'face_data/{file}', 'rb') as f:
                known_encodings.append(pickle.load(f))
                known_names.append(roll_no)

        for encoding in encodings:
            matches = face_recognition.compare_faces(known_encodings, encoding)
            if True in matches:
                index = matches.index(True)
                roll_no = known_names[index]
                with sqlite3.connect(DB_PATH) as conn:
                    c = conn.cursor()
                    c.execute("SELECT name FROM students WHERE roll_no = ?", (roll_no,))
                    result = c.fetchone()
                    if result:
                        name = result[0]
                        c.execute("INSERT INTO attendance (roll_no, name) VALUES (?, ?)", (roll_no, name))
                        conn.commit()
                        return jsonify({'status': 'success', 'message': f'Welcome {name}, attendance marked!'})

        return jsonify({'status': 'fail', 'message': 'Face not recognized. Try again.'})

    except Exception as e:
        return jsonify({'status': 'fail', 'message': str(e)})

@app.route('/admin_data')
def admin_data():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT name, roll_no FROM students")
        students = [{'name': row[0], 'roll_no': row[1]} for row in c.fetchall()]

        c.execute("SELECT id, roll_no, name, timestamp FROM attendance ORDER BY timestamp DESC")
        attendance = [{'id': row[0], 'roll_no': row[1], 'name': row[2], 'timestamp': row[3]} for row in c.fetchall()]

    return jsonify({'students': students, 'attendance': attendance})

@app.route('/delete_student', methods=['POST'])
def delete_student():
    try:
        data = request.get_json()
        roll_no = data['roll_no']
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
            c.execute("DELETE FROM attendance WHERE roll_no = ?", (roll_no,))
            conn.commit()

        face_file = f'face_data/{roll_no}.pkl'
        if os.path.exists(face_file):
            os.remove(face_file)

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'fail', 'message': str(e)})

@app.route('/delete_attendance', methods=['POST'])
def delete_attendance():
    try:
        data = request.get_json()
        entry_id = data['id']
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM attendance WHERE id = ?", (entry_id,))
            conn.commit()

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'fail', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)

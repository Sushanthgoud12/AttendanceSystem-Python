# 🎯 Face Recognition Attendance System (Python + Flask + SQLite + HTML)

This project is a real-time attendance management system using Face Recognition. It allows:

✅ Student Registration with Face Capture  
✅ Attendance Marking via Face Detection  
✅ Admin Panel to View/Delete Records  

---

## 🚀 Tech Stack Used

- **Python** (Backend logic)  
- **Flask** (Web Server)  
- **face_recognition** (Face Detection & Encoding)  
- **OpenCV** (Camera Integration)  
- **SQLite** (Database)  
- **HTML, CSS, JavaScript** (Frontend UI)  

---

## 📁 Project Structure

AttendanceSystem/
├── app.py # Flask Application Backend
├── attendance.db # SQLite Database File
├── face_data/ # Stores Face Encodings (.pkl files)
├── templates/
│ └── index.html # Single Page UI for All Actions
├── requirements.txt # Project Dependencies
└── README.md # Project Documentation



---

## 🎨 Features

✅ New Student Registration with Face Capture  
✅ Attendance Checking with Face Matching  
✅ Admin Panel to View/Delete Students & Attendance Records  
✅ Modern Responsive User Interface  
✅ Attendance Records Stored with Date & Time  

---

## 🛠️ Setup Instructions
```bash

1️⃣ Clone the Repository
git clone https://github.com/yourusername/Attendance-System.git
cd Attendance-System
2️⃣ Install Dependencies
pip install -r requirements.txt
For timezone handling:
pip install pytz
3️⃣ Run the Application
python app.py
Visit:
http://127.0.0.1:5000/
🖥️ Application Pages
Home Page
New Student Registration | Attendance Checking | Admin Panel

Student Registration
➡ Enter Name & Roll No, Capture Face, Save to Database

Attendance Checking
➡ Capture Face, Matches with Registered Users, Marks Attendance

Admin Panel
➡ View Students & Attendance Records
➡ Delete Student or Attendance Data

💾 Database Details
SQLite file: attendance.db

Tables:

students (id, name, roll_no)

attendance (id, roll_no, name, date, time)

Face encodings stored in: face_data/ (per student .pkl file)

📦 Dependencies List
flask
opencv-python
face_recognition
numpy
pillow
pytz
📢 Future Improvements
Admin Login Authentication

Downloadable Attendance Reports

Multi-angle Face Registration

Enhanced Accuracy Controls

🏆 Credits
Face Recognition Library 

Flask Web Framework

⚡ License
This project is for educational/demo purposes. Customize and use as per your needs.

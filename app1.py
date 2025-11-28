import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime, timedelta
from fpdf import FPDF
import subprocess
import psutil
import csv

# Page configuration
st.set_page_config(page_title="SnapTend - Attendance System", page_icon="📷", layout="centered")

# Load CSS
def load_css():
    if os.path.exists("login_style.css"):
        with open("login_style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Admin credentials (Multi-admin support)
ADMIN_CREDENTIALS = {
    "admin": "048577",
    "admin2": "1234"
}

# Session state setup
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "camera_source" not in st.session_state:
    st.session_state.camera_source = "0"

# Login
def login():
    load_css()
    st.markdown("<h2 class='login-title'>Welcome to SnapTend Admin Login</h2>", unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")

        if login_btn:
            if username in ADMIN_CREDENTIALS and password == ADMIN_CREDENTIALS[username]:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.query_params["logged_in"] = "1"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

# Logout
def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.query_params["logged_in"] = "0"
        st.rerun()

# Add student
def add_student():
    st.header("➕ Register New Student")

    if "add_process" not in st.session_state:
        st.session_state.add_process = None

    name = st.text_input("Enter Student Name")
    student_id = st.text_input("Enter Student ID")
    cam_source = st.session_state.get("camera_source", "0").strip()

    if st.button("Start Camera to Add Student"):
        if name and student_id:
            full_name = name + "_" + student_id
            if not cam_source:
                st.error("Please configure the camera source first.")
            else:
                if st.session_state.add_process is None:
                    process = subprocess.Popen(["python", "add_faces.py", full_name, cam_source])
                    st.session_state.add_process = process
                    st.success("Camera started for student registration.")
                else:
                    st.warning("Camera for student registration is already running.")
        else:
            st.warning("Please enter both Name and Student ID.")

    if st.button("Stop Camera"):
        process = st.session_state.get("add_process")
        if process:
            try:
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                st.session_state.add_process = None
                st.success("Student registration camera stopped.")
            except Exception as e:
                st.error(f"Failed to stop camera: {e}")
        else:
            st.warning("Camera is not running.")

# Take attendance
def take_attendance():
    st.header("📸 Take Attendance")
    if "camera_process" not in st.session_state:
        st.session_state.camera_process = None

    cam_source = st.session_state.get("camera_source", "0").strip()

    if st.button("Start Camera for Attendance"):
        if not cam_source:
            st.error("Please configure the camera source first.")
        else:
            if st.session_state.camera_process is None:
                process = subprocess.Popen(["python", "test.py", cam_source])
                st.session_state.camera_process = process
                st.success("Camera started for attendance.")
            else:
                st.warning("Camera is already running.")

    if st.button("Stop Camera"):
        process = st.session_state.get("camera_process")
        if process:
            try:
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                st.session_state.camera_process = None
                st.success("Camera process stopped.")
            except Exception as e:
                st.error(f"Failed to stop camera: {e}")
        else:
            st.warning("Camera is not running.")

# Log attendance
def log_attendance(name, timestamp, date):
    filename = f"Attendance/Attendance_{date}.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['NAME', 'TIME'])
        writer.writerow([name, timestamp])

# View attendance record
def attendance_record():
    st.header("📑 Attendance Record")
    ts = time.time()
    today_date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")

    last_30_days = [datetime.now() - timedelta(days=i) for i in range(30)]
    all_records = []

    for day in last_30_days:
        date_str = day.strftime("%d-%m-%Y")
        filename = f"Attendance/Attendance_{date_str}.csv"
        if os.path.isfile(filename):
            df = pd.read_csv(filename)
            all_records.append((date_str, df))

    if all_records:
        st.subheader(f"Attendance Records for Last 30 Days")
        for date_str, df in all_records:
            st.subheader(f"Date: {date_str}")
            st.dataframe(df, use_container_width=True)

        if st.button("Delete All Attendance Records"):
            for date_str, _ in all_records:
                os.remove(f"Attendance/Attendance_{date_str}.csv")
            st.success("All attendance records deleted.")
    else:
        st.warning("No attendance records found for the past 30 days.")

# Camera configuration
def camera_configuration():
    st.header("🎛️ Camera Configuration")
    cam_type = st.radio("Select Camera", ["Webcam", "IP Camera"])
    ip_url = st.text_input("Enter IP Camera URL (e.g., http://192.168.89.77:4747/video)")

    if cam_type == "Webcam":
        st.session_state.camera_source = "0"
        st.success("Webcam selected.")
    elif ip_url.strip():
        st.session_state.camera_source = ip_url.strip()
        st.success("IP Camera configured.")
    else:
        st.warning("Please enter a valid IP Camera URL.")

# Main dashboard
def snap_tend_dashboard():
    st.title("📅 SnapTend Dashboard")
    st.sidebar.title("Navigation")
    logout_button()

    choice = st.sidebar.radio("Select Action", [
        "Take Attendance",
        "Add Student",
        "Attendance Record",
        "Camera Configuration"
    ])

    if choice == "Take Attendance":
        take_attendance()
    elif choice == "Add Student":
        add_student()
    elif choice == "Attendance Record":
        attendance_record()
    elif choice == "Camera Configuration":
        camera_configuration()

# Entry point
if st.session_state.logged_in:
    snap_tend_dashboard()
else:
    login() 
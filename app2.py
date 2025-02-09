import os
import time
import torch
import json
import io
import streamlit as st
from diffusers import StableDiffusionPipeline
from moviepy.editor import ImageSequenceClip
from PIL import Image
from authlib.integrations.requests_client import OAuth2Session

# ----------------------
# Page Configuration
# ----------------------
st.set_page_config(page_title="Cineo AI - Login", layout="centered")

# ----------------------
# Load Users from JSON
# ----------------------
USER_DB = "users.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

def authenticate_google():
    """ Placeholder for Google OAuth """
    st.info("Google Login is not yet implemented.")

def login_page():
    st.title("🔑 Login to Cineo AI")
    
    login_method = st.radio("Choose login method:", ["Username & Password", "Google"])
    
    if login_method == "Username & Password":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            users = load_users()
            if username in users and users[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password!")
    
    if login_method == "Google":
        if st.button("Login with Google"):
            authenticate_google()
    
    if st.button("Sign Up"):
        st.session_state["page"] = "signup"
        st.rerun()

def signup_page():
    st.title("📝 Sign Up for Cineo AI")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Create Account"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        else:
            users = load_users()
            if username in users:
                st.error("Username already exists!")
            else:
                users[username] = {"password": password, "credits": 1000, "subscription": "Free"}
                save_users(users)
                st.success("✅ Account created successfully! Please login.")
                st.session_state["page"] = "login"
                st.rerun()
    
    if st.button("Back to Login"):
        st.session_state["page"] = "login"
        st.rerun()

# ----------------------
# Page Navigation Handling
# ----------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "login"

if st.session_state["logged_in"]:
    st.success(f"Welcome, {st.session_state['username']}!")
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
else:
    if st.session_state["page"] == "login":
        login_page()
    elif st.session_state["page"] == "signup":
        signup_page()

# ---------------------------------------------------
# Cineo Model Selection
# ---------------------------------------------------
st.title("🎬 Cineo AI - Movie Generator")

cineo_option = st.radio(
    "Select your Cineo model:",
    ["Cineo 1.0", "Cineo 2.0", "Cineo Next-Gen AI", "Cineo Motion+"],
    horizontal=True
)

# ---------------------------------------------------
# Video Generation & Display
# ---------------------------------------------------
st.write("## 🎥 Generated Video")

video_path = "output.mp4"  # Replace with actual video path
video_buffer = io.BytesIO()

# Display video if available
try:
    with open(video_path, "rb") as f:
        video_buffer.write(f.read())
    video_buffer.seek(0)
    st.video(video_buffer)
except FileNotFoundError:
    st.warning("No video generated yet. Please generate a video first.")

# ---------------------------------------------------
# Prompt & Controls (Two-Line Layout)
# ---------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    prompt = st.text_area("🎭 Enter Your Prompt", "A futuristic city with flying cars and neon lights.")

with col2:
    use_negative_prompt = st.checkbox("Enable Negative Prompt")
    negative_prompt = st.text_area("❌ Negative Prompt", "No blur, no distortion") if use_negative_prompt else ""

# Generate Video Button
if st.button("🎥 Generate Video"):
    if st.session_state['credits'] < 40 and st.session_state['subscription'] != "Pro":
        st.error("Not enough credits! Upgrade to Pro or purchase more credits.")
    else:
        st.write("### Generating your video...")
        time.sleep(3)
        st.success("✅ Video generated successfully!")
        if st.session_state['subscription'] != "Pro":
            st.session_state['credits'] -= 40
            users[st.session_state["username"]]["credits"] = st.session_state['credits']
            save_users(users)

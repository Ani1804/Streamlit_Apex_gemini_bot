from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")


import streamlit as st
import os
import google.generativeai as genai
import streamlit.components.v1 as components
from datetime import datetime
import pytz
import requests
import base64

# --- Streamlit Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "bot_typing" not in st.session_state:
    st.session_state.bot_typing = False

# --- Background Image Function ---
def add_background(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Call the background function here ---
add_background("danfoss image.jpg")  # Ensure image is present in same folder

# --- Configure Gemini ---
genai.configure(api_key=os.getenv("AIzaSyC3IWoW_QvQ1WJRpZCHVZhH9sSL4475-4E"))
model = genai.GenerativeModel("models/gemini-1.5-flash")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    return chat.send_message(question, stream=True)

# --- Real-time Info ---
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).strftime("%A, %d %B %Y • %I:%M %p")

# --- Weather & News ---
def get_weather(city="Chennai"):
    api_key = os.getenv("35747c2e49855eabf921aa5801d936d5")
    if not api_key:
        return "Weather API key not found."
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={"chennai"}&appid={"35747c2e49855eabf921aa5801d936d5"}&units=metric"
    
    try:
        response = requests.get(url, timeout=10).json()
        if response.get("main"):
            temp = response["main"]["temp"]
            desc = response["weather"][0]["description"].title()
            return f"{city}: {temp}°C, {desc}"
        return "Weather data unavailable."
    except Exception as e:
        return f"Error fetching weather: {e}"



def get_top_news():
    url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=6636a8f3659b475382b502b56c9415d8&pageSize=3"
    response = requests.get(url).json()
    if response.get("articles"):
        headlines = [f"• {article['title']}" for article in response["articles"][:3]]
        return "\n".join(headlines)
    return "No news available."

# --- Page Config ---
st.set_page_config(page_title="APEX Bot", layout="centered")

# --- Theme Toggle ---
theme = st.radio("Choose Theme", ["Light", "Dark"], horizontal=True)

# --- Base CSS ---
base_css = f"""
    <style>
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            background: {'#f4f4f7' if theme == 'Light' else '#1e1e1e'};
            color: {'#000' if theme == 'Light' else '#fff'};
        }}
        .chat-box {{
            max-width: 400px;
            background: {'white' if theme == 'Light' else '#2a2a2a'};
            margin: 40px auto;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .chat-header {{
            background-color: #e53935;
            color: white;
            padding: 14px;
            display: flex;
            flex-direction: column;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .chat-body {{
            padding: 16px;
            max-height: 400px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }}
        .chat-message {{
            margin: 8px 0;
            padding: 10px 14px;
            border-radius: 20px;
            max-width: 80%;
            display: inline-block;
            line-height: 1.4;
            font-size: 14px;
            animation: fadeIn 0.5s ease-in-out;
        }}
        .bot-message {{
            background-color: {'#f1f0f0' if theme == 'Light' else '#333'};
            color: {'#000' if theme == 'Light' else '#eee'};
        }}
        .user-message {{
            background-color: #e53935;
            color: white;
            align-self: flex-end;
        }}
        .clear {{ clear: both; }}
        .typing-indicator {{
            display: inline-block;
            width: 60px;
            height: 20px;
            background: #f1f0f0;
            border-radius: 20px;
            padding: 5px 10px;
            position: relative;
            animation: blink 1.4s infinite;
        }}
        .typing-indicator::before {{
            content: 'Typing...';
            color: #555;
            font-size: 12px;
            position: absolute;
            top: 2px;
            left: 10px;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes blink {{
            0% {{ opacity: 0.2; }}
            50% {{ opacity: 1; }}
            100% {{ opacity: 0.2; }}
        }}
        .stTextInput > div > input {{
            font-size: 14px;
            padding: 10px;
            border-radius: 20px;
            background-color: {'#fff' if theme == 'Light' else '#444'};
            color: {'#000' if theme == 'Light' else '#fff'};
        }}
        .stButton > button {{
            background-color: #e53935;
            color: white;
            padding: 0.5em 1.2em;
            border-radius: 20px;
            border: none;
        }}
        .option-button {{
            border: 1px solid #e53935;
            color: #e53935;
            background: white;
            border-radius: 20px;
            padding: 6px 14px;
            margin: 6px;
        }}
        .option-button:hover {{
            background: #e53935;
            color: white;
        }}
        .message-timestamp {{
            display: block;
            font-size: 10px;
            color: #999;
            margin-top: 4px;
            text-align: right;
        }}
    </style>
"""
st.markdown(base_css, unsafe_allow_html=True)

# --- Fetch Live Info ---
weather = get_weather("Chennai")
news = get_top_news()

# --- Chat UI Box ---
st.markdown('<div class="chat-box">', unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="chat-header">
    <div style="display:flex; justify-content:space-between;">
        <span>🤖 APEX Bot</span>
        <span style="font-size:13px;"><span style="color:#4caf50;">●</span> Online</span>
    </div>
    <div style="font-size:12px;">{current_time}</div>
    <div style="font-size:13px;margin-top:6px;">🌤️<strong>Weather:</strong>{weather}</div>
    <div style="font-size:13px;margin-top:4px;"><strong>📰 News Headlines:</strong><br>{news.replace('\n', '<br>')}</div>
</div>
""", unsafe_allow_html=True)

# Welcome Message
if len(st.session_state.chat_history) == 0:
    st.markdown("""
       <div style="padding:12px; background:#fff3cd; border:1px solid #ffeeba; border-radius:12px; margin:20px; color:black;">
             👋 Hi! I’m APEX Bot. Ask me anything:
        </div>
        <div>
            <button class="option-button" onclick="document.getElementById('input').value='Tell me the weather';">Weather</button>
            <button class="option-button" onclick="document.getElementById('input').value='What’s in the news?';">News</button>
        </div>
    """, unsafe_allow_html=True)

# Chat Body
st.markdown('<div class="chat-body">', unsafe_allow_html=True)
for role, text in st.session_state.chat_history:
    is_user = role == "You"
    avatar_url = "https://cdn-icons-png.flaticon.com/512/4712/4712107.png" if not is_user else "https://cdn-icons-png.flaticon.com/512/4086/4086679.png"
    alignment = "flex-end" if is_user else "flex-start"
    bubble_class = "user-message" if is_user else "bot-message"

    st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: {alignment}; margin-bottom: 10px;">
            <img src="{avatar_url}" width="24" style="margin-bottom: 4px;">
            <div class="chat-message {bubble_class}">{text}</div>
            <span class="message-timestamp">{current_time}</span>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Typing Indicator
if st.session_state.bot_typing:
    st.markdown('<div class="typing-indicator"></div>', unsafe_allow_html=True)

# Input
user_input = st.text_input("Reply to APEX Bot...", key="input", placeholder="Type something...")
submit = st.button("Ask")

# --- Message Handler ---
if submit and user_input:
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.bot_typing = True
    with st.spinner("Thinking..."):
        response = get_gemini_response(user_input)
        full_response = ""
        for chunk in response:
            full_response += chunk.text
    st.session_state.bot_typing = False
    st.session_state.chat_history.append(("Bot", full_response))
    st.rerun()

# Feedback Prompt
if st.session_state.chat_history and st.session_state.chat_history[-1][0] == "Bot":
    st.markdown('<div style="text-align:right;">Was this helpful? </div>', unsafe_allow_html=True)

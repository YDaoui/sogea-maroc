import streamlit as st
import sqlite3
import bcrypt
import datetime
from datetime import date
from PIL import Image
import os
import base64
import pandas as pd

def get_base64_icon(image_path):
    try:
        full_path = os.path.join(os.path.dirname(__file__), image_path)
        with open(full_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode()
        return encoded_string
    except FileNotFoundError:
        st.error(f"Erreur : Fichier d'icône introuvable à '{image_path}'. Vérifiez le chemin.")
        return None
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'icône : {e}")
        return None

def display_logo(image_path, width=150):
    try:
        full_path = os.path.join(os.path.dirname(__file__), image_path)
        img = Image.open(full_path)
       
        st.markdown("<div style='display: flex; align-items: center; justify-content: center; height: 100%;'>", unsafe_allow_html=True)
        st.image(img, width=280)
        st.markdown("</div>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Erreur : Image introuvable à '{image_path}'. Vérifiez le chemin.")
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'image : {e}")

def setup_db():
    with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
        c = conn.cursor()
        
        c.execute("SELECT * FROM Users WHERE Username=?", ("Admin",))
        admin_user = c.fetchone()
        
        if not admin_user:
            hashed_pw = hash_password("Admin10")
            c.execute("INSERT INTO Users (Username, Password, FirstName_User, LastName_User, Email_User, Phone_User, CIN_User, Statut_User) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     ("Admin", hashed_pw, "Administrateur", "SOGEA", "admin@sogeamaroc.ma", "0000000000", "ADMIN001", "Administrateur"))
        
        conn.commit()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(plain_password, hashed_password):
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()
    return bcrypt.checkpw(plain_password.encode(), hashed_password)

def display_app_header(page_title):
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        if 'authenticated' in st.session_state and st.session_state.authenticated:
            try:
                full_path = os.path.join(os.path.dirname(__file__), "Images", "Corp.JPG")
                img = Image.open(full_path)
                st.markdown("<div style='display: flex; align-items: center; justify-content: center; height: 100%;'>", unsafe_allow_html=True)
                st.image(img, width=350)
                st.markdown("</div>", unsafe_allow_html=True)
            except FileNotFoundError:
                display_logo(os.path.join("Images", "SOGEA-MAROC.JPG"), width=100)
            except Exception as e:
                st.error(f"Erreur lors du chargement de Corp.JPG : {e}")
        else:
            display_logo(os.path.join("Images", "SOGEA-MAROC.JPG"), width=100)
    with col2:
        st.markdown(f"""
        <h1 style='color: #004890; font-weight: bold; border-bottom: 2px solid #EE1B2E; padding-bottom: 10px;'>
            {page_title}
        </h1>
        """, unsafe_allow_html=True)
    st.markdown("---")

def styled_subheader(text):
    st.markdown(f"""
    <h2 style='color: #004890; font-weight: bold; margin-top: 20px;'>
        {text}
    </h2>
    """, unsafe_allow_html=True)

def authenticate(login, password):
    try:
        with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM Users WHERE Username=?", (login,))
            user = c.fetchone()
            
            if user:
                stored_password = user[2]  
                if verify_password(password, stored_password):
                    return True, user[0]  
    except Exception as e:
        st.error(f"Erreur d'authentification : {e}")
    
    return False, None

def get_user_team(user_id):
    return "Administration"

def get_user_status(user):
    return user[9] if len(user) > 9 else "Utilisateur"

def get_user_name(user):
    first_name = user[3] if len(user) > 3 and user[3] else ""
    last_name = user[4] if len(user) > 4 and user[4] else ""
    if first_name and last_name:
        return f"{first_name} {last_name}"
    else:
        return user[1] if len(user) > 1 else "Utilisateur"

def apply_custom_styles():
    st.markdown("""
    <style>
        :root {
            --primary-dark: #000000;
            --secondary-red: #EE1B2E;
            --primary-blue: #004890;
            --light-blue: #4A7FB0;
            --off-white: #FFFFFF;
            --main-background: #F5F5F5;
            --light-gray: #E0E0E0;
        }

        html, body, [data-testid="stAppViewContainer"] {
            font-family: "Inter", sans-serif;
            background-color: var(--main-background);
            color: var(--primary-dark);
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-blue);
            font-weight: bold;
        }

        [data-testid="stSidebar"] {
            background-color: var(--primary-blue);
            color: var(--off-white);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 3px 0px 10px rgba(0, 0, 0, 0.3);
        }

        [data-testid="stSidebar"] .st-emotion-cache-1jm50x5 {
            display: none;
        }

        [data-testid="stSidebar"] .st-emotion-cache-10o4u29 {
            color: var(--off-white);
            font-weight: bold;
        }

        .stButton > button {
            background-color: var(--primary-blue);
            color: var(--off-white);
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            transition: background-color 0.3s ease, transform 0.2s ease;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
        }
        .stButton > button:hover {
            background-color: var(--light-blue);
            transform: translateY(-2px);
        }
        .stButton > button:active {
            background-color: var(--light-blue);
            transform: translateY(0);
            box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] .stButton {
            margin-bottom: 5px;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] .stButton > button {
            background-color: transparent;
            color: var(--off-white);
            border: none;
            border-radius: 0;
            padding: 12px 20px;
            text-align: left;
            box-shadow: none;
            transition: background-color 0.2s ease, color 0.2s ease;
            width: 100%;
            font-weight: bold;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] .stButton > button:hover {
            background-color: rgba(238, 27, 46, 0.3);
            color: var(--off-white);
            transform: none;
            border-left: 4px solid var(--secondary-red);
        }

        .stTextInput > div > div > input,
        .stDateInput > div > input,
        .stTimeInput > div > input,
        .stNumberInput > div > input {
            background-color: var(--off-white);
            color: var(--primary-dark);
            border: 1px solid var(--light-gray);
            border-radius: 8px;
            padding: 10px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
            font-weight: bold;
        }
        .stTextInput > div > div > input:focus,
        .stDateInput > div > input:focus,
        .stTimeInput > div > input:focus,
        .stNumberInput > div > input:focus {
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 2px rgba(0, 72, 144, 0.2);
            outline: none;
        }

        .stTextInput > label,
        .stDateInput > label,
        .stTimeInput > label,
        .stNumberInput > label,
        .stSelectbox > label {
            color: var(--primary-blue);
            font-weight: bold;
            margin-bottom: 5px;
            display: block;
        }

        .stSelectbox > div > div {
            background-color: var(--off-white);
            color: var(--primary-dark);
            border: 1px solid var(--light-gray);
            border-radius: 8px;
            padding: 5px;
            font-weight: bold;
        }
        .stSelectbox > div > div:focus {
            border-color: var(--primary-blue);
            box-shadow: 0 0 0 2px rgba(0, 72, 144, 0.2);
            outline: none;
        }
        .stSelectbox .st-emotion-cache-1dp5ifq {
            color: var(--primary-dark);
        }

        .streamlit-expander {
            background-color: var(--off-white);
            border: 1px solid var(--light-gray);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
            transition: box-shadow 0.3s ease;
        }
        .streamlit-expander:hover {
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.15);
        }
        .streamlit-expanderContent {
            color: var(--primary-dark);
            padding-top: 10px;
            font-weight: bold;
        }
        .streamlit-expanderHeader {
            color: var(--primary-blue);
            font-weight: bold;
            font-size: 1.1em;
        }

        .stAlert {
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            font-weight: bold;
        }
        .stAlert.info {
            background-color: rgba(0, 72, 144, 0.1);
            color: var(--primary-dark);
            border-left: 5px solid var(--primary-blue);
        }
        .stAlert.success {
            background-color: rgba(0, 72, 144, 0.1);
            color: var(--primary-dark);
            border-left: 5px solid var(--primary-blue);
        }
        .stAlert.error {
            background-color: rgba(238, 27, 46, 0.1);
            color: var(--primary-dark);
            border-left: 5px solid var(--secondary-red);
        }

        hr {
            border-top: 2px solid var(--light-gray);
            margin: 20px 0;
        }

        .st-emotion-cache-1c7y2qn, .st-emotion-cache-ocqkz7 {
            gap: 20px;
        }

        .st-emotion-cache-10q7q0o {
            background-color: var(--off-white);
            border: 1px solid var(--light-gray);
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }

        .info-card {
            background-color: var(--off-white);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 5px solid var(--primary-blue);
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        }

        .login-title {
            color: #004890;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
            font-size: 1.8em;
        }
        
        .login-error {
            background-color: rgba(238, 27, 46, 0.1);
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 12px;
            margin-top: 15px;
            text-align: center;
            font-weight: bold;
        }

        .stDataFrame {
            border: 1px solid var(--light-gray);
            border-radius: 10px;
            overflow: hidden;
        }
        
        .stDataFrame div[data-testid="stDataFrameResizable"] {
            border-radius: 10px;
        }

    </style>
    """, unsafe_allow_html=True)
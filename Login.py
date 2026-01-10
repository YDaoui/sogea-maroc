import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import bcrypt
import datetime
from datetime import date, datetime, timedelta  
import time
from PIL import Image
import os
import base64
import pandas as pd

from Css import applay_Css

import sys

   


from Utils import *


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
def show_login():
    
    applay_Css() 
    
   
    col1, col2, col3 = st.columns([1,5,1.8])

    with col1:
        st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
        display_logo(os.path.join("Images", "SOGEA-MAROC.JPG"), width=None)  # Sans limite
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.subheader("Page de connexion")
        login = st.text_input("Nom d'utilisateur : ", key="login_username")
        password = st.text_input("Mot de passe :", type="password", key="login_password")

        display_app_header("<div style='text-alignt: left")
        
        btn_col1, btn_col2 = st.columns(2)
        
        is_authenticated = False
        user_id = None
        
        with btn_col1:
            if st.button("Se connecter", key="login_button", use_container_width=True):
                is_authenticated, user_id = authenticate(login, password)
        
        if is_authenticated and user_id is not None:
            try:
                with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                    c = conn.cursor()
                    c.execute("SELECT * FROM Users WHERE ID_User=?", (user_id,))
                    user = c.fetchone()
                    
                    if user:
                        user_name = get_user_name(user)
                        user_statut = get_user_status(user)
                        user_service = get_user_service(user)
                        
                        # Initialisation propre de la session
                        st.session_state.clear()
                        st.session_state.update({
                            "authenticated": True,
                            "current_user": user,
                            "ID_User": user_id,
                            "Nom_Prenom": user_name,
                            "Statut": user_statut,
                            "Service": user_service,
                            "is_admin": user_service == "Admin",
                            "edit_mode": False,
                            "menu_selection": "profil"
                        })
                        
                        st.success(f"Connexion réussie en tant que {user_name}!")
                        time.sleep(0.5)
                        st.rerun()
            except Exception as e:
                st.error(f"Erreur base de données : {e}")
        elif not is_authenticated and st.session_state.get('login_button_clicked', False):
            st.error("Échec de l'authentification. Veuillez vérifier vos informations.")
        
        with btn_col2:
            if st.button("Annuler", key="cancel_button", use_container_width=True):
                st.info("Connexion annulée")
                st.rerun()

    with col3:
        pass


if __name__ == "__main__":
    setup_db()
    apply_custom_styles()
    show_login()

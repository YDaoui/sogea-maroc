import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils import *

def show_login():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.markdown("""
        <style>
            .stApp > div:first-child {
                background-color: white !important;
            }
            [data-testid="stAppViewContainer"] {
                background-color: white !important;
            }
            body {
                background-color: white !important;
            }
        </style>
        """, unsafe_allow_html=True)   
    
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        col1, col2, col3 = st.columns([1,5,1.8])

        with col1:
            st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
            display_logo(os.path.join("Images", "Corp.JPG"), width=280)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.subheader("Page de connexion")
            login = st.text_input("Nom d'utilisateur : ", key="login_username")
            password = st.text_input("Mot de passe :", type="password", key="login_password")
            
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                if st.button("Se connecter", key="login_button", use_container_width=True):
                    is_authenticated, user_id = authenticate(login, password)
                    
                    if is_authenticated:
                        try:
                            with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                                c = conn.cursor()
                                c.execute("SELECT * FROM Users WHERE ID_User=?", (user_id,))
                                user = c.fetchone()
                                
                                if user:
                                    user_team = get_user_team(user_id)
                                    user_status = get_user_status(user)
                                    user_name = get_user_name(user)
                                    
                                    st.session_state.update({
                                        "authenticated": True,
                                        "current_user": user,
                                        "ID_User": user_id,
                                        "Nom_Prenom": user_name,
                                        "Team": user_team, 
                                        "Statut": user_status,
                                        "is_admin": user_status == "Administrateur"
                                    })
                                    
                                    st.success(f"Connexion réussie en tant que {user_name}!")
                                    st.rerun()
                        except Exception as e:
                            st.error(f"Erreur base de données : {e}")
                    else:
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

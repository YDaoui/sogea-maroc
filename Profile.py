import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils import *

def show_profile():
    user = st.session_state.current_user

    st.markdown("""
    <div class='info-card'>
        <h3 style='color: var(--primary-blue); margin-top: 0;'>Informations de profil</h3>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Nom d'utilisateur :** {user[1]}")  
        st.write(f"**Prénom :** {user[3] if len(user) > 3 and user[3] else 'Non spécifié'}")  
        st.write(f"**Nom de famille :** {user[4] if len(user) > 4 and user[4] else 'Non spécifié'}")  
        st.write(f"**CIN :** {user[7] if len(user) > 7 and user[7] else 'Non spécifié'}")  
    with col2:
        st.write(f"**Statut :** {user[9] if len(user) > 9 else 'Utilisateur'}")  
        st.write(f"**Email :** {user[5] if len(user) > 5 and user[5] else 'Non spécifié'}")  
        st.write(f"**Téléphone :** {user[6] if len(user) > 6 and user[6] else 'Non spécifié'}") 

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    apply_custom_styles()
    display_app_header("Mon Profil")
    show_profile()
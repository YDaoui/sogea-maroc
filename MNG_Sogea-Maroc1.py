import streamlit as st
import os

from Utils import *

def main():
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        icon_path = os.path.join("Images", "Corp.JPG")
    else:
        icon_path = os.path.join("Images", "SOGEA-MAROC.JPG")
    
    icon_base64 = get_base64_icon(icon_path)
    if icon_base64:
        st.set_page_config(
            layout="wide",
            page_title="SOGEA-MAROC - Gestion",
            page_icon=f"data:image/x-icon;base64,{icon_base64}",
            initial_sidebar_state="expanded"
        )
    else:
        st.set_page_config(
            layout="wide",
            page_title="SOGEA-MAROC - Gestion",
            initial_sidebar_state="expanded"
        )

    setup_db()
    apply_custom_styles()

    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'menu_selection' not in st.session_state:
        st.session_state.menu_selection = "profile"
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

    if st.session_state.current_user is None:
        from Login import show_login
        show_login()
    else:
        user = st.session_state.current_user
        user_first_name = user[3] if len(user) > 3 and user[3] else ""
        user_last_name = user[4] if len(user) > 4 and user[4] else ""
        user_statut = get_user_status(user)
        
        # Déterminer les droits de l'utilisateur
        is_admin = user_statut == "Administrateur"
        is_data_user = user_statut == "DATA"  # Si vous avez un statut "DATA"
        
        # Mettre à jour le statut admin
        st.session_state.is_admin = is_admin
        
        if user_first_name and user_last_name:
            greeting = f"Bonjour M. {user_first_name} {user_last_name}"
        else:
            greeting = f"Bonjour {user[1] if len(user) > 1 else 'Utilisateur'}"
        
        st.sidebar.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: var(--off-white); font-size: 1.5em; font-weight: bold; 
                        border-bottom: 2px solid var(--secondary-red); padding-bottom: 10px;">
                {greeting}
            </h2>
            <p style="color: var(--off-white); font-size: 0.9em; margin: 5px 0;">
                {user_statut}
            </p>
            <p style="color: var(--off-white); font-size: 0.9em; margin-top: 0;">
                SOGEA-MAROC
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Définir les menus selon le statut
        menu_items = []
        
        # TOUS les utilisateurs ont accès au profil
        menu_items.append(("Mon Profil", "profile"))
        
        # Seuls les administrateurs ont accès à "Modifier le profil" et "Settings"
        if is_admin:
            menu_items.append(("Modifier le profil", "edit_profile"))
            menu_items.append(("Settings", "settings"))
        
        # Si vous avez un statut "DATA" qui doit voir tout
        elif is_data_user:
            menu_items.append(("Modifier le profil", "edit_profile"))
            menu_items.append(("Settings", "settings"))
        
        # Les utilisateurs normaux n'ont que "Mon Profil"
        
        # Afficher les boutons du menu
        for label, key_name in menu_items:
            if st.sidebar.button(label, key=f"menu_{key_name}"):
                st.session_state.menu_selection = key_name
                st.rerun()

        # Bouton de déconnexion pour tous
        if st.sidebar.button("Se déconnecter", key="sidebar_logout_btn"):
            st.session_state.current_user = None
            st.session_state.menu_selection = "profile"
            st.session_state.is_admin = False
            st.session_state.authenticated = False
            st.rerun()

        # Afficher la page sélectionnée
        if st.session_state.menu_selection == "profile":
            display_app_header("Mon Profil")
            from Profile import show_profile
            show_profile()
        elif st.session_state.menu_selection == "edit_profile":
            display_app_header("Modifier le profil")
            from EditProfile import show_edit_profile
            show_edit_profile()
        elif st.session_state.menu_selection == "settings":
            display_app_header("Gestion des utilisateurs")
            from Settings import show_settings
            show_settings()
        else:
            # Par défaut, afficher le profil
            display_app_header("Mon Profil")
            from Profile import show_profile
            show_profile()

if __name__ == "__main__":
    main()
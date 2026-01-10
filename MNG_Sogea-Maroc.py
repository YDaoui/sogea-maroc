import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import bcrypt
import datetime as dt  # Correction du conflit
from datetime import date, datetime, timedelta  
import time
from PIL import Image
import os
import base64
import pandas as pd
from io import BytesIO
from SOR import show_sor_page

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
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS EnergyTracking (
                ID_Tracking INTEGER PRIMARY KEY AUTOINCREMENT,
                Date_Tracking DATE NOT NULL,
                Type_Tracking TEXT NOT NULL,
                Categorie_Tracking TEXT NOT NULL,
                Quantite REAL NOT NULL,
                Unite TEXT NOT NULL,
                Cout REAL,
                Localisation TEXT,
                Observations TEXT,
                ID_User INTEGER,
                Date_Saisie TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ID_User) REFERENCES Users(ID_User)
            )
        ''')
        
        c.execute("PRAGMA table_info(Users)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'Service' not in columns:
            c.execute("ALTER TABLE Users ADD COLUMN Service TEXT")
        
        c.execute("SELECT * FROM Users WHERE Username=?", ("Admin",))
        admin_user = c.fetchone()
        
        if not admin_user:
            hashed_pw = hash_password("Admin10")
            c.execute("INSERT INTO Users (Username, Password, FirstName_User, LastName_User, Email_User, Phone_User, CIN_User, Statut_User, Service) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     ("Admin", hashed_pw, "Administrateur", "SOGEA", "admin@sogeamaroc.ma", "0000000000", "ADMIN001", "Administrateur", "Admin"))
        
        conn.commit()

def get_user_menu_items(user_service):
    """Retourne les éléments du menu selon le service de l'utilisateur"""
    
    base_menu = [
        ("  Profil", "profil"),
        ("  Se déconnecter", "logout")
    ]
    
    if user_service == "Admin":
        return [
            ("  Profil", "profil"),
            ("  Safety Observation Report", "sor"),
            ("  PréTask", "pretask"),
            ("  Energy Tracking", "energy_tracking"),
            ("  Settings", "settings"),
            ("  Se déconnecter", "logout")
        ]
    
    elif user_service == "HSE":
        return [
            ("  Profil", "profil"),
            ("  Safety Observation Report", "sor"),
            ("  PréTask", "pretask"),
            ("  Energy Tracking", "energy_tracking"),
            ("  Se déconnecter", "logout")
        ]
    
    else:
        return base_menu

def show_edit_form(user):
    """Affiche le formulaire d'édition du profil"""
    
    with st.form(key="profile_edit_form"):
        st.markdown("#### Modifier les informations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            CIN = st.text_input("CIN *", 
                                value=user[7] if len(user) > 7 else "", 
                                key="edit_profile_cin")
            username = st.text_input("Nom d'utilisateur *", 
                                    value=user[1],
                                    key="edit_profile_username")
            first_name = st.text_input("Prénom *", 
                                      value=user[3] if len(user) > 3 else "",
                                      key="edit_profile_first_name")
            last_name = st.text_input("Nom de famille *", 
                                     value=user[4] if len(user) > 4 else "",
                                     key="edit_profile_last_name")
        
        with col2:
            email = st.text_input("Email", 
                                 value=user[5] if len(user) > 5 else "",
                                 key="edit_profile_email")
            phone = st.text_input("Téléphone", 
                                 value=user[6] if len(user) > 6 else "",
                                 key="edit_profile_phone")
            
            current_service = user[10] if len(user) > 10 else "Utilisateur"
            service = st.selectbox(
                "Service",
                ["Utilisateur", "Admin", "HSE", "Production", "Maintenance", "Direction", "Finance", "RH"],
                index=["Utilisateur", "Admin", "HSE", "Production", "Maintenance", "Direction", "Finance", "RH"].index(current_service) 
                if current_service in ["Utilisateur", "Admin", "HSE", "Production", "Maintenance", "Direction", "Finance", "RH"] else 0,
                key="edit_profile_service"
            )
            
            current_statut = user[9] if len(user) > 9 else 'Utilisateur'
            if st.session_state.get('is_admin', False) or st.session_state.get('Service') == "Admin":
                statut = st.selectbox(
                    "Statut *",
                    ["Utilisateur", "Administrateur", "Chef.Chentier", "HSE", "Gestionnaire"],
                    index=["Utilisateur", "Administrateur", "Chef.Chentier", "HSE", "Gestionnaire"].index(current_statut) 
                    if current_statut in ["Utilisateur", "Administrateur", "Chef.Chentier", "HSE", "Gestionnaire"] else 0,
                    key="edit_profile_statut"
                )
            else:
                statut = current_statut
                st.text_input("Statut", value=statut, disabled=True)
        
        st.markdown("#### Changer le mot de passe")
        st.info("Laissez vide pour ne pas modifier le mot de passe")
        
        col_pass1, col_pass2 = st.columns(2)
        with col_pass1:
            new_password = st.text_input("Nouveau mot de passe", 
                                        type="password", 
                                        key="edit_profile_new_password",
                                        placeholder="Entrez un nouveau mot de passe")
        with col_pass2:
            confirm_password = st.text_input("Confirmer le mot de passe", 
                                            type="password", 
                                            key="edit_profile_confirm_password",
                                            placeholder="Confirmez le nouveau mot de passe")
        
        st.markdown("**Champs obligatoires ***")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            submitted = st.form_submit_button("💾 Enregistrer", 
                                             use_container_width=True)
        with col_btn2:
            canceled = st.form_submit_button("✖ Annuler", 
                                            use_container_width=True)
        
        if canceled:
            st.session_state.edit_mode = False
            st.session_state.selected_user_id = None
            st.session_state.selected_user_data = None
            st.rerun()
        
        if submitted:
            if not all([CIN, username, first_name, last_name]):
                st.error("Veuillez remplir tous les champs obligatoires (*)")
            elif new_password and new_password != confirm_password:
                st.error("Les mots de passe ne correspondent pas !")
            else:
                try:
                    with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                        c = conn.cursor()
                        
                        c.execute("""
                            UPDATE Users 
                            SET CIN_User=?, Username=?, FirstName_User=?, LastName_User=?, 
                                Email_User=?, Phone_User=?, Statut_User=?, Service=?
                            WHERE ID_User=?
                        """, (CIN, username, first_name, last_name, 
                              email, phone, statut, service, user[0]))
                        
                        if new_password:
                            hashed_password = hash_password(new_password)
                            c.execute("UPDATE Users SET Password=? WHERE ID_User=?", 
                                     (hashed_password, user[0]))
                        
                        conn.commit()
                        
                        c.execute("SELECT * FROM Users WHERE ID_User=?", (user[0],))
                        updated_user = c.fetchone()
                        st.session_state.current_user = updated_user
                        st.session_state.Nom_Prenom = get_user_name(updated_user)
                        st.session_state.Statut = statut
                        st.session_state.Service = service
                        st.session_state.is_admin = (service == "Admin")
                    
                    st.success(f"Profil mis à jour avec succès !")
                    st.session_state.edit_mode = False
                    st.session_state.selected_user_id = None
                    st.session_state.selected_user_data = None
                    st.rerun()
                    
                except sqlite3.IntegrityError as e:
                    if "CIN_User" in str(e) or "CIN" in str(e):
                        st.error("Ce CIN existe déjà dans la base de données !")
                    elif "Username" in str(e):
                        st.error("Ce nom d'utilisateur existe déjà !")
                    else:
                        st.error(f"Erreur d'intégrité : {e}")
                except Exception as e:
                    st.error(f"Erreur lors de la mise à jour : {e}")

def show_profile_info(user):
    """Affiche les informations du profil en lecture seule"""
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Nom d'utilisateur :** {user[1]}")  
        st.write(f"**Prénom :** {user[3] if len(user) > 3 and user[3] else 'Non spécifié'}")  
        st.write(f"**Nom de famille :** {user[4] if len(user) > 4 and user[4] else 'Non spécifié'}")  
        st.write(f"**CIN :** {user[7] if len(user) > 7 and user[7] else 'Non spécifié'}")  
    with col2:
        st.write(f"**Statut :** {user[9] if len(user) > 9 else 'Utilisateur'}")  
        st.write(f"**Service :** {user[10] if len(user) > 10 else 'Non spécifié'}")  
        st.write(f"**Email :** {user[5] if len(user) > 5 and user[5] else 'Non spécifié'}")  
        st.write(f"**Téléphone :** {user[6] if len(user) > 6 and user[6] else 'Non spécifié'}") 

    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; 
                border-left: 5px solid #004890; margin-top: 20px;'>
        <p style='color: #004890; font-weight: bold; margin: 0;'>
            Statut : Connecté • Dernière connexion : {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_user_management_section():
    """Section de gestion des utilisateurs pour les administrateurs"""
    
    st.markdown("###  Gestion des utilisateurs")
    
    if 'user_search_mode' not in st.session_state:
        st.session_state.user_search_mode = False
    if 'show_add_user_form' not in st.session_state:
        st.session_state.show_add_user_form = False
    
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    
    with col_opt1:
        if st.button(" Rechercher utilisateur", use_container_width=True):
            st.session_state.user_search_mode = True
            st.session_state.show_add_user_form = False
            st.rerun()
    
    with col_opt2:
        if st.button(" Ajouter utilisateur", use_container_width=True):
            st.session_state.show_add_user_form = True
            st.session_state.user_search_mode = False
            st.rerun()
    
    with col_opt3:
        if st.button(" Liste complète", use_container_width=True):
            st.session_state.user_search_mode = False
            st.session_state.show_add_user_form = False
            st.rerun()
    
    if st.session_state.user_search_mode:
        show_user_search_section()
    elif st.session_state.show_add_user_form:
        show_add_user_section()
    else:
        show_all_users_section()

def show_user_search_section():
    """Section de recherche d'utilisateurs"""
    
    st.markdown("#### Recherche d'utilisateur")
    
    col_search, col_action = st.columns([3, 1])
    
    with col_search:
        search_term = st.text_input(
            "Rechercher par CIN ou nom d'utilisateur :",
            placeholder="Ex: AB123456 ou john.doe",
            key="user_search_input"
        )
    
    with col_action:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        if st.button("🔍 Rechercher", key="search_user_button", use_container_width=True):
            if search_term:
                try:
                    with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                        c = conn.cursor()
                        
                        c.execute("""
                            SELECT * FROM Users 
                            WHERE CIN_User LIKE ? OR Username LIKE ? OR 
                                  FirstName_User LIKE ? OR LastName_User LIKE ?
                        """, (f"%{search_term}%", f"%{search_term}%", 
                              f"%{search_term}%", f"%{search_term}%"))
                        users = c.fetchall()
                        
                        if users:
                            st.session_state.search_results = users
                            st.session_state.show_search_results = True
                        else:
                            st.info(f"Aucun utilisateur trouvé pour : {search_term}")
                            st.session_state.show_search_results = False
                except Exception as e:
                    st.error(f"Erreur lors de la recherche : {e}")
    
    if 'search_results' in st.session_state and st.session_state.get('show_search_results', False):
        st.markdown("#### Résultats de la recherche")
        
        users_df = pd.DataFrame(
            st.session_state.search_results,
            columns=["ID", "Username", "Password", "FirstName", "LastName", 
                    "Email", "Phone", "CIN", "Team", "Statut", "Service"]
        )
        
        for idx, user in enumerate(st.session_state.search_results):
            with st.expander(f"{user[3]} {user[4]} - {user[1]} ({user[7]})"):
                col_info, col_action = st.columns([3, 1])
                
                with col_info:
                    st.write(f"**CIN :** {user[7]}")
                    st.write(f"**Email :** {user[5]}")
                    st.write(f"**Téléphone :** {user[6]}")
                    st.write(f"**Statut :** {user[9]}")
                    st.write(f"**Service :** {user[10] if len(user) > 10 else 'Non spécifié'}")
                
                with col_action:
                    if st.button("Modifier", key=f"edit_searched_{user[0]}", use_container_width=True):
                        st.session_state.edit_mode = True
                        st.session_state.selected_user_id = user[0]
                        st.session_state.selected_user_data = user
                        st.rerun()
        
        if st.button("Effacer les résultats", key="clear_search_results"):
            del st.session_state.search_results
            st.session_state.show_search_results = False
            st.rerun()

def show_add_user_section():
    """Section d'ajout d'un nouvel utilisateur"""
    
    st.markdown("#### Ajouter un nouvel utilisateur")
    
    if st.button("✖ Fermer", key="close_add_form"):
        st.session_state.show_add_user_form = False
        st.rerun()
    
    with st.form(key="add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            CIN = st.text_input("CIN *", 
                                placeholder="Ex: AB123456",
                                key="add_user_cin")
            username = st.text_input("Nom d'utilisateur *", 
                                    placeholder="Ex: john.doe",
                                    key="add_user_username")
            password = st.text_input("Mot de passe *", 
                                   type="password",
                                   placeholder="Mot de passe sécurisé",
                                   key="add_user_password")
            first_name = st.text_input("Prénom *", 
                                      placeholder="Ex: John",
                                      key="add_user_first_name")
            last_name = st.text_input("Nom de famille *", 
                                     placeholder="Ex: Doe",
                                     key="add_user_last_name")
        
        with col2:
            email = st.text_input("Email", 
                                 placeholder="Ex: john.doe@sogeamaroc.ma",
                                 key="add_user_email")
            phone = st.text_input("Téléphone", 
                                 placeholder="Ex: +212 6XXXXXXXX",
                                 key="add_user_phone")
            
            statut = st.selectbox(
                "Statut *",
                ["Utilisateur", "Administrateur", "Chef.Chentier", "HSE", "Gestionnaire"],
                key="add_user_statut"
            )
            
            service = st.selectbox(
                "Service *",
                ["Utilisateur", "Admin", "HSE", "Production", "Maintenance", "Direction", "Finance", "RH"],
                key="add_user_service"
            )
        
        st.markdown("**Champs obligatoires ***")
        
        col_submit, col_reset = st.columns(2)
        with col_submit:
            submitted = st.form_submit_button(" Enregistrer", 
                                             use_container_width=True)
        with col_reset:
            reset_button = st.form_submit_button(" Réinitialiser", 
                                                use_container_width=True)
        
        if reset_button:
            st.rerun()
        
        if submitted:
            if not all([CIN, username, password, first_name, last_name, statut, service]):
                st.error("Veuillez remplir tous les champs obligatoires (*)")
            else:
                try:
                    hashed_password = hash_password(password)
                    
                    with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                        c = conn.cursor()
                        c.execute("""
                            INSERT INTO Users 
                            (CIN_User, Username, Password, FirstName_User, LastName_User, 
                             Email_User, Phone_User, Statut_User, Service) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (CIN, username, hashed_password, first_name, last_name, 
                             email or "", phone or "", statut, service))
                        conn.commit()
                    
                    st.success(f"Utilisateur {username} créé avec succès !")
                    st.session_state.show_add_user_form = False
                    st.rerun()
                except sqlite3.IntegrityError as e:
                    if "CIN_User" in str(e):
                        st.error(f"Le CIN '{CIN}' existe déjà !")
                    elif "Username" in str(e):
                        st.error(f"Le nom d'utilisateur '{username}' existe déjà !")
                    else:
                        st.error(f"Erreur d'intégrité : {e}")
                except Exception as e:
                    st.error(f"Erreur lors de la création : {e}")

def show_all_users_section():
    """Affiche la liste complète des utilisateurs"""
    
    st.markdown("####  Liste des utilisateurs")
    
    try:
        with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
            c = conn.cursor()
            c.execute("SELECT ID_User, CIN_User, Username, FirstName_User, LastName_User, Email_User, Phone_User, Statut_User, Service FROM Users")
            all_users = c.fetchall()
        
        if all_users:
            users_df = pd.DataFrame(
                all_users,
                columns=["ID", "CIN", "Nom d'utilisateur", "Prénom", "Nom", "Email", "Téléphone", "Statut", "Service"]
            )
            
            st.markdown(f"**Total des utilisateurs :** {len(users_df)}")
            
            for user in all_users:
                with st.expander(f"{user[3]} {user[4]} - {user[2]} ({user[7]})"):
                    col_info, col_action = st.columns([3, 1])
                    
                    with col_info:
                        st.write(f"**CIN :** {user[1]}")
                        st.write(f"**Email :** {user[5]}")
                        st.write(f"**Téléphone :** {user[6]}")
                        st.write(f"**Statut :** {user[7]}")
                        st.write(f"**Service :** {user[8] if len(user) > 8 else 'Non spécifié'}")
                    
                    with col_action:
                        if st.button("Modifier", key=f"edit_{user[0]}", use_container_width=True):
                            st.session_state.edit_mode = True
                            st.session_state.selected_user_id = user[0]
                            st.session_state.selected_user_data = user
                            st.rerun()
            
            col_stat1, col_stat2 = st.columns(2)
            
            with col_stat1:
                st.markdown("##### Répartition par service")
                if not users_df["Service"].empty:
                    service_counts = users_df["Service"].value_counts()
                    for service_name, count in service_counts.items():
                        st.write(f"**{service_name}** : {count} utilisateur(s)")
            
            with col_stat2:
                st.markdown("##### Export des données")
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    users_df.to_excel(writer, index=False, sheet_name='Utilisateurs')
                excel_data = output.getvalue()
                
                st.download_button(
                    label=" Télécharger la liste (Excel)",
                    data=excel_data,
                    file_name="users_sogea_maroc.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_users_list"
                )
                
        else:
            st.info("Aucun utilisateur trouvé dans la base de données.")
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des utilisateurs : {e}")

def show_settings():
    """Page Settings"""
    display_app_header("Gestion des utilisateurs")
    
    # Vérification directe du service
    user_service = st.session_state.get('Service', '')
    if user_service != "Admin":
        st.error("⚠️ Vous n'avez pas accès à cette fonctionnalité.")
        st.info("Cette fonctionnalité est réservée au service Admin.")
        return
    
    show_user_management_section()

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

def get_user_status(user):
    return user[9] if len(user) > 9 else "Utilisateur"

def get_user_service(user):
    """Récupère le service de l'utilisateur"""
    if len(user) > 10:
        service = user[10]
        if service is not None and str(service).strip():
            return str(service).strip()
    return "Utilisateur"

def get_user_name(user):
    first_name = user[3] if len(user) > 3 and user[3] else ""
    last_name = user[4] if len(user) > 4 and user[4] else ""
    if first_name and last_name:
        return f"{first_name} {last_name}"
    else:
        return user[1] if len(user) > 1 else "Utilisateur"

def show_login():
    col1, col2,col3 = st.columns([1,3,7])
    with col1:
        pass
    with col2:
        st.markdown("<div style='display: flex; align-items: flex-start; justify-content: center; height: 100%; padding-top: 20px;'>", unsafe_allow_html=True)
        display_logo(os.path.join("Images", "SOGEA-MAROC.JPG"), width=600)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        login = st.text_input("Nom d'utilisateur : ", key="login_username")
        password = st.text_input("Mot de passe :", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
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
                else:
                    st.error("Identifiant ou mot de passe incorrect")
        
        with col_btn2:
            if st.button("Annuler", key="cancel_button", use_container_width=True):
                st.info("Connexion annulée")
                st.rerun()

def show_profile_page():
    """Page Profil unique qui combine affichage et modification"""
    
    display_app_header("Profil")
    
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'selected_user_id' not in st.session_state:
        st.session_state.selected_user_id = None
    if 'selected_user_data' not in st.session_state:
        st.session_state.selected_user_data = None
    
    user = st.session_state.current_user
    
    col_title, col_btn = st.columns([4, 1])
    
    with col_title:
        st.markdown("### Informations du profil")
    
    with col_btn:
        if st.session_state.edit_mode:
            if st.button(" Annuler", key="cancel_edit_button", use_container_width=True):
                st.session_state.edit_mode = False
                st.session_state.selected_user_id = None
                st.session_state.selected_user_data = None
                st.rerun()
        else:
            if st.button(" Modifier", key="edit_profile_button", use_container_width=True):
                st.session_state.edit_mode = True
                st.session_state.selected_user_id = user[0]
                st.session_state.selected_user_data = user
                st.rerun()
    
    if st.session_state.edit_mode:
        show_edit_form(user)
    else:
        show_profile_info(user)
        
        # Afficher la gestion des utilisateurs seulement pour les admins
        if st.session_state.get('is_admin', False):
            show_user_management_section()

def show_energy_tracking_page():
    """Page de suivi énergétique"""
    display_app_header("Suivi Énergétique")

    # Vérification directe du service
    user_service = st.session_state.get('Service', '')
    if user_service not in ["Admin", "HSE"]:
        st.error("⚠️ Vous n'avez pas accès à cette fonctionnalité.")
        st.info("Cette fonctionnalité est réservée aux services Admin et HSE.")
        return
    
    tab1, tab2, tab3 = st.tabs([" Carburant         ", " Eau ", " Électricité"])
    
    with tab1:
        show_fuel_tracking()
    
    with tab2:
        show_water_tracking()
    
    with tab3:
        show_electricity_tracking()

def show_water_tracking():
    """Onglet de suivi de l'eau"""
    st.markdown("### Suivi de la consommation d'eau")
    
    water_tab1, water_tab2, water_tab3, water_tab4 = st.tabs([
        " Saisie des données", 
        " Visualisation", 
        " Historique", 
        " Statistiques"
    ])
    
    with water_tab1:
        show_water_data_entry()
    
    with water_tab2:
        show_water_visualization()
    
    with water_tab3:
        show_water_history()
    
    with water_tab4:
        show_water_statistics()

def show_water_data_entry():
    """Formulaire de saisie des données eau"""
    st.markdown("#### Saisir une nouvelle consommation d'eau")
    
    with st.form(key="water_entry_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date_tracking = st.date_input("Date de la consommation", value=datetime.now())
            type_water = st.selectbox(
                "Type d'eau *",
                ["Eau potable", "Eau usée", "Eau recyclée"],
                key="water_type"
            )
            quantity = st.number_input("Quantité *", min_value=0.0, step=0.1, format="%.2f")
            unit = st.selectbox("Unité *", ["m³", "L", "m³/jour", "L/jour"])
        
        with col2:
            cost = st.number_input("Coût (DH)", min_value=0.0, step=0.1, format="%.2f")
            location = st.text_input("Localisation (chantier/bâtiment)")
            observations = st.text_area("Observations")
        
        col_submit, col_reset = st.columns(2)
        
        with col_submit:
            submitted = st.form_submit_button(" Enregistrer", use_container_width=True)
        
        with col_reset:
            reset = st.form_submit_button(" Réinitialiser", use_container_width=True)
        
        if submitted:
            if quantity <= 0:
                st.error("La quantité doit être supérieure à 0")
            else:
                try:
                    with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                        c = conn.cursor()
                        c.execute("""
                            INSERT INTO EnergyTracking 
                            (Date_Tracking, Type_Tracking, Categorie_Tracking, Quantite, Unite, Cout, Localisation, Observations, ID_User)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            date_tracking, 
                            "Eau", 
                            type_water,
                            quantity, 
                            unit,
                            cost if cost > 0 else None,
                            location if location else None,
                            observations if observations else None,
                            st.session_state.ID_User
                        ))
                        conn.commit()
                    
                    st.success(f" Consommation d'eau ({type_water}) enregistrée avec succès !")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Erreur lors de l'enregistrement : {e}")

def show_water_visualization():
    """Visualisation des données eau"""
    st.markdown("#### Visualisation de la consommation d'eau")
    
    try:
        with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
            query = """
                SELECT Date_Tracking, Categorie_Tracking, SUM(Quantite) as Total_Quantite
                FROM EnergyTracking 
                WHERE Type_Tracking = 'Eau' 
                    AND Date_Tracking >= date('now', '-30 days')
                GROUP BY Date_Tracking, Categorie_Tracking
                ORDER BY Date_Tracking
            """
            df = pd.read_sql_query(query, conn)
        
        if not df.empty:
            df['Date_Tracking'] = pd.to_datetime(df['Date_Tracking'])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            categories = df['Categorie_Tracking'].unique()
            colors = {'Eau potable': '#004890', 'Eau usée': '#EE1B2E', 'Eau recyclée': '#00A859'}
            
            for category in categories:
                category_data = df[df['Categorie_Tracking'] == category]
                ax.plot(category_data['Date_Tracking'], category_data['Total_Quantite'], 
                       marker='o', label=category, color=colors.get(category, '#000000'), linewidth=2)
            
            ax.set_xlabel('Date', fontweight='bold')
            ax.set_ylabel('Quantité (m³/L)', fontweight='bold')
            ax.set_title('Consommation d\'eau sur les 30 derniers jours', fontweight='bold', fontsize=14)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
            
            st.markdown("##### Détails par type d'eau")
            pivot_df = df.pivot_table(
                index='Date_Tracking', 
                columns='Categorie_Tracking', 
                values='Total_Quantite',
                aggfunc='sum'
            ).fillna(0)
            
            st.dataframe(pivot_df, use_container_width=True)
            
        else:
            st.info("Aucune donnée de consommation d'eau disponible pour les 30 derniers jours.")
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")

def show_water_history():
    """Historique des consommations d'eau"""
    st.markdown("#### Historique des consommations d'eau")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input("Date début", value=datetime.now() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("Date fin", value=datetime.now())
    
    with col3:
        water_type_filter = st.selectbox(
            "Type d'eau",
            ["Tous", "Eau potable", "Eau usée", "Eau recyclée"]
        )
    
    try:
        with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
            query = """
                SELECT 
                    et.Date_Tracking,
                    et.Categorie_Tracking,
                    et.Quantite,
                    et.Unite,
                    et.Cout,
                    et.Localisation,
                    et.Observations,
                    et.Date_Saisie,
                    u.FirstName_User || ' ' || u.LastName_User as Saisi_Par
                FROM EnergyTracking et
                LEFT JOIN Users u ON et.ID_User = u.ID_User
                WHERE et.Type_Tracking = 'Eau'
                    AND et.Date_Tracking BETWEEN ? AND ?
            """
            
            params = [start_date, end_date]
            
            if water_type_filter != "Tous":
                query += " AND et.Categorie_Tracking = ?"
                params.append(water_type_filter)
            
            query += " ORDER BY et.Date_Tracking DESC"
            
            df = pd.read_sql_query(query, conn, params=params)
        
        if not df.empty:
            col_met1, col_met2, col_met3 = st.columns(3)
            
            with col_met1:
                total_quantity = df['Quantite'].sum()
                st.metric("Consommation totale", f"{total_quantity:.2f} m³/L")
            
            with col_met2:
                total_cost = df['Cout'].sum()
                st.metric("Coût total", f"{total_cost:.2f} DH")
            
            with col_met3:
                avg_daily = total_quantity / len(df['Date_Tracking'].unique())
                st.metric("Moyenne quotidienne", f"{avg_daily:.2f} m³/L/jour")
            
            st.markdown("##### Détails des enregistrements")
            st.dataframe(
                df,
                column_config={
                    "Date_Tracking": "Date",
                    "Categorie_Tracking": "Type d'eau",
                    "Quantite": "Quantité",
                    "Unite": "Unité",
                    "Cout": "Coût (DH)",
                    "Localisation": "Localisation",
                    "Observations": "Observations",
                    "Date_Saisie": "Date saisie",
                    "Saisi_Par": "Saisi par"
                },
                use_container_width=True,
                hide_index=True
            )
            
            # Export en Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Historique_Eau')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Télécharger l'historique (Excel)",
                data=excel_data,
                file_name=f"historique_eau_{start_date}_{end_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        else:
            st.info(f"Aucune donnée trouvée pour la période sélectionnée ({start_date} à {end_date})")
    
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'historique : {e}")

def show_water_statistics():
    """Statistiques sur la consommation d'eau"""
    st.markdown("#### Statistiques de consommation d'eau")
    
    try:
        with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
            query_stats = """
                SELECT 
                    Categorie_Tracking as Type_Eau,
                    COUNT(*) as Nombre_Enregistrements,
                    SUM(Quantite) as Total_Consommation,
                    AVG(Quantite) as Moyenne_Consommation,
                    SUM(Cout) as Total_Cout,
                    MIN(Date_Tracking) as Premiere_Date,
                    MAX(Date_Tracking) as Derniere_Date
                FROM EnergyTracking 
                WHERE Type_Tracking = 'Eau'
                GROUP BY Categorie_Tracking
                ORDER BY Total_Consommation DESC
            """
            
            stats_df = pd.read_sql_query(query_stats, conn)
        
        if not stats_df.empty:
            for _, row in stats_df.iterrows():
                with st.expander(f" {row['Type_Eau']}", expanded=True):
                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    
                    with col_stat1:
                        st.metric("Consommation totale", f"{row['Total_Consommation']:.2f} m³/L")
                        st.metric("Moyenne", f"{row['Moyenne_Consommation']:.2f} m³/L")
                    
                    with col_stat2:
                        st.metric("Coût total", f"{row['Total_Cout']:.2f} DH" if row['Total_Cout'] else "N/A")
                        st.metric("Nombre d'enregistrements", int(row['Nombre_Enregistrements']))
                    
                    with col_stat3:
                        st.write(f"**Période :**")
                        st.write(f"Début : {row['Premiere_Date']}")
                        st.write(f"Fin : {row['Derniere_Date']}")
            
            fig, ax = plt.subplots(figsize=(8, 8))
            colors = ['#004890', '#EE1B2E', '#00A859']
            ax.pie(
                stats_df['Total_Consommation'], 
                labels=stats_df['Type_Eau'], 
                autopct='%1.1f%%',
                colors=colors[:len(stats_df)],
                startangle=90,
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )
            ax.set_title('Répartition de la consommation d\'eau', fontweight='bold', fontsize=14)
            
            st.pyplot(fig)
            
        else:
            st.info("Aucune statistique disponible pour la consommation d'eau.")
    
    except Exception as e:
        st.error(f"Erreur lors du calcul des statistiques : {e}")

def show_fuel_tracking():
    """Onglet de suivi du carburant"""
    st.markdown("### Suivi de la consommation de carburant")
    
    with st.form(key="fuel_placeholder"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Type de carburant", ["Gasoil", "Essence", "Gaz"])
            st.number_input("Quantité (L)", min_value=0.0, step=0.1)
            st.selectbox("Véhicule/Équipement", ["Camion", "Excavatrice", "Groupe électrogène", "Autre"])
        
        with col2:
            st.number_input("Prix unitaire (DH/L)", min_value=0.0, step=0.1)
            st.text_input("Numéro de carte carburant")
            st.date_input("Date de ravitaillement")
        
        st.form_submit_button("Enregistrer (bientôt disponible)", disabled=True)

def show_electricity_tracking():
    """Onglet de suivi de l'électricité"""
    st.markdown("### Suivi de la consommation électrique")
    
    with st.form(key="electricity_placeholder"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Source d'énergie", ["Réseau ONEE", "Solaire", "Éolien", "Groupe électrogène"])
            st.number_input("Consommation (kWh)", min_value=0.0, step=0.1)
            st.text_input("Compteur N°")
        
        with col2:
            st.number_input("Puissance souscrite (kVA)", min_value=0.0, step=0.1)
            st.number_input("Coût (DH)", min_value=0.0, step=0.1)
            st.date_input("Date de relevé")
        
        st.form_submit_button("Enregistrer (bientôt disponible)", disabled=True)

def show_pretask_page():
    """Page PréTask"""
    display_app_header("PréTask")
    
    # Vérification directe du service
    user_service = st.session_state.get('Service', '')
    if user_service not in ["Admin", "HSE"]:
        st.error("⚠️ Vous n'avez pas accès à cette fonctionnalité.")
        st.info("Cette fonctionnalité est réservée aux services Admin et HSE.")
        return
    
    st.markdown("### Système de PréTask - Analyse des risques avant travail")
    
    pretask_tab1, pretask_tab2, pretask_tab3 = st.tabs([
        " Nouvelle PréTask", 
        " PréTasks en cours", 
        " Historique"
    ])
    
    with pretask_tab1:
        st.markdown("#### Créer une nouvelle PréTask")
        with st.form(key="pretask_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                pretask_date = st.date_input("Date de la tâche *", value=datetime.now())
                work_location = st.text_input("Lieu de travail *", placeholder="Ex: Chantier X, Bâtiment Y")
                work_description = st.text_area("Description du travail *", placeholder="Décrivez la tâche à réaliser")
                team_members = st.text_area("Équipe concernée", placeholder="Noms des membres de l'équipe")
            
            with col2:
                equipment_used = st.text_area("Équipements utilisés", placeholder="Liste des équipements nécessaires")
                hazards_identified = st.text_area("Risques identifiés *", placeholder="Liste des risques potentiels")
                preventive_measures = st.text_area("Mesures préventives *", placeholder="Mesures de sécurité à prendre")
                supervisor = st.text_input("Superviseur responsable *")
            
            st.markdown("**Champs obligatoires ***")
            
            col_submit, col_reset = st.columns(2)
            with col_submit:
                if st.form_submit_button(" Créer la PréTask", use_container_width=True):
                    if all([work_location, work_description, hazards_identified, preventive_measures, supervisor]):
                        st.success("✅ PréTask créée avec succès !")
                    else:
                        st.error("Veuillez remplir tous les champs obligatoires (*)")
            with col_reset:
                st.form_submit_button(" Réinitialiser", use_container_width=True)
    
    with pretask_tab2:
        st.markdown("#### PréTasks en cours de validation")
        st.info("Aucune PréTask en cours pour le moment.")
    
    with pretask_tab3:
        st.markdown("#### Historique des PréTasks")
        st.info("Aucun historique disponible pour le moment.")

def main():
    icon_base64 = None
    
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        icon_path = os.path.join("Images", "Corp.JPG")
    else:
        icon_path = os.path.join("Images", "SOGEA-MAROC.JPG")
    
    icon_base64 = get_base64_icon(icon_path)
    
    if icon_base64 is not None:
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
        
        .energy-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-top: 4px solid var(--primary-blue);
        }
        
        .water-card {
            border-top: 4px solid #004890;
        }
        
        .fuel-card {
            border-top: 4px solid #EE1B2E;
        }
        
        .electricity-card {
            border-top: 4px solid #FFD700;
        }
        
        .stMetric {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

    </style>
    """, unsafe_allow_html=True)

    # Initialisation des variables de session
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'menu_selection' not in st.session_state:
        st.session_state.menu_selection = "profil"
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'Service' not in st.session_state:
        st.session_state.Service = "Utilisateur"
    if 'Statut' not in st.session_state:
        st.session_state.Statut = "Utilisateur"
    if 'ID_User' not in st.session_state:
        st.session_state.ID_User = None
    if 'Nom_Prenom' not in st.session_state:
        st.session_state.Nom_Prenom = ""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    if not st.session_state.authenticated or st.session_state.current_user is None:
        show_login()
    else:
        user = st.session_state.current_user
        user_first_name = user[3] if len(user) > 3 and user[3] else ""
        user_last_name = user[4] if len(user) > 4 and user[4] else ""
        
        user_statut = st.session_state.Statut
        user_service = st.session_state.Service
        
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
                {user_statut} • {user_service}
            </p>
            <p style="color: var(--off-white); font-size: 0.9em; margin-top: 0;">
                SOGEA-MAROC
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Obtenir les éléments du menu selon le service
        menu_items = get_user_menu_items(user_service)
        
        # Afficher les boutons du menu (sauf logout)
        for label, key_name in menu_items:
            if key_name == "logout":
                continue
            
            if st.sidebar.button(label, key=f"menu_{key_name}"):
                st.session_state.menu_selection = key_name
                st.rerun()
        
        # Bouton de déconnexion
        st.sidebar.markdown("---")
        if st.sidebar.button("  Se déconnecter", key="sidebar_logout_btn"):
            # Nettoyer la session
            for key in list(st.session_state.keys()):
                if key not in ['_runner', '_client', '_pages', '_last_uploaded_file']:
                    del st.session_state[key]
            st.rerun()
        
        # Navigation selon la sélection
        current_page = st.session_state.menu_selection
        
        if current_page == "profil":
            show_profile_page()
        elif current_page == "energy_tracking":
            show_energy_tracking_page()
        elif current_page == "settings":
            show_settings()
        elif current_page == "sor":
            # Vérification d'accès pour SOR
            if user_service not in ["Admin", "HSE"]:
                st.error("⚠️ Vous n'avez pas accès à cette fonctionnalité.")
                st.info("Cette fonctionnalité est réservée aux services Admin et HSE.")
                st.session_state.menu_selection = "profil"
                st.rerun()
            else:
                show_sor_page()
        elif current_page == "pretask":
            show_pretask_page()
        else:
            show_profile_page()

if __name__ == "__main__":
    main()
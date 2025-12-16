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
            display_logo(os.path.join("Images", "SOGEA-MAROC.JPG"), width=280)
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

def show_edit_profile():
    user = st.session_state.current_user
    
    
    if 'selected_user_id' not in st.session_state:
        st.session_state.selected_user_id = None
    if 'selected_user_data' not in st.session_state:
        st.session_state.selected_user_data = None
    if 'show_edit_section' not in st.session_state:
        st.session_state.show_edit_section = False
    
   # st.subheader("Modification des profils utilisateurs")
    
    
    # st.markdown("### Recherche et gestion des utilisateurs")
    
   
    col_search, col_add = st.columns([3, 1])
    
    with col_search:
       # st.markdown("#### Rechercher par CIN")
        cin_search = st.text_input(
            "Entrez le CIN de l'utilisateur :",
            placeholder="Ex: AB123456",
            key="search_cin_input",
            label_visibility="collapsed"
        )
        
        col_search_btn, col_clear = st.columns([1, 2])
        with col_search_btn:
            search_button = st.button("Rechercher", key="search_cin_button", use_container_width=True)
    
    with col_add:

        
        add_button = st.button("➕", 
                      key="add_new_user_button",
                      use_container_width=True,
                      help="Ajouter un nouvel utilisateur")
    
    
    with col_clear:
        if st.session_state.show_edit_section:
            if st.button("Effacer", key="clear_search_button", use_container_width=True):
                st.session_state.show_edit_section = False
                st.session_state.selected_user_id = None
                st.session_state.selected_user_data = None
                st.rerun()
    
    
    user_data = None
    if search_button and cin_search:
        try:
            with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM Users WHERE CIN_User=?", (cin_search.strip().upper(),))
                user_data = c.fetchone()
                
                if user_data:
                    st.session_state.selected_user_id = user_data[0]
                    st.session_state.selected_user_data = user_data
                    st.session_state.show_edit_section = True
                    #st.success(f"Utilisateur trouvé : {user_data[3]} {user_data[4]}")
                else:
                    st.session_state.show_edit_section = False
                   # st.info(f"Aucun utilisateur trouvé avec le CIN : {cin_search}")
        except Exception as e:
            st.error(f"Erreur lors de la recherche : {e}")
    
   
    if add_button:
        st.session_state.show_edit_section = True
        st.session_state.selected_user_id = None
        st.session_state.selected_user_data = None
        st.rerun()
    
    st.markdown("---")
    
    
    if st.session_state.show_edit_section:
       
        if st.session_state.selected_user_data:
           
            try:
                with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                    c = conn.cursor()
                    c.execute("SELECT * FROM Users WHERE ID_User=?", (st.session_state.selected_user_id,))
                    full_user_data = c.fetchone()
                    
                    if not full_user_data:
                        st.error("Utilisateur non trouvé dans la base de données")
                        st.session_state.show_edit_section = False
                        st.session_state.selected_user_id = None
                        st.session_state.selected_user_data = None
                        st.rerun()
                        return
            except Exception as e:
                st.error(f"Erreur lors du chargement des données utilisateur : {e}")
                return
            
            
            username_display = full_user_data[1] if len(full_user_data) > 1 else "Utilisateur"
            st.markdown(f"###  Modifier l'utilisateur : {username_display}")
            
            with st.form(key="edit_profile_form"):
                st.markdown("#### Informations personnelles")
                col1, col2 = st.columns(2)
                
                with col1:
                    CIN = st.text_input("CIN *", 
                                        value=full_user_data[7] if len(full_user_data) > 7 else "", 
                                        key="edit_profile_cin")
                    username = st.text_input("Nom d'utilisateur *", 
                                            value=username_display,
                                            key="edit_profile_username")
                    first_name = st.text_input("Prénom *", 
                                              value=full_user_data[3] if len(full_user_data) > 3 else "",
                                              key="edit_profile_first_name")
                    last_name = st.text_input("Nom de famille *", 
                                             value=full_user_data[4] if len(full_user_data) > 4 else "",
                                             key="edit_profile_last_name")
                
                with col2:
                    email = st.text_input("Email", 
                                         value=full_user_data[5] if len(full_user_data) > 5 else "",
                                         key="edit_profile_email")
                    phone = st.text_input("Téléphone", 
                                         value=full_user_data[6] if len(full_user_data) > 6 else "",
                                         key="edit_profile_phone")
                    
                    current_statut = full_user_data[9] if len(full_user_data) > 9 else 'Utilisateur'
                    if st.session_state.get('is_admin', False):
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
                
                
                st.markdown("---")
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
                
                st.markdown("---")
                st.markdown("**Champs obligatoires ***")
                
               
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    submitted = st.form_submit_button(" Enregistrer", 
                                                     use_container_width=True)
                with col_btn2:
                    delete_button = st.form_submit_button(" Supprimer", 
                                                         use_container_width=True)
                with col_btn3:
                    canceled = st.form_submit_button("✖ Annuler", 
                                                    use_container_width=True)
                
                if canceled:
                    st.session_state.show_edit_section = False
                    st.session_state.selected_user_id = None
                    st.session_state.selected_user_data = None
                    st.rerun()
                
                if delete_button:
                    try:
                        with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                            c = conn.cursor()
                            c.execute("DELETE FROM Users WHERE ID_User=?", (st.session_state.selected_user_id,))
                            conn.commit()
                        
                        st.success("Utilisateur supprimé avec succès !")
                        st.session_state.show_edit_section = False
                        st.session_state.selected_user_id = None
                        st.session_state.selected_user_data = None
                        st.rerun()
                    except Exception as e:
                        st.error(f" Erreur lors de la suppression : {e}")
                
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
                                        Email_User=?, Phone_User=?, Statut_User=?
                                    WHERE ID_User=?
                                """, (CIN, username, first_name, last_name, 
                                      email, phone, statut, st.session_state.selected_user_id))
                                
                                
                                if new_password:
                                    hashed_password = hash_password(new_password)
                                    c.execute("UPDATE Users SET Password=? WHERE ID_User=?", 
                                             (hashed_password, st.session_state.selected_user_id))
                                
                                conn.commit()
                                
                                
                                if st.session_state.current_user[0] == st.session_state.selected_user_id:
                                    c.execute("SELECT * FROM Users WHERE ID_User=?", (st.session_state.selected_user_id,))
                                    updated_user = c.fetchone()
                                    st.session_state.current_user = updated_user
                            
                            st.success(f" Profil de {first_name} {last_name} mis à jour avec succès !")
                            st.rerun()
                            
                        except sqlite3.IntegrityError as e:
                            if "CIN_User" in str(e) or "CIN" in str(e):
                                st.error(" Ce CIN existe déjà dans la base de données !")
                            elif "Username" in str(e):
                                st.error(" Ce nom d'utilisateur existe déjà !")
                            else:
                                st.error(f" Erreur d'intégrité : {e}")
                        except Exception as e:
                            st.error(f" Erreur lors de la mise à jour : {e}")
        
        
        else:
            st.markdown("### ➕ Ajouter un nouvel utilisateur")
            
            with st.form(key="add_user_form"):
                st.markdown("#### Informations personnelles")
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
                
                st.markdown("---")
                st.markdown("**Champs obligatoires ***")
                
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    submitted = st.form_submit_button("Enregistrer", 
                                                     use_container_width=True)
                with col_btn2:
                    reset_button = st.form_submit_button("Réinitialiser", 
                                                        use_container_width=True)
                with col_btn3:
                    canceled = st.form_submit_button("✖ Annuler", 
                                                    use_container_width=True)
                
                if canceled:
                    st.session_state.show_edit_section = False
                    st.rerun()
                
                if reset_button:
                    st.rerun()
                
                if submitted:
                    
                    if not all([CIN, username, password, first_name, last_name, statut]):
                        st.error("Veuillez remplir tous les champs obligatoires (*)")
                    else:
                        try:
                            hashed_password = hash_password(password)
                            
                            with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                                c = conn.cursor()
                                c.execute("""
                                    INSERT INTO Users 
                                    (CIN_User, Username, Password, FirstName_User, LastName_User, 
                                     Email_User, Phone_User, Statut_User) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (CIN, username, hashed_password, first_name, last_name, 
                                     email or "", phone or "", statut))
                                conn.commit()
                            
                            st.success(f" Utilisateur {username} créé avec succès !")
                            st.session_state.show_edit_section = False
                            st.rerun()
                        except sqlite3.IntegrityError as e:
                            if "CIN_User" in str(e):
                                st.error("❌ Ce CIN existe déjà dans la base de données !")
                            elif "Username" in str(e):
                                st.error("❌ Ce nom d'utilisateur existe déjà !")
                            else:
                                st.error(f" Erreur d'intégrité : {e}")
                        except Exception as e:
                            st.error(f" Erreur lors de la création : {e}")
    
    
    else:
        st.markdown("###  Liste des utilisateurs existants")
        
        try:
            with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                c = conn.cursor()
                c.execute("SELECT ID_User, CIN_User, Username, FirstName_User, LastName_User, Email_User, Phone_User, Statut_User FROM Users")
                all_users = c.fetchall()
            
            if all_users:
                
                users_df = pd.DataFrame(
                    all_users,
                    columns=["ID", "CIN", "Nom d'utilisateur", "Prénom", "Nom", "Email", "Téléphone", "Statut"]
                )
                
                st.markdown(f"**Total des utilisateurs :** {len(users_df)}")
                
                
               # st.markdown("#### Tableau des utilisateurs")
                st.dataframe(
                    users_df[["CIN", "Nom d'utilisateur", "Prénom", "Nom", "Email", "Statut"]],
                    column_config={
                        "CIN": st.column_config.TextColumn("CIN", width="small"),
                        "Nom d'utilisateur": st.column_config.TextColumn("Nom d'utilisateur", width="medium"),
                        "Prénom": st.column_config.TextColumn("Prénom", width="small"),
                        "Nom": st.column_config.TextColumn("Nom", width="small"),
                        "Email": st.column_config.TextColumn("Email", width="medium"),
                        "Statut": st.column_config.TextColumn("Statut", width="small")
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=400
                )
                
               
                st.markdown("---")
                col_stat1, col_stat2 = st.columns(2)
                
                with col_stat1:
                    st.markdown("#### Répartition par statut")
                    if not users_df["Statut"].empty:
                        statut_counts = users_df["Statut"].value_counts()
                        for statut_name, count in statut_counts.items():
                            st.write(f"**{statut_name}** : {count} utilisateur(s)")
                
                with col_stat2:
                    st.markdown("#### Détails rapides")
                    st.write(f"**Total** : {len(users_df)} utilisateurs")
                    if not users_df["CIN"].empty:
                        cin_not_null = users_df["CIN"].notna().sum()
                        st.write(f"**Avec CIN** : {cin_not_null} utilisateurs")
                
                
                csv = users_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=" Télécharger la liste (CSV)",
                    data=csv,
                    file_name="users_sogea_maroc.csv",
                    mime="text/csv",
                    key="download_users_list"
                )
                
            else:
                st.info(" Aucun utilisateur trouvé dans la base de données.")
                
        except Exception as e:
            st.error(f"Erreur lors du chargement des utilisateurs : {e}")

def show_settings():
   # st.subheader("Gestion des utilisateurs")   
   # st.markdown("---")
    
   
    if 'user_found' not in st.session_state:
        st.session_state.user_found = False
    if 'current_user_cin' not in st.session_state:
        st.session_state.current_user_cin = None
    if 'show_add_form' not in st.session_state:
        st.session_state.show_add_form = False
    
  
    st.markdown("### Gestion des utilisateurs")
    col_search1, col_search2 = st.columns([2, 1])
    
    with col_search1:
        cin_search = st.text_input("Recherche d'utilisateur par CIN :", 
                                   key="cin_search_input",
                                   placeholder="Ex: AB123456",
                                   label_visibility="visible")
        
    with col_search2:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
           # search_button = st.button(" Rechercher", key="cin_search_button", use_container_width=True)
            pass
        with col_btn2:
            search_button = st.button(" Rechercher", key="cin_search_button", use_container_width=True)
            add_button = st.button("➕", key="add_user_button", 
                                   use_container_width=True,
                                   help="Ajouter un nouvel utilisateur")
    
    
    if add_button:
        st.session_state.show_add_form = not st.session_state.show_add_form
        st.session_state.user_found = False
        st.session_state.current_user_cin = None
        st.rerun()
    
    user_data = None
    
    
    if st.session_state.user_found and st.session_state.current_user_cin:
        try:
            with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM Users WHERE CIN_User=?", (st.session_state.current_user_cin,))
                user_data = c.fetchone()
        except:
            st.session_state.user_found = False
            st.session_state.current_user_cin = None
    
    if search_button and cin_search:
        try:
            with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM Users WHERE CIN_User=?", (cin_search.strip(),))
                user_data = c.fetchone()
                
                if user_data:
                    st.session_state.user_found = True
                    st.session_state.current_user_cin = cin_search.strip()
                    st.session_state.show_add_form = False
                    st.success(f"Utilisateur trouvé : {user_data[3]} {user_data[4]}")
                else:
                    st.session_state.user_found = False
                    st.session_state.current_user_cin = None
                    st.info(f"Aucun utilisateur trouvé avec le CIN : {cin_search}")
        except Exception as e:
            st.error(f"Erreur lors de la recherche : {e}")
    
   
    if st.session_state.user_found:
        if st.button("Nouvelle recherche", key="new_search_button"):
            st.session_state.user_found = False
            st.session_state.current_user_cin = None
            st.rerun()
    
    st.markdown("---")
    
    
    if st.session_state.user_found and user_data:
        
        username_display = user_data[1] if len(user_data) > 1 else "Utilisateur"
        st.markdown(f"### Modifier l'utilisateur : {username_display}")
        
        with st.form(key="edit_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                CIN = st.text_input("CIN *", value=user_data[7] if len(user_data) > 7 else "", key="edit_user_cin", disabled=True)
                username = st.text_input("Nom d'utilisateur *", value=user_data[1], key="edit_user_username")
                first_name = st.text_input("Prénom *", value=user_data[3] if len(user_data) > 3 else "", key="edit_user_first_name")
                last_name = st.text_input("Nom de famille *", value=user_data[4] if len(user_data) > 4 else "", key="edit_user_last_name")
                
            with col2:
                email = st.text_input("Email", value=user_data[5] if len(user_data) > 5 else "", key="edit_user_email")
                phone = st.text_input("Téléphone", value=user_data[6] if len(user_data) > 6 else "", key="edit_user_phone")
                statut = st.selectbox(
                    "Statut *",
                    ["Utilisateur", "Administrateur", "Chef.Chentier", "HSE", "Gestionnaire"],
                    index=["Utilisateur", "Administrateur", "Chef.Chentier", "HSE", "Gestionnaire"].index(user_data[9]) if user_data[9] in ["Utilisateur", "Administrateur", "Chef.Chentier", "HSE", "Gestionnaire"] else 0,
                    key="edit_user_statut"
                )
            
            st.markdown("**Champs obligatoires *")
            
            
            st.markdown("---")
            st.markdown("### Changer le mot de passe")
            col_pass1, col_pass2 = st.columns(2)
            with col_pass1:
                new_password = st.text_input("Nouveau mot de passe", type="password", 
                                            key="edit_user_new_password", 
                                            placeholder="Laisser vide pour ne pas changer")
            with col_pass2:
                confirm_password = st.text_input("Confirmer le mot de passe", type="password",
                                                key="edit_user_confirm_password",
                                                placeholder="Laisser vide pour ne pas changer")
            
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                update_button = st.form_submit_button("Mettre à jour", use_container_width=True)
            with btn_col2:
                delete_button = st.form_submit_button("Supprimer l'utilisateur", use_container_width=True)
            with btn_col3:
                cancel_button = st.form_submit_button("Annuler", use_container_width=True)
            
            if cancel_button:
                st.info("Modification annulée")
                st.rerun()
            
            if delete_button:
                try:
                    with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                        c = conn.cursor()
                        c.execute("DELETE FROM Users WHERE CIN_User=?", (user_data[7],))
                        conn.commit()
                    st.session_state.user_found = False
                    st.session_state.current_user_cin = None
                    st.success("Utilisateur supprimé avec succès !")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de la suppression : {e}")
            
            if update_button:
                if not all([CIN, username, first_name, last_name, statut]):
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                elif new_password and new_password != confirm_password:
                    st.error("Les mots de passe ne correspondent pas !")
                else:
                    try:
                        with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                            c = conn.cursor()
                            
                            
                            update_data = (username, first_name, last_name, 
                                          email or "", phone or "", 
                                          statut, user_data[7])
                            
                           
                            c.execute("""
                                UPDATE Users 
                                SET Username=?, FirstName_User=?, LastName_User=?, 
                                    Email_User=?, Phone_User=?, Statut_User=?
                                WHERE CIN_User=?
                            """, update_data)
                            
                            
                            if new_password:
                                hashed_password = hash_password(new_password)
                                c.execute("UPDATE Users SET Password=? WHERE CIN_User=?", 
                                         (hashed_password, user_data[7]))
                            
                            conn.commit()
                        
                        st.success("Utilisateur mis à jour avec succès !")
                        st.rerun()
                    except sqlite3.IntegrityError as e:
                        if "Username" in str(e):
                            st.error(f"Le nom d'utilisateur '{username}' existe déjà !")
                        else:
                            st.error(f"Erreur d'intégrité : {e}")
                    except Exception as e:
                        st.error(f"Erreur lors de la mise à jour : {e}")
    
    # Afficher le formulaire d'ajout si le bouton plus a été cliqué
    elif st.session_state.show_add_form:
        st.markdown("### Ajouter un nouvel utilisateur")
        
        # Bouton pour masquer le formulaire
        if st.button("✖ Masquer le formulaire", key="hide_form_button"):
            st.session_state.show_add_form = False
            st.rerun()
        
        with st.form(key="add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                CIN = st.text_input("CIN *", key="add_user_cin", placeholder="Ex: AB123456")
                username = st.text_input("Nom d'utilisateur *", key="add_user_username")
                password = st.text_input("Mot de passe *", type="password", key="add_user_password")
                first_name = st.text_input("Prénom *", key="add_user_first_name")
                last_name = st.text_input("Nom de famille *", key="add_user_last_name")
                
            with col2:
                email = st.text_input("Email", key="add_user_email")
                phone = st.text_input("Téléphone", key="add_user_phone")
                statut = st.selectbox(
                    "Statut *",
                    ["Utilisateur", "Administrateur", "Chef.Chentier", "HSE", "Gestionnaire"],
                    key="add_user_statut"
                )
            
            st.markdown("**Champs obligatoires *")
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                submit_button = st.form_submit_button("Enregistrer", use_container_width=True)
            with btn_col2:
                cancel_button = st.form_submit_button("Annuler", use_container_width=True)
            
            if cancel_button:
                st.info("Opération annulée")
                st.session_state.show_add_form = False
                st.rerun()
            
            if submit_button:
                if not all([CIN, username, password, first_name, last_name, statut]):
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                else:
                    try:
                        hashed_password = hash_password(password)
                        
                        with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
                            c = conn.cursor()
                            c.execute("""
                                INSERT INTO Users 
                                (CIN_User, Username, Password, FirstName_User, LastName_User, 
                                 Email_User, Phone_User, Statut_User) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (CIN, username, hashed_password, first_name, last_name, 
                                 email or "", phone or "", statut))
                            conn.commit()
                        
                        st.success(f"Utilisateur {username} créé avec succès !")
                        st.session_state.show_add_form = False
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
    
    #st.markdown("---")
    st.subheader("Liste des utilisateurs existants")
    
    try:
        with sqlite3.connect('BD_SOGEA-MAROC.db') as conn:
            c = conn.cursor()
            c.execute("SELECT CIN_User, Username, FirstName_User, LastName_User, Email_User, Phone_User, Statut_User FROM Users")
            users = c.fetchall()
        
        if users:
            df = pd.DataFrame(  
                users,
                columns=["CIN", "Nom d'utilisateur", "Prénom", "Nom", "Email", "Téléphone", "Statut"]
            )
            
            st.markdown(f"**Total des utilisateurs :** {len(df)}")
            
           # st.markdown("### Tableau des utilisateurs")
            
            st.dataframe(
                df,
                column_config={
                    "CIN": st.column_config.TextColumn("CIN", width="medium"),
                    "Nom d'utilisateur": st.column_config.TextColumn("Nom d'utilisateur", width="medium"),
                    "Prénom": st.column_config.TextColumn("Prénom", width="medium"),
                    "Nom": st.column_config.TextColumn("Nom", width="medium"),
                    "Email": st.column_config.TextColumn("Email", width="large"),
                    "Téléphone": st.column_config.TextColumn("Téléphone", width="medium"),
                    "Statut": st.column_config.TextColumn("Statut", width="medium")
                },
                hide_index=True,
                use_container_width=True,
                height=400
            )
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Télécharger la liste des utilisateurs (CSV)",
                data=csv,
                file_name="users_sogea_maroc.csv",
                mime="text/csv",
                key="download_users_csv"
            )
            
            st.markdown("### Répartition par statut")
            if not df["Statut"].empty:
                statut_counts = df["Statut"].value_counts()
                cols = st.columns(min(4, len(statut_counts)))
                for i, (statut_name, count) in enumerate(statut_counts.items()):
                    if i < 4:
                        with cols[i % len(cols)]:
                            st.metric(label=f"Statut: {statut_name}", value=count)
            
        else:
           # st.info("Aucun utilisateur trouvé dans la base de données.")
            pass
    except Exception as e:
        st.error(f"Erreur lors du chargement des utilisateurs : {e}")

def show_sor_page():
    """Page SOR (Suivi Opérationnel de Routine) pour HSE et Chef de chantier"""
    
    # Afficher le header de la page
    display_app_header("Suivi Opérationnel de Routine (SOR)")
    
    # Informations sur l'utilisateur connecté
    user = st.session_state.current_user
    user_name = get_user_name(user)
    user_statut = get_user_status(user)
    
    # Afficher un message de bienvenue
   # st.markdown(f"""
  #  <div class='info-card'>
 #       <h3 style='color: var(--primary-blue); margin-top: 0;'>
  #          Bienvenue dans le module SOR - {user_name}
   #     </h3>
    #    <p style='font-size: 1.1em;'>
    #       Vous êtes connecté en tant que <strong>{user_statut}</strong>.
    #    Ce module est réservé aux équipes HSE et Chefs de chantier.
       # </p>
    #</div>
   # """, unsafe_allow_html=True)
    
    # Section principale SOR
  #  st.markdown("---")
    styled_subheader(" Fonctionnalités SOR")
    
    # Créer des onglets pour les différentes fonctionnalités
    tab1, tab2, tab3, tab4 = st.tabs([
        " Nouveau SOR", 
        " SOR en cours", 
        " SOR terminés", 
        " Statistiques"
    ])
    
    with tab1:
        st.markdown("### Créer un nouveau SOR")
        
        with st.form(key="new_sor_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                sor_date = st.date_input("Date du SOR", value=date.today())
                chantier = st.selectbox(
                    "Chantier",
                    ["Chantier A - Casablanca", "Chantier B - Rabat", "Chantier C - Marrakech", 
                     "Chantier D - Tanger", "Chantier E - Agadir"],
                    index=0
                )
                type_intervention = st.selectbox(
                    "Type d'intervention",
                    ["Visite de sécurité", "Audit HSE", "Inspection équipements", 
                     "Formation sécurité", "Réunion sécurité", "Autre"],
                    index=0
                )
            
            with col2:
                Déclarant = st.text_input(
                    "Déclarant",
                    value=user_name,
                    disabled=True
                )
                statut_sor = st.selectbox(
                    "Statut",
                    ["Planifié", "En cours", "À reporter", "Urgent"],
                    index=0
                )
                priorite = st.select_slider(
                    "Priorité",
                    options=["Basse", "Moyenne", "Haute", "Critique"],
                    value="Moyenne"
                )
            
            st.markdown("### Description de l'intervention")
            description = st.text_area(
                "Description détaillée",
                placeholder="Décrivez l'intervention à effectuer...",
                height=150
            )
            
            st.markdown("### Points de contrôle")
            col_check1, col_check2 = st.columns(2)
            
            with col_check1:
                epi_verifie = st.checkbox("EPI vérifiés")
                signalisation = st.checkbox("Signalisation en place")
                acces_securise = st.checkbox("Accès sécurisé")
            
            with col_check2:
                equipements_ok = st.checkbox("Équipements vérifiés")
                procédures_respectees = st.checkbox("Procédures respectées")
                risques_identifies = st.checkbox("Risques identifiés")
            
            st.markdown("### Photos / Documents")
            photo_upload = st.file_uploader(
                "Ajouter une photo (optionnel)",
                type=['png', 'jpg', 'jpeg'],
                accept_multiple_files=False
            )
            
            st.markdown("---")
            
            col_submit, col_reset = st.columns(2)
            with col_submit:
                submit_sor = st.form_submit_button("Enregistrer le SOR", use_container_width=True)
            with col_reset:
                reset_sor = st.form_submit_button(" Réinitialiser", use_container_width=True)
            
            if submit_sor:
                if not description:
                    st.error("Veuillez saisir une description pour le SOR")
                else:
                    # Ici, normalement, vous enregistreriez dans la base de données
                    # Pour l'instant, simulation
                    st.success(f" SOR créé avec succès pour le chantier {chantier}")
                    st.info(f"Date : {sor_date} | Priorité : {priorite} | Statut : {statut_sor}")
                    
                    # Réinitialiser le formulaire
                    st.rerun()
    
    with tab2:
        st.markdown("### SOR en cours de traitement")
        
        # Données simulées pour la démonstration
        sor_en_cours = [
            {
                "id": "SOR-2024-001",
                "chantier": "Chantier A - Casablanca",
                "date": "2024-01-15",
                "Déclarant": user_name,
                "priorite": "Haute",
                "statut": "En cours"
            },
            {
                "id": "SOR-2024-002",
                "chantier": "Chantier B - Rabat",
                "date": "2024-01-14",
                "Déclarant": "Ahmed Benani",
                "priorite": "Moyenne",
                "statut": "Planifié"
            },
            {
                "id": "SOR-2024-003",
                "chantier": "Chantier C - Marrakech",
                "date": "2024-01-13",
                "Déclarant": user_name,
                "priorite": "Critique",
                "statut": "En cours"
            }
        ]
        
        for sor in sor_en_cours:
            with st.expander(f"🔴 {sor['id']} - {sor['chantier']} - Priorité: {sor['priorite']}"):
                col_info, col_action = st.columns([3, 1])
                
                with col_info:
                    st.write(f"**Date :** {sor['date']}")
                    st.write(f"**Déclarant :** {sor['Déclarant']}")
                    st.write(f"**Statut :** {sor['statut']}")
                
                with col_action:
                    if st.button(" Modifier", key=f"edit_{sor['id']}"):
                        st.info(f"Modification du SOR {sor['id']} - Fonctionnalité à implémenter")
                    
                    if st.button(" Terminer", key=f"complete_{sor['id']}"):
                        st.success(f"SOR {sor['id']} marqué comme terminé")
                        st.rerun()
    
    with tab3:
        st.markdown("### Historique des SOR terminés")
        
        sor_termines = [
            {
                "id": "SOR-2023-045",
                "chantier": "Chantier D - Tanger",
                "date": "2023-12-20",
                "Déclarant": user_name,
                "resultat": "Conforme"
            },
            {
                "id": "SOR-2023-044",
                "chantier": "Chantier A - Casablanca",
                "date": "2023-12-18",
                "Déclarant": "Fatima Zahra",
                "resultat": "Non-conformité mineure"
            }
        ]
        
        for sor in sor_termines:
            st.markdown(f"""
            <div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                <strong>🔵 {sor['id']} - {sor['chantier']}</strong><br>
                Date: {sor['date']} | Déclarant: {sor['Déclarant']} | 
                Résultat: <span style='color: {'green' if sor['resultat'] == 'Conforme' else 'orange'}'>
                {sor['resultat']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### Statistiques SOR")
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("SOR créés ce mois", "15", "+3")
        
        with col_stat2:
            st.metric("SOR en cours", "8", "-1")
        
        with col_stat3:
            st.metric("Taux de conformité", "92%", "+2%")
        
        st.markdown("---")
        
        # Graphique simple (simulé)
        st.markdown("#### Répartition par chantier")
        data = pd.DataFrame({
            'Chantier': ['Casablanca', 'Rabat', 'Marrakech', 'Tanger', 'Agadir'],
            'SOR': [5, 3, 4, 2, 1]
        })
        st.bar_chart(data.set_index('Chantier'))
    
    # Section pour les rapports
    st.markdown("---")
    styled_subheader(" Rapports")
    
    col_report1, col_report2 = st.columns(2)
    
    with col_report1:
        if st.button(" Générer rapport mensuel", use_container_width=True):
            st.info("Génération du rapport mensuel en cours...")
            st.success("Rapport généré avec succès !")
    
    with col_report2:
        if st.button(" Exporter vers Excel", use_container_width=True):
            st.info("Exportation des données SOR vers Excel...")
            st.success("Exportation terminée !")

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
        
        /* Styles supplémentaires pour SOR */
        .sor-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 5px solid var(--primary-blue);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .sor-high-priority {
            border-left: 5px solid #EE1B2E;
        }
        
        .sor-medium-priority {
            border-left: 5px solid #FFA500;
        }
        
        .sor-low-priority {
            border-left: 5px solid #008000;
        }

    </style>
    """, unsafe_allow_html=True)

    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'menu_selection' not in st.session_state:
        st.session_state.menu_selection = "profile"
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

    if st.session_state.current_user is None:
        show_login()
    else:
        # Récupérer les informations de l'utilisateur courant
        user = st.session_state.current_user
        user_first_name = user[3] if len(user) > 3 and user[3] else ""
        user_last_name = user[4] if len(user) > 4 and user[4] else ""
        user_statut = user[9] if len(user) > 9 else "Utilisateur"
        
        # Déterminer si l'utilisateur a accès à SOR
        has_sor_access = user_statut in ["HSE", "Chef.Chentier"]
        
        # Afficher le bon message dans la sidebar
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

        # Menu en fonction du statut de l'utilisateur
        menu_items = [
            ("Mon Profil", "profile"),
            ("Modifier le profil", "edit_profile")
        ]
        
        # Ajouter SOR pour HSE et Chef de chantier
        if has_sor_access:
            menu_items.insert(1, ("Safety Observation Report", "sor"))
        
        if st.session_state.get('is_admin', False):
            menu_items.append(("Settings", "settings"))

        for label, key_name in menu_items:
            if st.sidebar.button(label, key=f"menu_{key_name}"):
                st.session_state.menu_selection = key_name
                st.rerun()

        if st.sidebar.button("Se déconnecter", key="sidebar_logout_btn"):
            st.session_state.current_user = None
            st.session_state.menu_selection = "profile"
            st.session_state.is_admin = False
            st.session_state.authenticated = False
            st.rerun()

        # Afficher la page correspondante
        if st.session_state.menu_selection == "profile":
            display_app_header("Mon Profil")
            show_profile()
        elif st.session_state.menu_selection == "edit_profile":
            display_app_header("Modifier le profil")
            show_edit_profile()
        elif st.session_state.menu_selection == "settings":
            display_app_header("Gestion des utilisateurs")
            show_settings()
        elif st.session_state.menu_selection == "sor":
            show_sor_page()

if __name__ == "__main__":
    main()
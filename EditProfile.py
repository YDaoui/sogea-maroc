import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils import *

def show_edit_profile():
    user = st.session_state.current_user
    
    if 'selected_user_id' not in st.session_state:
        st.session_state.selected_user_id = None
    if 'selected_user_data' not in st.session_state:
        st.session_state.selected_user_data = None
    if 'show_edit_section' not in st.session_state:
        st.session_state.show_edit_section = False
    
    #st.subheader("Modification des profils utilisateurs")
    
   # st.markdown("### Recherche et gestion des utilisateurs")
    
    col_search, col_add = st.columns([3, 1])
    
    with col_search:
       # st.markdown("####  Rechercher par CIN")
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
                    st.success(f"Utilisateur trouvé : {user_data[3]} {user_data[4]}")
                else:
                    st.session_state.show_edit_section = False
                    st.info(f"Aucun utilisateur trouvé avec le CIN : {cin_search}")
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
                            ["Utilisateur", "Administrateur", "Superviseur", "Manager"],
                            index=["Utilisateur", "Administrateur", "Superviseur", "Manager"].index(current_statut) 
                            if current_statut in ["Utilisateur", "Administrateur", "Superviseur", "Manager"] else 0,
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
                        ["Utilisateur", "Administrateur", "Superviseur", "Manager"],
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
        st.markdown("### Liste des utilisateurs existants")
        
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
                
                #st.markdown("#### Tableau des utilisateurs")
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

if __name__ == "__main__":
    apply_custom_styles()
    display_app_header("Modifier le profil")
    show_edit_profile()
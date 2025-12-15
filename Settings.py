import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Utils import *

def show_settings():
   # st.subheader("Gestion des utilisateurs")   
   # st.markdown("---")
    
    if 'user_found' not in st.session_state:
        st.session_state.user_found = False
    if 'current_user_cin' not in st.session_state:
        st.session_state.current_user_cin = None
    if 'show_add_form' not in st.session_state:
        st.session_state.show_add_form = False
    
   # st.markdown("### Gestion des utilisateurs")
    col_search1, col_search2 = st.columns([1, 1])
    
    with col_search1:
        cin_search = st.text_input("Recherche d'utilisateur par CIN :", 
                                   key="cin_search_input",
                                   placeholder="Ex: AB123456",
                                   label_visibility="visible")
        
    with col_search2:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            search_button = st.button(" Rechercher", key="cin_search_button", use_container_width=True)
        with col_btn2:
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
    
   # st.markdown("---")
    
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
                    ["Utilisateur", "Administrateur", "Superviseur", "Manager"],
                    index=["Utilisateur", "Administrateur", "Superviseur", "Manager"].index(user_data[9]) if user_data[9] in ["Utilisateur", "Administrateur", "Superviseur", "Manager"] else 0,
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
    
    elif st.session_state.show_add_form:
        st.markdown("### Ajouter un nouvel utilisateur")
        
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
                    ["Utilisateur", "Administrateur", "Superviseur", "Manager"],
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
    
    st.markdown("---")
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
            
            st.markdown("### Tableau des utilisateurs")
            
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
            st.info("Aucun utilisateur trouvé dans la base de données.")
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des utilisateurs : {e}")

if __name__ == "__main__":
    apply_custom_styles()
    display_app_header("Gestion des utilisateurs")
    show_settings()
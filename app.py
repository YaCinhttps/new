
import json
import streamlit as st
import google.generativeai as genai
import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect("prompts.sqlite")
   
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            current_user TEXT
        )
    """)

    c.execute('''CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    prompt TEXT,
                    expected TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tests_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    prompt TEXT,
                    expected TEXT,
                    ai_answer TEXT,
                    is_correct INTEGER,
                    date_test TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS adl_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    code TEXT,
    question TEXT,
    answer TEXT,
    date_saved TEXT
     ) ''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,   
                    username TEXT UNIQUE,
                    password TEXT
                )''')

    conn.commit()
    conn.close()

init_db()

def add_prompt(user, prompt, expected):
    conn = sqlite3.connect("prompts.sqlite")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("INSERT INTO prompts (user, prompt, expected) VALUES (?, ?, ?)", 
              (user, prompt, expected))
    conn.commit()
    conn.close()

def update_prompt(prompt_id, new_prompt, new_expected):
    conn = sqlite3.connect("prompts.sqlite")
    c = conn.cursor()
    c.execute("UPDATE prompts SET prompt=?, expected=? WHERE id=?", (new_prompt, new_expected, prompt_id))
    conn.commit()
    conn.close()


def get_prompts(user):
    conn = sqlite3.connect("prompts.sqlite")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, prompt, expected FROM prompts WHERE user=?", (user,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def delete_prompt(prompt_id):
    conn = sqlite3.connect("prompts.sqlite")
    c = conn.cursor()
    c.execute("DELETE FROM prompts WHERE id=?", (prompt_id,))
    conn.commit()
    conn.close()


def save_test_result(user, prompt, expected, ai_answer, is_correct):
    conn = sqlite3.connect("prompts.sqlite")
    c = conn.cursor()
    c.execute("INSERT INTO tests_history (user, prompt, expected, ai_answer, is_correct, date_test) VALUES (?, ?, ?, ?, ?, ?)",
              (user, prompt, expected, ai_answer, int(is_correct), datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def save_adl_code(user, code, question, answer):
    conn = sqlite3.connect("prompts.sqlite")
    c = conn.cursor()
    c.execute(
        "INSERT INTO adl_history (user, code, question, answer ,date_saved) VALUES (?, ?, ?, ?, ?)",
        (user, code ,question, answer ,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()
    

def get_history(user):
    conn = sqlite3.connect("prompts.sqlite")
    c = conn.cursor()
    c.execute("SELECT id, prompt, expected, ai_answer, is_correct, date_test FROM tests_history WHERE user=? ORDER BY date_test DESC", (user,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_adl_history(user):
    conn = sqlite3.connect("prompts.sqlite")
    c = conn.cursor()
    c.execute("SELECT rowid, code, question, answer, date_saved FROM adl_history WHERE user=? ORDER BY date_saved DESC", (user,))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_test_history(row_id):
    conn = sqlite3.connect("prompts.sqlite")
    c = conn.cursor()
    c.execute("DELETE FROM tests_history WHERE id=?", (row_id,))
    conn.commit()
    conn.close()

def delete_adl_history(row_id):
    conn = sqlite3.connect("prompts.sqlite")
    c = conn.cursor()
    c.execute("DELETE FROM adl_history WHERE rowid=?", (row_id,))
    conn.commit()
    conn.close()

def save_session(user):
    conn = sqlite3.connect("prompts.sqlite")
    c = conn.cursor()
    c.execute("DELETE FROM session") 
    if user:
        c.execute("INSERT INTO session (current_user) VALUES (?)", (user,))
    conn.commit()
    conn.close()

def load_session():
    conn = sqlite3.connect('prompts.sqlite')
    c = conn.cursor()
    c.execute("SELECT current_user FROM session LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        st.session_state["current_user"] = row[0]

def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    conn = sqlite3.connect("prompts.sqlite")
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row and row[0] == hashed_password:
        return True
    return False
def register_user(username, password):
    conn = sqlite3.connect("prompts.sqlite")
    c = conn.cursor()
    hashed_password = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
default_user= None



st.set_page_config(page_title="Smart ADL", layout="wide")
if "current_user" not in st.session_state:
    load_session()


st.sidebar.title("Smart ADL")
menu = st.sidebar.radio("Navigation", [
    " Développement en ADL",
    " Optimisation de code",
    " Prompts & Tests",
    " Historique",
    " Gestion des utilisateurs"
])

st.title(menu)
genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")
if "adl_code" not in st.session_state:
    st.session_state.adl_code = ""

if menu == " Développement en ADL":
    st.subheader("Éditeur de code ADL")
    code = st.text_area("Code ADL", height=300, value=st.session_state.adl_code)
    st.session_state.adl_code = code
    question = st.text_input("Demander au chatbot", placeholder="Ex: Comment déclarer une variable ?")

    if question:
        with st.spinner(" Le chatbot réfléchit..."):
            prompt = f"""Tu es un expert du langage ADL. Voici le code actuel :\n{st.session_state.adl_code}\nL'utilisateur te demande : {question}"""
            prompt_code= f"""voici le code actuel :\n{st.session_state.adl_code}\n ,donner moi en code!! une reponse concise et pertinente à la question suivante : {question}"""
            try:
                response = model.generate_content(prompt)
                response_code=model.generate_content(prompt_code)
                st.info(" Réponse IA :\n" + response.text)

                if st.button("📥 Insérer dans le code"):
                    st.session_state.adl_code = response_code.text
                    save_adl_code(st.session_state["current_user"], st.session_state.adl_code, question, response.text)

                    st.success(" Réponse insérée dans le code !")
            except Exception as e:
                st.error(f" Erreur : {e}")



elif menu == " Optimisation de code":
    st.subheader("Optimisation de votre code")
    code = st.text_area("Code initial", height=200,placeholder="Entrez votre code ADL ici")
    if st.button("Optimiser"):
       with st.spinner("Optimisation en cours..."):
            prompt = f"""Tu es un expert en optimisation de code ADL. Voici le code à optimiser :\n{code}\nOptimise ce code pour qu'il soit plus efficace et lisible."""
            try:
                response = model.generate_content(prompt)
                optimized_code = response.text
                st.session_state.adl_code = optimized_code
                save_adl_code(st.session_state["current_user"], st.session_state.adl_code, "", "")
                st.success("Code optimisé avec succès.")
                st.code(optimized_code, language='adl')
            except Exception as e:
                st.error(f" Erreur : {e}") 
        

elif menu == " Prompts & Tests":
    st.subheader("Ajoutez un prompt personnalisé")

    if "prompts" not in st.session_state:
        st.session_state.prompts = get_prompts(st.session_state["current_user"] if "current_user" in st.session_state else "default_user")

    if "edit_index" not in st.session_state:
        st.session_state.edit_index = None

    if st.session_state.edit_index is None:
        with st.form("add_prompt_form"):
            new_input = st.text_area("Prompt (question ou instruction)", height=100)
            expected_output = st.text_area("Réponse attendue", height=100)
            submitted = st.form_submit_button("Ajouter le prompt")

            if submitted:
                if new_input.strip() and expected_output.strip():
                    add_prompt(user=st.session_state["current_user"], prompt=new_input.strip(), expected=expected_output.strip())
                    st.success(" Prompt ajouté avec succès.")
                    st.session_state.prompts = get_prompts(st.session_state["current_user"])
                else:
                    st.warning("Veuillez remplir les deux champs.")
    else:
    
        prompt_to_edit = st.session_state.prompts[st.session_state.edit_index]
        with st.form("edit_prompt_form"):
            updated_input = st.text_area("Modifier le prompt", value=prompt_to_edit['prompt'], height=100)
            updated_expected = st.text_area("Modifier la réponse attendue", value=prompt_to_edit['expected'], height=100)
            update_btn = st.form_submit_button(" Sauvegarder")
            cancel_btn = st.form_submit_button(" Annuler")

            if update_btn:
                st.session_state.prompts[st.session_state.edit_index] = {
                    "prompt": updated_input.strip(),
                    "expected": updated_expected.strip()
                }
                update_prompt(prompt_to_edit['id'], updated_input.strip(), updated_expected.strip())
                st.session_state.edit_index = None
                st.success(" Prompt modifié avec succès.")
                st.rerun()
            elif cancel_btn:
                st.session_state.edit_index = None
                st.rerun()

    if st.session_state.prompts:
        st.subheader("Prompts enregistrés")
        for i, p in enumerate(st.session_state.prompts):
            st.markdown(f"**{i+1}. Prompt :** `{p['prompt']}`")
            st.markdown(f"**Réponse attendue :** `{p['expected']}`")
            col1, col2,col3 = st.columns(3)
            with col1:
                if st.button(f" Modifier {i+1}"):
                    st.session_state.edit_index = i
                    st.rerun()
            with col2:
                if st.button(f"Supprimer {i+1}"):
                    delete_prompt(p['id']) 
                    st.session_state.edit_index = None
                    st.session_state.prompts = get_prompts(st.session_state["current_user"] if "current_user" in st.session_state else "default_user")
                    st.rerun()
            with col3:
                    single_prompt_json = json.dumps(p, indent=4, ensure_ascii=False)
                    st.download_button(
                        label="📥 Télécharger le prompt en JSON",
                        data=single_prompt_json,
                        file_name=f"prompt_{i+1}.json",
                        mime="application/json"
                    )

            
    uploaded_file = st.file_uploader("📤 Importer un fichier JSON", type=["json"])
    if uploaded_file is not None:
        try:
            imported_prompts = json.load(uploaded_file)

            if isinstance(imported_prompts, list) and all("prompt" in p and "expected" in p for p in imported_prompts):
                for p in imported_prompts:
                    add_prompt(
                        user=st.session_state.get("current_user", "default_user"),
                        prompt=p["prompt"],
                        expected=p["expected"]
                    )
                st.success("✅ Prompts importés avec succès !")
                st.session_state.prompts = get_prompts(st.session_state.get("current_user", "default_user"))
                st.rerun()
            else:
                st.error(" Format JSON invalide. Il doit contenir une liste d'objets avec 'prompt' et 'expected'.")

        except Exception as e:
            st.error(f"Erreur lors de l'import : {e}")
            

    
    if st.button("🔍 Lancer les tests"):
        
        if not st.session_state.prompts:
            st.warning("Aucun prompt enregistré pour tester.")
        else:
                
            genai.configure(api_key="AIzaSyApetU5zm2IEA_vrdpU97h2jvopK2wlI_s") 

            model = genai.GenerativeModel("gemini-1.5-flash")

            for i, p in enumerate(st.session_state.prompts):
                with st.spinner(f"Test du prompt {i+1}..."):
                    try:
                        response = model.generate_content(p['prompt'])
                        ai_answer = response.text.strip()
                        with st.container():
                            st.markdown(
                                f"""
                                <div style="
                                    background-color:#f9f9f9;
                                    padding:15px;
                                    border-radius:10px;
                                    margin-bottom:10px;
                                    border:1px solid #ddd;">
                                    <h4>📝 Test #{i+1}</h4>
                                    <b>💬 Prompt:</b> {p['prompt']}<br>
                                    <b>✅ Expected:</b> <span style="color:green;">{p['expected']}</span><br>
                                    <b>🤖 AI Answer:</b> <span style="color:purple;">{ai_answer}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        if p['expected'].lower() in ai_answer.lower():
                            st.success(" Réponse correcte")
                            is_correct = True
                            
                        else:
                            st.error(" Réponse incorrecte")
                            is_correct = False
                        save_test_result(
                                        st.session_state.get("current_user", "default_user"), 
                                        p['prompt'], 
                                        p['expected'], 
                                        ai_answer, 
                                        is_correct
                                                        )

                    except Exception as e:
                        st.error(f"Erreur lors du test : {e}")
    
    


elif menu == " Historique":
    st.subheader("Historique des tests")

    user = st.session_state["current_user"] if "current_user" in st.session_state else "default_user" 
    test_history = get_history(user)
    adl_history = get_adl_history(user)
    

    if test_history:
        for row_id, prompt, expected, ai_answer, is_correct, date_test in test_history:
            st.markdown(f"**🗓 Date :** {date_test}")
            st.markdown(f"**Prompt :** `{prompt}`")
            st.markdown(f"**Réponse attendue :** `{expected}`")
            st.markdown(f"**Réponse IA :** `{ai_answer}`")
            if is_correct:
                st.success("✅ Correct")
            else:
                st.error("❌ Incorrect")

            if st.button(f"🗑️ Supprimer Test ", key=f"del_test_{row_id}"):
                delete_test_history(row_id)
                st.success("Test supprimé avec succès ✅")
                st.rerun()

            st.markdown("---")
    else:
        st.info("Aucun historique trouvé pour cet utilisateur.")


    st.subheader("Historique des codes ADL")

    if adl_history:
        for row_id, code, question, answer, date_saved in adl_history:
            st.markdown(f"**🗓 Date :** {date_saved}")
            st.code(code, language="adl")
            st.markdown(f"**Question :** `{question}`")
            st.markdown(f"**Réponse IA :** `{answer}`")

            if st.button(f"🗑️ Supprimer Code ", key=f"del_adl_{row_id}"):
                delete_adl_history(row_id)
                st.success("Code supprimé avec succès ✅")
                st.rerun()

            st.markdown("---")
    else:
        st.info("Aucun historique ADL trouvé pour cet utilisateur.")




elif menu == " Gestion des utilisateurs":
    st.subheader("Gestion des utilisateurs")

    if "current_user" in st.session_state:
        st.success(f"Connecté en tant que : {st.session_state['current_user']}")
        if st.button("Déconnexion"):
            del st.session_state["current_user"]
            save_session(None)
            st.success("Déconnexion réussie.")
    else:
        tab1, tab2 = st.tabs([" Connexion", " Inscription"])

        with tab1:
            username = st.text_input("Nom d'utilisateur", key="login_username")
            password = st.text_input("Mot de passe", type="password", key="login_password")
            if st.button("Se connecter"):
                if verify_user(username, password):
                    st.session_state["current_user"] = username
                    save_session(username)
                    st.success(f"Bienvenue {username} !")
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect.")

        with tab2:
            new_username = st.text_input("Nom d'utilisateur", key="register_username")
            new_password = st.text_input("Mot de passe", type="password", key="register_password")
            if st.button("S'inscrire"):
                if new_username.strip() and new_password.strip():
                    if register_user(new_username, new_password):
                        st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
                    else:
                        st.error("Nom d'utilisateur déjà utilisé.")
                else:
                    st.warning("Veuillez remplir tous les champs.")

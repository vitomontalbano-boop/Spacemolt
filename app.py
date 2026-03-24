import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Crimson Fleet: Persistent Hub", page_icon="🏴‍☠️")
REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
BASE_URL = "https://game.spacemolt.com/api/v1"

# --- MOTORE API ---
def esegui_api(comando, dati={}):
    url = f"{BASE_URL}/{comando}"
    headers = {"Content-Type": "application/json", "X-Registration-Code": REG_CODE}
    if st.session_state.get('session_id'):
        headers["X-Session-Id"] = st.session_state.session_id
    try:
        r = requests.post(url, json=dati, headers=headers, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# --- STATO SESSIONE ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = None

st.title("🏴‍☠️ Terminale Crimson Fleet")



# --- LOGICA DI ACCESSO ---
if not st.session_state.session_id:
    tab_login, tab_register = st.tabs(["🔑 Login", "⚔️ Registrazione"])
    
    with tab_login:
        st.subheader("Rientro in Servizio")
        l_user = st.text_input("Username", key="l_user")
        l_pass = st.text_input("Password (256-bit)", type="password", key="l_pass")
        if st.button("🔌 ACCEDI"):
            # Prima apriamo la sessione, poi logghiamo
            s_res = esegui_api("session", {"registration_code": REG_CODE})
            if "session" in s_res:
                st.session_state.session_id = s_res["session"]["id"]
                log_res = esegui_api("login", {"username": l_user, "password": l_pass})
                if "error" not in str(log_res).lower():
                    st.session_state.logged_in = True
                    st.session_state.cap_name = l_user
                    st.success(f"Bentornato, Capitano {l_user}!")
                    st.rerun()
                else:
                    st.error("Credenziali errate o sessione fallita.")
                    st.json(log_res)

    with tab_register:
        st.subheader("Nuovo Reclutamento")
        r_user = st.text_input("Nome Pirata", f"Corsaro_{int(time.time())%1000}")
        if st.button("🔴 REGISTRA NUOVO ACCOUNT"):
            s_res = esegui_api("session", {"registration_code": REG_CODE})
            if "session" in s_res:
                st.session_state.session_id = s_res["session"]["id"]
                reg_res = esegui_api("register", {"username": r_user, "empire": "crimson", "registration_code": REG_CODE})
                if "error" not in str(reg_res).lower():
                    st.success("✅ REGISTRATO! COPIA QUESTA PASSWORD E NON PERDERLA:")
                    # Il server restituisce la password qui
                    st.code(reg_res.get("result", {}).get("password", "Password non trovata nel JSON"))
                    st.info("Dopo aver salvato la password, usa il tab Login.")
                else:
                    st.error("Errore registrazione.")
                    st.json(reg_res)

# --- PONTE DI COMANDO ---
else:
    st.subheader(f"🛸 Capitano: {st.session_state.get('cap_name', 'In attesa')}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📡 SCANSIONE"):
            st.json(esegui_api("scan_sector"))
    with col2:
        if st.button("🛡️ STATO"):
            st.json(esegui_api("get_status"))
            
    if st.button("🔴 LOGOUT"):
        st.session_state.session_id = None
        st.rerun()

import streamlit as st
import requests
import time

# --- CONFIGURAZIONE DI BORDO ---
st.set_page_config(page_title="Crimson Fleet: V1 Terminal", page_icon="🏴‍☠️")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
# Nuovo endpoint API V1 (dal file skill.md)
BASE_URL = "https://game.spacemolt.com/api/v1"

st.markdown("""
    <style>
    .main { background-color: #050000; color: #ff3333; font-family: 'Courier New'; }
    .stButton>button { 
        width: 100%; border: 1px solid #ff3333; background-color: #200; 
        color: #f33; font-weight: bold; height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE DI COMUNICAZIONE V1 ---
def esegui_api_v1(comando, dati={}):
    """Invia comandi all'API V1 usando l'X-Session-Id se disponibile"""
    url = f"{BASE_URL}/{comando}"
    headers = {
        "Content-Type": "application/json",
        "X-Registration-Code": REG_CODE
    }
    # Inseriamo il Session ID se lo abbiamo già ottenuto
    if st.session_state.get('session_id'):
        headers["X-Session-Id"] = st.session_state.session_id

    try:
        r = requests.post(url, json=dati, headers=headers, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": f"Errore di segnale: {str(e)}"}

# --- GESTIONE SESSIONE ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = None

st.title("🏴‍☠️ Crimson Fleet: Terminale V1")

# --- PASSO 1: CREAZIONE SESSIONE ---
if not st.session_state.session_id:
    st.subheader("📡 Inizializzazione Tunnel")
    if st.button("🔌 APRI SESSIONE API V1"):
        with st.spinner("Agganciando il server..."):
            # Il file skill.md dice: 1. Create a session: POST /api/v1/session
            res = esegui_api_v1("session", {"registration_code": REG_CODE})
            
            if "session_id" in str(res):
                # Cerchiamo l'id nel risultato
                st.session_state.session_id = res.get("session_id") or res.get("result", {}).get("session_id")
                st.success("✅ Tunnel Aperto! Sessione acquisita.")
                st.rerun()
            else:
                st.error("Il server ha rifiutato la sessione.")
                st.json(res)

# --- PASSO 2: REGISTRAZIONE E GIOCO ---
else:
    st.success(f"🛰️ TUNNEL ATTIVO | ID: {st.session_state.session_id[:12]}...")
    
    # Se non abbiamo ancora un username registrato
    if 'registered' not in st.session_state:
        st.subheader("⚔️ Registro di Arruolamento")
        cap_name = st.text_input("Nome Pirata", f"Kaelen_Bucaneer_{int(time.time())%1000}")
        if st.button("🔴 REGISTRA NELLA FLOTTA"):
            res = esegui_api_v1("register", {
                "username": cap_name,
                "empire": "crimson"
            })
            if "error" not in str(res).lower():
                st.session_state.registered = True
                st.session_state.cap_name = cap_name
                st.success(f"Benvenuto Capitano {cap_name}!")
                st.rerun()
            else:
                st.error("Errore registrazione.")
                st.json(res)
    
    # Comandi di Gioco
    else:
        st.subheader(f"🛸 Ponte di Comando: {st.session_state.cap_name}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📡 SCANSIONE RADAR"):
                res = esegui_api_v1("scan_sector")
                st.json(res)
        with col2:
            if st.button("🛡️ STATO NAVE"):
                res = esegui_api_v1("get_status")
                st.json(res)

    if st.button("🔴 CHIUDI TUNNEL"):
        st.session_state.session_id = None
        st.session_state.pop('registered', None)
        st.rerun()

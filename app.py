import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Crimson Fleet: Tactical Link", page_icon="🏴‍☠️")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
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

def esegui_api_v1(comando, dati={}):
    url = f"{BASE_URL}/{comando}"
    headers = {
        "Content-Type": "application/json",
        "X-Registration-Code": REG_CODE
    }
    if st.session_state.get('session_id'):
        headers["X-Session-Id"] = st.session_state.session_id

    try:
        r = requests.post(url, json=dati, headers=headers, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

if 'session_id' not in st.session_state:
    st.session_state.session_id = None

st.title("🏴‍☠️ Crimson Fleet: Terminale V1")

# --- PASSO 1: AGGANCIO SESSIONE ---
if not st.session_state.session_id:
    st.info("📡 In attesa di stabilire il link con SpaceMolt...")
    if st.button("🔌 STABILISCI LINK (V1)"):
        res = esegui_api_v1("session", {"registration_code": REG_CODE})
        
        # LOGICA CORRETTA PER IL TUO JSON:
        if "session" in res and "id" in res["session"]:
            st.session_state.session_id = res["session"]["id"]
            st.success("✅ Link Stabilito! Sessione acquisita.")
            st.rerun()
        else:
            st.error("Errore nell'estrazione del Session ID.")
            st.json(res)

# --- PASSO 2: ARRUOLAMENTO ---
else:
    st.success(f"🛰️ TUNNEL ATTIVO | ID: {st.session_state.session_id[:12]}...")
    
    if 'registered' not in st.session_state:
        st.subheader("⚔️ Registro di Arruolamento")
        # Generiamo un nome che non sia già preso (username_taken)
        default_name = f"Pirata_{int(time.time()) % 1000}"
        cap_name = st.text_input("Scegli il tuo nome da pirata", default_name)
        
        if st.button("🔴 GIURA FEDELTÀ ALLA FLOTTA"):
            # Usiamo l'ID sessione che abbiamo già per registrarci
            res = esegui_api_v1("register", {
                "username": cap_name,
                "empire": "crimson"
            })
            
            # Se la registrazione va a buon fine, il server restituisce i dati del player
            if "result" in res and not res.get("isError"):
                st.session_state.registered = True
                st.session_state.cap_name = cap_name
                st.success(f"Benvenuto Capitano {cap_name}! La galassia è nostra.")
                st.rerun()
            else:
                st.error("Errore durante l'arruolamento.")
                st.json(res)
    
    # --- PASSO 3: PONTE DI COMANDO ---
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

    if st.button("🔴 RESET"):
        st.session_state.session_id = None
        st.session_state.pop('registered', None)
        st.rerun()

import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Terminale Agente", page_icon="🚀")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Stile Terminale
st.markdown("<style>.main { background-color: #050a0f; color: #00d4ff; font-family: 'Courier New'; }</style>", unsafe_allow_html=True)

# --- FUNZIONE DI SESSIONE (LOGIN) ---
def inizializza_sessione():
    """Esegue il login obbligatorio richiesto dal server"""
    payload = {
        "jsonrpc": "2.0",
        "method": "login", # Metodo richiesto dall'errore
        "params": { "reg_code": REG_CODE },
        "id": 1
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        res_json = response.json()
        if "result" in res_json:
            return True, res_json["result"]
        else:
            return False, res_json.get("error", "Errore ignoto")
    except Exception as e:
        return False, str(e)

# --- FUNZIONE PER COMANDI ---
def invia_ordine(nome_comando, argomenti={}):
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": nome_comando,
            "arguments": argomenti
        },
        "id": int(time.time())
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- INTERFACCIA ---
st.title("🛰️ SpaceMolt Control Center")

# Gestione Stato Connessione
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    if st.button("🔌 STABILISCI CONNESSIONE NEURALE"):
        successo, msg = inizializza_sessione()
        if successo:
            st.session_state.logged_in = True
            st.success("✅ Sessione Inizializzata! Benvenuto Comandante.")
            st.rerun()
        else:
            st.error(f"❌ Fallimento Login: {msg}")
else:
    st.sidebar.success("📡 Collegato a SpaceMolt")
    if st.sidebar.button("Esci (Log out)"):
        st.session_state.logged_in = False
        st.rerun()

    # Pannello Azioni
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📡 Scansione Settore"):
            res = invia_ordine("scan_sector")
            st.json(res)
            
    with col2:
        if st.button("⛏️ Estrazione"):
            res = invia_ordine("mine_resources")
            st.json(res)

    st.divider()
    istruzione = st.text_input("Ordini per l'Ammiraglio (AI)", placeholder="Es. Vai su Plutone")
    if st.button("ESEGUI"):
        st.info(f"Ricevuto. Elaborazione rotta per {istruzione}...")

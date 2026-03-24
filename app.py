import streamlit as st
import requests
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Terminale Admiral", page_icon="🚀", layout="wide")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Stile Terminale Hard-Coded
st.markdown("""
    <style>
    .main { background-color: #010a01; color: #33ff33; font-family: 'Courier New', monospace; }
    .stButton>button { 
        width: 100%; border: 1px solid #33ff33; background-color: #001100; 
        color: #33ff33; font-weight: bold; border-radius: 0px;
    }
    .stButton>button:active { background-color: #33ff33; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE BATCH (IL "CUORE" DELL'APP) ---
def esegui_comando_batch(nome_tool, argomenti={}):
    """
    Invia un pacchetto BATCH: [Initialize, Initialized, ToolCall]
    Questo risolve il problema della sessione che scade istantaneamente.
    """
    batch_payload = [
        # 1. Passo: Inizializzazione
        {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2026-01-01",
                "reg_code": REG_CODE,
                "clientInfo": {"name": "Gemini-Admiral-Mobile", "version": "3.0"}
            },
            "id": 101
        },
        # 2. Passo: Notifica di conferma (senza ID come da protocollo)
        {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {"reg_code": REG_CODE}
        },
        # 3. Passo: Il comando reale che vogliamo eseguire
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": nome_tool,
                "arguments": {**argomenti, "reg_code": REG_CODE}
            },
            "id": 102
        }
    ]

    try:
        # Invio del pacchetto unico
        response = requests.post(
            API_URL, 
            json=batch_payload, 
            headers={"Authorization": f"Bearer {REG_CODE}"},
            timeout=15
        )
        
        risultati = response.json()
        
        # Cerchiamo la risposta del comando reale (quello con ID 102)
        if isinstance(risultati, list):
            for r in risultati:
                if r.get("id") == 102:
                    return r
            return risultati # Se non lo trova, restituisce tutto il batch
        return risultati
        
    except Exception as e:
        return {"error": f"Errore critico di trasmissione: {e}"}

# --- INTERFACCIA DI COMANDO ---
st.title("🛰️ SPACEMOLT: COMANDO BATCH")
st.write(f"📡 **Agente:** `CAPTAIN-GEN-2026` | **Link:** `OPEN-BATCH-PROTOCOL`")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📡 Sistemi di Bordo")
    if st.button("SCANSIONE RADAR"):
        with st.spinner("Compilazione pacchetto Batch..."):
            st.session_state.last_op = esegui_comando_batch("scan_sector")
            
    if st.button("STATO STRUTTURALE"):
        with st.spinner("Interrogazione telemetria..."):
            st.session_state.last_op = esegui_comando_batch("get_ship_status")

with col2:
    st.subheader("⛏️ Operazioni Minerarie")
    if st.button("ATTIVA LASER MINERARI"):
        with st.spinner("Sequenza di estrazione..."):
            st.session_state.last_op = esegui_comando_batch("mine_resources")
            
    if st.button("VERIFICA CARGO"):
        with st.spinner("Analisi inventario..."):
            st.session_state.last_op = esegui_comando_batch("get_inventory")

# --- OUTPUT CONSOLE ---
st.divider()
if 'last_op' in st.session_state:
    st.write("📂 **Dati Ricevuti dal Settore:**")
    st.json(st.session_state.last_op)
    
    # Check di debug per l'utente
    if "error" in st.session_state.last_op:
        msg = st.session_state.last_op["error"].get("message", "")
        if "Session not initialized" in msg:
            st.error("❗ Il server rifiuta persino il Batch. Potrebbe esserci un blocco sul Registration Code.")
else:
    st.info("In attesa di istruzioni. Seleziona un'azione per avviare il protocollo.")

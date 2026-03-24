import streamlit as st
import requests
import time

# --- CONFIGURAZIONE DI BORDO ---
st.set_page_config(page_title="SpaceMolt: Crimson Fleet Terminal", page_icon="🏴‍☠️")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
API_URL = "https://game.spacemolt.com/mcp"

# Stile Pirata (Rosso e Nero)
st.markdown("""
    <style>
    .main { background-color: #1a0000; color: #ff3333; font-family: 'Courier New'; }
    .stButton>button { 
        width: 100%; border: 1px solid #ff3333; background-color: #330000; 
        color: #ff3333; font-weight: bold; height: 3.5em;
    }
    .stTextInput>div>div>input { background-color: #220000; color: #ff3333; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE DI COMUNICAZIONE ---
def chiama_mcp(metodo, params):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {REG_CODE}"}
    payload = {"jsonrpc": "2.0", "method": metodo, "params": params, "id": int(time.time())}
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# --- GESTIONE STATO NAVE ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'captain_name' not in st.session_state:
    st.session_state.captain_name = ""

st.title("🏴‍☠️ Crimson Fleet: Hub Pirata")
st.write(f"📡 **Status:** {'Sincronizzato' if st.session_state.session_id else 'In attesa di registrazione'}")

# --- FASE 1: REGISTRAZIONE ---
if not st.session_state.session_id:
    st.subheader("⚔️ Reclutamento Capitano")
    username = st.text_input("Scegli il tuo nome da battaglia (es: Kaelen_Red)", "Kaelen_Red")
    
    if st.button("🔴 REGISTRA NELLA CRIMSON FLEET"):
        with st.spinner("Inizializzando link neurale..."):
            # Handshake obbligatorio
            chiama_mcp("initialize", {"protocolVersion": "2026-01-01", "reg_code": REG_CODE})
            chiama_mcp("notifications/initialized", {})
            
            # Registrazione come Pirata
            res = chiama_mcp("tools/call", {
                "name": "register",
                "arguments": {
                    "username": username,
                    "empire": "crimson", # Forzato su Crimson Fleet per il playstyle scelto
                    "reg_code": REG_CODE
                }
            })
            
            if "result" in res and "session_id" in res["result"]:
                st.session_state.session_id = res["result"]["session_id"]
                st.session_state.captain_name = username
                st.success(f"Benvenuto a bordo, Capitano {username}! La galassia tremerà.")
                st.rerun()
            else:
                st.error(f"Errore di registrazione: {res}")

# --- FASE 2: OPERAZIONI PIRATA ---
else:
    st.subheader(f"🛸 Nave: Blood Cipher | Capitano: {st.session_state.captain_name}")
    st.caption(f"Session Token: {st.session_state.session_id[:15]}...")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📡 SCANSIONE PREDE"):
            res = chiama_mcp("tools/call", {
                "name": "scan_sector",
                "arguments": {"session_id": st.session_state.session_id}
            })
            st.session_state.last_op = res
            
        if st.button("🛡️ STATO NAVE"):
            res = chiama_mcp("tools/call", {
                "name": "get_status",
                "arguments": {"session_id": st.session_state.session_id}
            })
            st.session_state.last_op = res

    with col2:
        if st.button("🏴‍☠️ ATTACCO / ABBORDAGGIO"):
            # Qui si potrebbero aggiungere coordinate o target
            st.warning("Seleziona prima un bersaglio dalla scansione!")
            
        if st.button("📦 BOTTINO (Inventario)"):
            res = chiama_mcp("tools/call", {
                "name": "get_inventory",
                "arguments": {"session_id": st.session_state.session_id}
            })
            st.session_state.last_op = res

    if 'last_op' in st.session_state:
        st.divider()
        st.write("📂 **Dati Sensori:**")
        st.json(st.session_state.last_op)

    if st.button("🔴 ABBANDONA NAVE (Logout)"):
        st.session_state.session_id = None
        st.rerun()

import streamlit as st
import asyncio
import websockets
import json
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Agente Neurale", page_icon="🛸")

REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
WS_URL = "wss://game.spacemolt.com/ws/mcp" # Usiamo il protocollo WebSocket

st.markdown("<style>.main { background-color: #000; color: #0f0; }</style>", unsafe_allow_html=True)

# --- MOTORE WEBSOCKET ---
async def comunica_con_spacemolt(comando, argomenti={}):
    """Apre un socket, fa l'handshake e invia il comando in un unico flusso continuo"""
    try:
        async with websockets.connect(WS_URL) as websocket:
            # 1. INITIALIZE
            await websocket.send(json.dumps({
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2026-01-01",
                    "reg_code": REG_CODE,
                    "clientInfo": {"name": "Gemini-Admiral-Mobile"}
                },
                "id": 1
            }))
            
            # Attendiamo la risposta di conferma (obbligatoria)
            init_res = await websocket.recv()
            
            # 2. NOTIFICATIONS/INITIALIZED
            await websocket.send(json.dumps({
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {"reg_code": REG_CODE}
            }))

            # 3. IL VERO COMANDO
            await websocket.send(json.dumps({
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": comando,
                    "arguments": {**argomenti, "reg_code": REG_CODE}
                },
                "id": int(time.time())
            }))
            
            # Riceviamo il risultato finale
            risultato = await websocket.recv()
            return json.loads(risultato)

    except Exception as e:
        return {"error": f"Errore di connessione spaziale: {e}"}

# --- INTERFACCIA ---
st.title("🛰️ SpaceMolt: Terminale WSS")
st.write(f"📡 **Link attivo via WebSocket** | **ID:** `{REG_CODE[:8]}...`")

col1, col2 = st.columns(2)

with col1:
    if st.button("📡 SCANSIONE SETTORE"):
        with st.spinner("Apriamo il tunnel..."):
            # Eseguiamo la funzione asincrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(comunica_con_spacemolt("scan_sector"))
            st.session_state.data = res

with col2:
    if st.button("⛏️ ESTRAZIONE"):
        with st.spinner("Laser in carica..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(comunica_con_spacemolt("mine_resources"))
            st.session_state.data = res

if 'data' in st.session_state:
    st.divider()
    st.subheader("📊 Output in Tempo Reale")
    st.json(st.session_state.data)

import streamlit as st
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="SpaceMolt: Crimson MCP", page_icon="🏴‍☠️")
REG_CODE = "8b4586fc4c72d5814472c5f35a93c235"
# Endpoint MCP raccomandato dal file skill.md
MCP_URL = "https://game.spacemolt.com/mcp"

st.markdown("<style>.main { background-color: #0a0505; color: #ff3333; }</style>", unsafe_allow_html=True)

# --- MOTORE MCP (ASINCRONO) ---
async def esegui_mcp_tool(tool_name, arguments={}):
    """Si connette come un vero client MCP e chiama il tool richiesto"""
    try:
        # Apriamo il trasporto SSE (Streamable HTTP) come raccomandato
        async with sse_client(MCP_URL) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Inizializzazione automatica gestita dalla libreria
                await session.initialize()
                
                # Aggiungiamo il registration_code a ogni chiamata come richiesto dal server
                full_args = {**arguments, "registration_code": REG_CODE}
                
                # Chiamata al tool (es. register, scan_sector, etc.)
                result = await session.call_tool(tool_name, full_args)
                return result.content
    except Exception as e:
        return f"Errore MCP: {str(e)}"

# --- INTERFACCIA STREAMLIT ---
st.title("🏴‍☠️ Crimson Fleet: MCP Terminal")
st.write("⚓️ *Protocollo Model Context Protocol attivo.*")

if 'session_id' not in st.session_state:
    st.session_state.session_id = None

# FASE 1: REGISTRAZIONE (Usando i tool scoperti via MCP)
if not st.session_state.session_id:
    st.subheader("⚔️ Arruolamento")
    # Suggerimento per nome unico
    captain_name = st.text_input("Nome Pirata", f"Kaelen_Rex_{int(time.time())%1000}")
    
    if st.button("🔴 REGISTRA VIA MCP"):
        with st.spinner("Negoziazione con il server..."):
            # Chiamiamo il tool 'register' tramite il protocollo MCP
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(esegui_mcp_tool("register", {
                "username": captain_name,
                "empire": "crimson"
            }))
            
            # Analisi risposta per estrarre il session_id
            resp_str = str(response)
            if "session_id" in resp_str:
                import re
                match = re.search(r'session_id[\"\'\s:=]+([a-zA-Z0-9\-_]+)', resp_str)
                if match:
                    st.session_state.session_id = match.group(1)
                    st.session_state.captain = captain_name
                    st.success(f"✅ Benvenuto a bordo, Capitano {captain_name}!")
                    st.rerun()
            
            st.write("📂 **Risultato Tool:**")
            st.write(response)

# FASE 2: COMANDI DI GIOCO
else:
    st.success(f"📡 COLLEGATO: Capitano {st.session_state.captain}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📡 SCANSIONE"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(esegui_mcp_tool("scan_sector", {
                "session_id": st.session_state.session_id
            }))
            st.json(res)
            
    with col2:
        if st.button("🛡️ STATO NAVE"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(esegui_mcp_tool("get_status", {
                "session_id": st.session_state.session_id
            }))
            st.json(res)

    if st.button("🔴 ABBANDONA PONTE"):
        st.session_state.session_id = None
        st.rerun()

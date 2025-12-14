from ui.login import render as render_login
import asyncio
import streamlit as st
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

st.set_page_config(page_title="AI Feed Assistant", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Get or create event loop and run
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

loop.run_until_complete(render_login())

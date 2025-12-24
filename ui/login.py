import streamlit as st
import streamlit.components.v1 as components
import httpx
import os

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL") + "/flow"
AUTH_ENDPOINT = f"{API_BASE_URL}/auth"


async def get_login_url():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{AUTH_ENDPOINT}/login")
            response.raise_for_status()
            data = response.json()
            return data.get("auth_url")
        except httpx.HTTPError as e:
            st.error(f"Error getting login URL: {str(e)}")
            return None


async def start_login():
    login_url = await get_login_url()

    if login_url:
        st.markdown(
            f"""
            <div style="text-align: center; margin: 20px 0;">
                <a href="{login_url}" target="_self">
                    <button style="
                        padding: 12px 24px;
                        background-color: #4285f4;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 16px;
                        font-weight: 500;
                        cursor: pointer;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    ">
                        🔐 Sign in with Google
                    </button>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )


async def complete_login():
    """Check if we just completed OAuth flow and verify authentication"""
    query_params = st.query_params

    # Check if we have a 'login' success parameter from OAuth redirect
    if "auth" in query_params and query_params["auth"] == "success":
        # Clear the query param
        st.query_params.clear()
        # Try to verify the session
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{AUTH_ENDPOINT}/check",
                    cookies=st.context.cookies if hasattr(st.context, 'cookies') else None
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("authenticated"):
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = data.get("user", {})
                        st.rerun()
            except Exception as e:
                st.error(f"Error verifying login: {str(e)}")

    # Clear any leftover OAuth code from URL
    if "code" in query_params or "state" in query_params:
        st.query_params.clear()


async def check_cached_session():
    """Check if user has a valid session cookie by calling /check endpoint via browser"""
    if st.session_state.get("logged_in"):
        return True

    # Use JavaScript to check authentication since cookies are in the browser
    result = components.html(
        f"""
        <script>
            console.log('Checking auth at: {AUTH_ENDPOINT}/check');
            fetch('{AUTH_ENDPOINT}/check', {{
                method: 'GET',
                credentials: 'include',  // Important: sends cookies with request
                headers: {{
                    'Accept': 'application/json',
                }}
            }})
            .then(response => {{
                console.log('Auth check response status:', response.status);
                if (response.ok) {{
                    return response.json();
                }} else {{
                    throw new Error('Not authenticated: ' + response.status);
                }}
            }})
            .then(data => {{
                console.log('Auth check success:', data);
                if (data.authenticated && data.user) {{
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: {{authenticated: true, user: data.user}}
                    }}, '*');
                }} else {{
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: {{authenticated: false}}
                    }}, '*');
                }}
            }})
            .catch(error => {{
                console.error('Auth check failed:', error);
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: {{authenticated: false}}
                }}, '*');
            }});
        </script>
        """,
        height=0,
    )

    # Handle the result from JavaScript
    if result and isinstance(result, dict):
        if result.get("authenticated"):
            st.session_state["logged_in"] = True
            st.session_state["user"] = result.get("user", {})
            # Trigger rerun to update the UI
            st.rerun()
        else:
            st.session_state["logged_in"] = False
            st.session_state["user"] = None

    return st.session_state.get("logged_in", False)


async def logout():
    components.html(
        f"""
        <script>
            fetch('{AUTH_ENDPOINT}/logout', {{
                method: 'POST',
                credentials: 'include',
                headers: {{
                    'Accept': 'application/json',
                }}
            }})
            .then(response => response.json())
            .then(data => {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: {{success: true}}
                }}, '*');
            }})
            .catch(error => {{
                console.error('Logout error:', error);
            }});
        </script>
        """,
        height=0,
    )

    st.session_state["logged_in"] = False
    st.session_state["user"] = None

    st.success("Logged out successfully!")
    st.rerun()


async def render():
    st.title("Welcome 👋")

    # Check for authentication on page load
    if not st.session_state.get("logged_in"):
        # Clear any leftover OAuth params
        await complete_login()

        # Check if user has valid cookie
        has_valid_token = await check_cached_session()

        if not has_valid_token:
            # Show login page
            st.write("Sign in to connect your calendar, mail, and news feed.")
            await start_login()
        else:
            # User is authenticated via cookie, show logged-in state
            user = st.session_state.get("user", {})
            render_logged_in_view(user)
    else:
        # User already logged in via session state
        user = st.session_state["user"]
        render_logged_in_view(user)


def render_logged_in_view(user: dict):
    """Render the view for logged-in users"""
    user_email = user.get("email", "User")
    user_name = user.get("name", user_email)
    user_picture = user.get("picture")

    # Create columns for user info and logout button
    col1, col2 = st.columns([3, 1])

    with col1:
        st.success(f"✅ Logged in as **{user_name}**")
        if user_email != user_name:
            st.caption(f"📧 {user_email}")

    with col2:
        import asyncio
        if st.button("🚪 Logout", type="secondary"):
            asyncio.run(logout())

    # Show user profile card
    if user_picture:
        st.image(user_picture, width=100)

    st.divider()

    # Placeholder for main app content
    st.subheader("🎯 Your Dashboard")
    st.info("Connected services: Gmail, Google Calendar")

    # Add tabs for different features
    tab1, tab2, tab3 = st.tabs(["📧 Email", "📅 Calendar", "📰 News Feed"])

    with tab1:
        st.write("Email integration coming soon...")

    with tab2:
        st.write("Calendar integration coming soon...")

    with tab3:
        st.write("News feed coming soon...")

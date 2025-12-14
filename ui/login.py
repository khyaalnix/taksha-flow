import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta

from app.client.oauth_client import get_login_url, handle_oauth_callback


from app.services.google_calendar_service import GoogleCalendarService
from app.services.gmail_service import GmailService

gmail_service = GmailService()
google_calendar_service = GoogleCalendarService()


def get_user_id_from_cookie():
    """Get user_id from browser cookie."""
    user_id = components.html(
        """
        <script>
            function getCookie(name) {
                const value = `; ${document.cookie}`;
                const parts = value.split(`; ${name}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
                return null;
            }
            const userId = getCookie('taksha_flow_user_id');
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: userId}, '*');
        </script>
        """,
        height=0,
    )
    return user_id


def save_user_id_to_cookie(user_id, days=30):
    """Save user_id to browser cookie with expiration."""
    components.html(
        f"""
        <script>
            const expires = new Date();
            expires.setTime(expires.getTime() + ({days} * 24 * 60 * 60 * 1000));
            document.cookie = 'taksha_flow_user_id={user_id}; expires=' + expires.toUTCString() + '; path=/; SameSite=Lax';
        </script>
        """,
        height=0,
    )


def clear_user_id_from_cookie():
    """Clear user_id from browser cookie."""
    components.html(
        """
        <script>
            document.cookie = 'taksha_flow_user_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax';
        </script>
        """,
        height=0,
    )



async def start_login():

    login_url = get_login_url()
    st.markdown(f"Click [here]({login_url}) to login with Google")


async def complete_login():
    query_params = st.query_params
    code = query_params.get("code")

    if code:
        result = handle_oauth_callback(code)
        user_id = result["user_info"]['id']

        await gmail_service.cache_user_token(
            user_id=user_id,
            access_token=result["tokens"]["access_token"],
            expires_in=result["tokens"]["expiry"],
        )

        await google_calendar_service.cache_user_token(
            user_id=user_id,
            access_token=result["tokens"]["access_token"],
            expires_in=result["tokens"]["expiry"],
        )

        st.session_state["logged_in"] = True
        st.session_state["user"] = result["user_info"]
        st.session_state["user_id"] = user_id

        # Save user_id to browser cookie for persistence (30 days)
        save_user_id_to_cookie(user_id, days=30)

        st.query_params.clear()
        st.rerun()  # Rerun to show logged-in state


async def check_cached_session():
    """Check if there's a valid cached token for the user."""
    # First check session state, then fall back to cookie
    user_id = st.session_state.get("user_id")

    if not user_id:
        # Try to get user_id from browser cookie
        user_id = get_user_id_from_cookie()

    if not user_id:
        return False

    # Check if token is still valid in cache
    gmail_token_valid = await gmail_service.check_if_valid_token(user_id)
    calendar_token_valid = await google_calendar_service.check_if_valid_token(user_id)

    if gmail_token_valid and calendar_token_valid:
        # Token is valid, restore session
        st.session_state["logged_in"] = True
        st.session_state["user_id"] = user_id
        if not st.session_state.get("user"):
            # We don't have user info in session, just store minimal info
            st.session_state["user"] = {"id": user_id}
        return True
    else:
        # Token expired or invalid, clear cookie
        if user_id:
            clear_user_id_from_cookie()

    return False


async def logout():
    """Logout user and clear all session data."""
    user_id = st.session_state.get("user_id")

    # Invalidate cached tokens
    if user_id:
        await gmail_service.invalidate_cache(user_id)
        await google_calendar_service.invalidate_cache(user_id)

    # Clear session state
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.session_state["user_id"] = None

    # Clear browser cookie
    clear_user_id_from_cookie()

    st.success("Logged out successfully!")
    st.rerun()


async def render():
    st.title("Welcome 👋")

    try:
        if not st.session_state.get("logged_in"):
            # Check if there's a valid cached token before prompting login
            has_valid_token = await check_cached_session()

            if not has_valid_token:
                st.write("Sign in to connect your calendar, mail, and news feed.")
                await start_login()
                await complete_login()
            else:
                # We have a valid cached token
                user = st.session_state.get("user", {})
                user_display = user.get("email") or user.get("id", "User")
                st.success(f"Welcome back! Logged in as {user_display}")

                # Add logout button
                if st.button("Logout"):
                    await logout()
        else:
            user = st.session_state["user"]
            user_display = user.get("email") or user.get("id", "User")
            st.success(f"Logged in as {user_display}")

            # Add logout button
            if st.button("Logout"):
                await logout()
    finally:
        # Close Redis connections before event loop closes
        await cleanup_redis_connections()


async def cleanup_redis_connections():
    """Close all Redis connections to prevent event loop errors."""
    try:
        if gmail_service.oauth_service.store._redis:
            await gmail_service.oauth_service.store._redis.aclose()
        if google_calendar_service.oauth_service.store._redis:
            await google_calendar_service.oauth_service.store._redis.aclose()
    except Exception as e:
        print(f"Error closing Redis connections: {e}")


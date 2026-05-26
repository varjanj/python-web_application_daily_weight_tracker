import streamlit as st
import logging
from database import supabase  # Reusing the existing supabase client from database.py

logger = logging.getLogger(__name__)

def sign_up_user(email: str, password: str) -> bool:
    """
    Registers a new user with email and password in Supabase.
    """
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
        # If user is created, response.user will contain user details
        if response.user:
            logger.info(f"User successfully registered: {email}")
            return True
        return False
    except Exception as e:
        logger.error(f"Sign up failed for {email}: {str(e)}")
        st.error(f"Registration failed: {str(e)}")
        return False

def sign_in_user(email: str, password: str) -> dict | None:
    """
    Authenticates an existing user. Returns the session data on success.
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        if response.session:
            logger.info(f"User successfully logged in: {email}")
            # Return user details (like ID and email)
            return {
                "user_id": response.user.id,
                "email": response.user.email
            }
        return None
    except Exception as e:
        logger.error(f"Sign in failed for {email}: {str(e)}")
        st.error(f"Login failed: Invalid email or password.")
        return None

def sign_out_user():
    """
    Logs out the current user and clears the session.
    """
    try:
        supabase.auth.sign_out()
        logger.info("User successfully logged out.")
        # Clear Streamlit session state keys related to auth
        if "user" in st.session_state:
            del st.session_state["user"]
        st.rerun()
    except Exception as e:
        logger.error(f"Sign out failed: {str(e)}")
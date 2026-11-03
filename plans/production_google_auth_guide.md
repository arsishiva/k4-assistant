# Technical Architecture: Production Google OAuth Authentication with Streamlit

To make Google Sign-In work in production (on Streamlit Community Cloud, AWS, GCP, Vercel, or custom servers), standard Google OAuth 2.0 must be configured using client credentials.

## Step 1: Google Cloud Console Setup
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project named `skatteverket-tax-assistant`.
3. Navigate to **APIs & Services > Credentials**.
4. Click **Create Credentials > OAuth client ID**.
5. Set Application Type to **Web application**.
6. Add Authorized Redirect URIs:
   - For local development: `http://localhost:8501/`
   - For production deployment: `https://your-app-name.streamlit.app/`
7. Copy your **Client ID** and **Client Secret**.

## Step 2: Streamlit Secret Configuration (`.streamlit/secrets.toml`)

Create `.streamlit/secrets.toml` (or enter in Streamlit Cloud App Settings):

```toml
[auth]
redirect_uri = "http://localhost:8501/"
cookie_secret = "your_random_secret_string_here"

[auth.google]
client_id = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

## Step 3: Python Package Integration
Use the official OAuth library for Streamlit (`authlib` / `streamlit-oauth`):

```bash
uv add authlib requests streamlit-oauth
```

## Step 4: Native Streamlit OAuth Code Integration (`src/app.py`)

Replace the simulated button handler with the production authentication flow:

```python
import streamlit as st
from streamlit_oauth import OAuth2Component

# Load credentials from secrets
CLIENT_ID = st.secrets["auth"]["google"]["client_id"]
CLIENT_SECRET = st.secrets["auth"]["google"]["client_secret"]
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, REVOKE_URL)

if "user_profile" not in st.session_state or not st.session_state.user_profile:
    result = oauth2.authorize_button(
        name="Sign in with Google",
        icon="https://www.google.com/favicon.ico",
        redirect_uri=st.secrets["auth"]["redirect_uri"],
        scope="openid email profile",
    )
    if result and "token" in result:
        # Extract user profile from ID token / userInfo endpoint
        st.session_state.user_profile = result["token"]
        st.rerun()
```

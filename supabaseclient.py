from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON = os.getenv("SUPABASE_ANON")  # Public key, safe to expose
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_KEY")  # Private key (⚠️ server-side only)

# Service role client (use only for admin/secure backend tasks)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)

# Public client (anon key, safe for user sessions)
supabase_public: Client = create_client(SUPABASE_URL, SUPABASE_ANON)

def get_user_client(access_token: str, refresh_token: str) -> Client:
    """
    Create a Supabase client authenticated as a specific user.
    This uses the anon key + restores the user's session.
    """
    client = create_client(SUPABASE_URL, SUPABASE_ANON)
    client.auth.set_session(access_token, refresh_token)
    return client

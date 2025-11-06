from typing import Optional
from supabase import create_client, Client
from app.core.config import get_settings

settings = get_settings()

# Global Supabase client
_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """
    Get Supabase client singleton.

    Returns:
        Supabase client instance
    """
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    return _supabase_client

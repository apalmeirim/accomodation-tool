from .auth import get_supabase_client

# Shared Supabase client
supabase = get_supabase_client()



def insert_attraction(user_id, name, lat, lon):
    """Insert a new tourist attraction for the current user."""
    return supabase.table("attractions").insert({
        "user_id": user_id,
        "name": name,
        "lat": lat,
        "lon": lon
    }).execute()


def get_user_attractions(user_id):
    """Retrieve all tourist attractions for the current user."""
    result = supabase.table("attractions").select("*").eq("user_id", user_id).execute()
    return result.data


def delete_attraction(attraction_id, user_id):
    """Delete a specific attraction owned by the user."""
    return supabase.table("attractions").delete().eq("id", attraction_id).eq("user_id", user_id).execute()


def insert_accommodation(user_id, name, lat, lon, price):
    """Insert a new accommodation for the current user."""
    return supabase.table("accommodations").insert({
        "user_id": user_id,
        "name": name,
        "lat": lat,
        "lon": lon,
        "price": price
    }).execute()


def get_user_accommodations(user_id):
    """Retrieve all accommodations for the current user."""
    result = supabase.table("accommodations").select("*").eq("user_id", user_id).execute()
    return result.data


def delete_accommodation(accommodation_id, user_id):
    """Delete a specific accommodation owned by the user."""
    return supabase.table("accommodations").delete().eq("id", accommodation_id).eq("user_id", user_id).execute()


def get_user_entries(table_name, user_id):
    """Generic fetch helper if you want to reuse one function."""
    result = supabase.table(table_name).select("*").eq("user_id", user_id).execute()
    return result.data
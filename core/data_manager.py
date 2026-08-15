import os
import toml
from supabase import create_client, Client
from core.logger_config import get_logger

logger = get_logger(__name__)

def get_supabase_client():
    path = os.path.join(".streamlit", "secrets.toml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo de secretos en {path}")
    secrets = toml.load(path)
    if "SUPABASE_URL" not in secrets or "SUPABASE_KEY" not in secrets:
        raise KeyError("SUPABASE_URL y SUPABASE_KEY deben estar en secrets.toml")
    
    return create_client(secrets["SUPABASE_URL"], secrets["SUPABASE_KEY"])

def update_user_stats(username_db, xp_gain, puntos_gain, nivel_nuevo, log_entry):
    supabase = get_supabase_client()
    
    # 1. Get current stats
    user = supabase.table("usuarios").select("xp, puntos").eq("username", username_db).single().execute().data
    
    # 2. Update user stats
    supabase.table("usuarios").update({
        "xp": user["xp"] + xp_gain,
        "puntos": user["puntos"] + puntos_gain,
        "nivel": nivel_nuevo
    }).eq("username", username_db).execute()
    
    # 3. Add to history
    log_entry["username"] = username_db
    supabase.table("historial").insert(log_entry).execute()

def redeem_reward(username_db, reward_data):
    supabase = get_supabase_client()
    
    # 1. Update points
    user = supabase.table("usuarios").select("puntos").eq("username", username_db).single().execute().data
    supabase.table("usuarios").update({
        "puntos": user["puntos"] - reward_data["coste"]
    }).eq("username", username_db).execute()
    
    # 2. Add to recompensas_usuario
    reward_data["username"] = username_db
    supabase.table("recompensas_usuario").insert(reward_data).execute()
    
    # 3. Add to history
    supabase.table("historial").insert({
        "username": username_db,
        "tipo": "recompensa_canjeada",
        "recompensa": reward_data["recompensa"],
        "coste": reward_data["coste"],
        "fecha": reward_data["fecha_canje"]
    }).execute()

def mark_reward_enjoyed(username_db, recompensa_id, fecha_disfrutada):
    supabase = get_supabase_client()
    
    # 1. Update reward status
    supabase.table("recompensas_usuario").update({
        "estado": "completed",
        "fecha_disfrutada": fecha_disfrutada
    }).eq("id", recompensa_id).execute()
    
    # 2. Add to history
    reward = supabase.table("recompensas_usuario").select("recompensa").eq("id", recompensa_id).single().execute().data
    supabase.table("historial").insert({
        "username": username_db,
        "tipo": "recompensa_disfrutada",
        "recompensa": reward["recompensa"],
        "fecha": fecha_disfrutada
    }).execute()

def get_all_data():
    """
    Simulates loading the legacy 'datos' structure from Supabase for compatibility.
    NOTE: This is not scalable and should be replaced by granular data fetching.
    """
    supabase = get_supabase_client()
    
    # Fetch all necessary data from tables
    usuarios_list = supabase.table("usuarios").select("*").execute().data
    tareas_list = supabase.table("tareas").select("*").execute().data
    recompensas_list = supabase.table("recompensas").select("*").execute().data
    historial_list = supabase.table("historial").select("*").execute().data
    recompensas_usuario_list = supabase.table("recompensas_usuario").select("*").execute().data
    niveles_list = supabase.table("niveles").select("*").execute().data

    # Reconstruct the legacy structure
    datos = {
        "usuarios": {},
        "cuentas": {},
        "tareas_personalizadas": [t for t in tareas_list if t["personalizada"]],
        "recompensas_canjeadas": [], # Need to derive this from recompensas_usuario or legacy logic
        "niveles": niveles_list
    }

    # Map users and accounts
    for u in usuarios_list:
        username = u["username"]
        display_name = u["name"]
        
        datos["cuentas"][username] = {
            "name": display_name,
            "email": u["email"],
            "password": u["password"],
            "role": u["role"],
            "logged_in": u["logged_in"],
            "failed_login_attempts": u["failed_login_attempts"]
        }
        
        datos["usuarios"][display_name] = {
            "xp": u["xp"],
            "puntos": u["puntos"],
            "nivel": u["nivel"],
            "historial": [],
            "recompensas": []
        }

    # Reconstruct history
    for h in historial_list:
        username = h["username"]
        # Find display name
        display_name = next((u["name"] for u in usuarios_list if u["username"] == username), None)
        if display_name:
            datos["usuarios"][display_name]["historial"].append(h)

    # Reconstruct user rewards
    for ru in recompensas_usuario_list:
        username = ru["username"]
        display_name = next((u["name"] for u in usuarios_list if u["username"] == username), None)
        if display_name:
            datos["usuarios"][display_name]["recompensas"].append(ru)

    return datos

# --- Legacy compatibility (to be removed) ---
def cargar_datos():
    return get_all_data()

def guardar_datos(datos):
    logger.warning("guardar_datos() llamado. Refactor a granular updates required.")
    pass

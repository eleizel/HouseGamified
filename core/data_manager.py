import json
import os

DATA_FILE = "gamificacion_datos.json"

INITIAL_ACCOUNTS = {
    "sergio": {
        "name": "Sergio",
        "email": "sergio@house-gamified.local",
        "password": "$2b$12$qjmwcaPLNzilzPTIR18jyeXtz1STyQDk84wg3.ONonqVF3kC/qEFy",
        "role": "admin",
    },
    "raquel": {
        "name": "Raquel",
        "email": "raquel@house-gamified.local",
        "password": "$2b$12$qjmwcaPLNzilzPTIR18jyeXtz1STyQDk84wg3.ONonqVF3kC/qEFy",
        "role": "admin",
    },
}

# Estructura por defecto
DEFAULT_DATA = {
    "usuarios": {
        "Sergio": {"xp": 0, "puntos": 0, "nivel": 1, "historial": [], "recompensas": []},
        "Raquel": {"xp": 0, "puntos": 0, "nivel": 1, "historial": [], "recompensas": []},
    },
    "recompensas_canjeadas": [],
    "cuentas": INITIAL_ACCOUNTS,
    "tareas_personalizadas": [],
}


def cargar_datos():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      datos = json.load(f)
      datos.setdefault("cuentas", INITIAL_ACCOUNTS.copy())
      datos.setdefault("tareas_personalizadas", [])
      for username, cuenta in INITIAL_ACCOUNTS.items():
        datos["cuentas"].setdefault(username, cuenta)
      
      # Migración: los datos anteriores no tenían una moneda separada.
      usuarios_sin_recompensas = {
          nombre for nombre, usuario in datos.get("usuarios", {}).items()
          if "recompensas" not in usuario
      }
      for usuario in datos.get("usuarios", {}).values():
        usuario.setdefault("puntos", usuario.get("xp", 0))
        usuario.setdefault("recompensas", [])
      for recompensa in datos.get("recompensas_canjeadas", []):
        nombre_usuario = recompensa.get("usuario")
        if nombre_usuario not in usuarios_sin_recompensas:
          continue
        usuario = datos["usuarios"].get(nombre_usuario)
        if usuario is not None:
          usuario["recompensas"].append({
              "recompensa": recompensa.get("recompensa", "Recompensa"),
              "coste": recompensa.get("coste", 0),
              "fecha_canje": recompensa.get("fecha", ""),
              "estado": "ongoing",
          })
          usuario["historial"].append({
              "tipo": "recompensa_canjeada",
              "recompensa": recompensa.get("recompensa", "Recompensa"),
              "coste": recompensa.get("coste", 0),
              "fecha": recompensa.get("fecha", ""),
          })
      return datos
  return DEFAULT_DATA


def guardar_datos(datos):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=4)

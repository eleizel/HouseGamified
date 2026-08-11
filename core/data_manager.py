import json
import os
from core.logger_config import get_logger

logger = get_logger(__name__)

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


def cargar_datos_local():
  logger.info(f"Cargando datos locales desde {DATA_FILE}...")
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
      logger.info("Datos locales cargados y migrados exitosamente.")
      return datos
  logger.info("Archivo de datos locales no encontrado. Usando DEFAULT_DATA.")
  return DEFAULT_DATA


def guardar_datos_local(datos):
  logger.info(f"Guardando datos locales en {DATA_FILE}...")
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=4)
  logger.info("Datos guardados localmente con éxito.")



import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

def cargar_datos():
    logger.info("Intentando cargar datos desde Google Sheets...")
    try:
        conn = st.connection('gsheets', type=GSheetsConnection)
        df = conn.read(ttl=0)
        if df is not None and not df.empty and 'key' in df.columns and 'value' in df.columns:
            datos = {}
            for _, row in df.iterrows():
                key = str(row['key'])
                val_str = str(row['value'])
                try:
                    datos[key] = json.loads(val_str)
                except Exception:
                    datos[key] = val_str
            datos.setdefault('cuentas', INITIAL_ACCOUNTS.copy())
            datos.setdefault('tareas_personalizadas', [])
            for username, cuenta in INITIAL_ACCOUNTS.items():
                datos['cuentas'].setdefault(username, cuenta)
            for usuario in datos.get('usuarios', {}).values():
                usuario.setdefault('puntos', usuario.get('xp', 0))
                usuario.setdefault('recompensas', [])
            logger.info("Datos cargados exitosamente desde Google Sheets.")
            return datos
    except Exception as e:
        logger.warning(f"Google Sheets no disponible o sin conexión ({e}). Cargando desde JSON local.")
        st.sidebar.warning(f'Cargando desde JSON local (Google Sheets no configurado o sin conexion: {e})')
    return cargar_datos_local()

def guardar_datos(datos):
    logger.info("Iniciando guardado de datos...")
    guardar_datos_local(datos)
    try:
        conn = st.connection('gsheets', type=GSheetsConnection)
        rows = []
        for key, val in datos.items():
            rows.append({
                'key': key,
                'value': json.dumps(val, ensure_ascii=False)
            })
        df = pd.DataFrame(rows)
        try:
            conn.update(worksheet='GamificacionDatos', data=df)
            logger.info("Datos actualizados en Google Sheets correctamente.")
        except Exception:
            try:
                conn.create(worksheet='GamificacionDatos', data=df)
                logger.info("Datos creados en Google Sheets correctamente.")
            except Exception as e:
                logger.info(f"Google Sheets es público/solo lectura (datos guardados localmente): {e}")
    except Exception as e:
        logger.info(f"Google Sheets no disponible para escritura (datos guardados localmente): {e}")

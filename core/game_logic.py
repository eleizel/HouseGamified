from datetime import datetime
from core.logger_config import get_logger
from core.data_manager import get_supabase_client

logger = get_logger(__name__)

# Period configuration
PERIODOS = ["daily", "weekly", "monthly", "yearly"]
NOMBRES_PERIODOS = {
    "daily": "Diaria",
    "weekly": "Semanal",
    "monthly": "Mensual",
    "yearly": "Anual",
}
PERIODO_MAP = {
    "daily": "☀️ Tareas Diarias",
    "weekly": "📅 Tareas Semanales",
    "monthly": "🗓️ Tareas Mensuales",
    "yearly": "🏆 Tareas Anuales (Grandes Desafíos)",
}

def fetch_db_data():
    """Fetches reference data from Supabase."""
    supabase = get_supabase_client()
    niveles = supabase.table("niveles").select("*").order("nivel").execute().data
    tareas = supabase.table("tareas").select("*").execute().data
    recompensas = supabase.table("recompensas").select("*").execute().data
    return niveles, tareas, recompensas

# Data populated on module load
NIVELES, TAREAS_DB, RECOMPENSAS = fetch_db_data()

def get_tareas_structured():
    """Organizes tasks from DB into categories."""
    structured = {nombre: [] for nombre in PERIODO_MAP.values()}
    for t in TAREAS_DB:
        cat_nombre = PERIODO_MAP.get(t["periodo"])
        if cat_nombre:
            structured[cat_nombre].append(t)
    return structured

TAREAS = get_tareas_structured()

def calcular_nivel(xp):
  """Calcula el nivel usando la progresión de la DB."""
  logger.debug(f"Calculando nivel para XP: {xp}")
  nivel_actual = NIVELES[0]
  for nivel in NIVELES:
    if xp >= nivel["xp_minimo"]:
      nivel_actual = nivel
    else:
      break
  return (
      nivel_actual["nivel"],
      nivel_actual["titulo"],
      nivel_actual["xp_siguiente"],
  )

def periodo_tarea(categoria, momento):
  """Devuelve la clave del periodo vigente para una tarea periódica."""
  if categoria not in PERIODO_MAP.values():
    return None
  
  # Reverse map
  periodo_key = next(k for k, v in PERIODO_MAP.items() if v == categoria)
  
  if periodo_key == "daily":
    return momento.strftime("%Y-%m-%d")
  if periodo_key == "weekly":
    calendario_iso = momento.isocalendar()
    return f"{calendario_iso.year}-W{calendario_iso.week:02d}"
  if periodo_key == "monthly":
    return momento.strftime("%Y-%m")
  return momento.strftime("%Y")  # Anual

def completaciones_tarea_en_periodo(datos, nombre_tarea, categoria, momento):
  """Devuelve las completaciones actuales junto al jugador que las hizo."""
  periodo_actual = periodo_tarea(categoria, momento)
  completaciones = []
  for nombre_usuario, usuario in datos["usuarios"].items():
    for log in usuario.get("historial", []):
      if log.get("tarea") != nombre_tarea:
        continue
      if log.get("categoria") and log["categoria"] != categoria:
        continue
      if periodo_actual is None:
        completaciones.append(nombre_usuario)
        continue
      try:
        fecha_log = datetime.strptime(log["fecha"][:16], "%Y-%m-%d %H:%M")
      except (KeyError, TypeError, ValueError):
        continue
      if periodo_tarea(categoria, fecha_log) == periodo_actual:
        completaciones.append(nombre_usuario)
  return completaciones

def veces_completada_en_periodo(datos, nombre_tarea, categoria, momento):
  return len(
      completaciones_tarea_en_periodo(datos, nombre_tarea, categoria, momento)
  )

def limite_tarea(tarea):
  """Devuelve el máximo de completaciones permitidas para una tarea."""
  return max(1, int(tarea.get("max_repeticiones", 1)))

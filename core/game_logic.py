import json
import os
import copy
from datetime import datetime
from core.logger_config import get_logger

logger = get_logger(__name__)

LEVELS_FILE = "niveles.json"

BASE_TAREAS = {
    "☀️ Tareas Diarias": [
        {"nombre": "Barrer el suelo", "xp": 10},
        {"nombre": "Fregar cacharros y biberones", "xp": 15},
        {"nombre": "Limpiar el arenero", "xp": 10},
        {"nombre": "Ventilar la casa", "xp": 5},
        {"nombre": "Hacer la cama", "xp": 10},
        {"nombre": "Despejar la mesa baja del salón", "xp": 10},
        {"nombre": "Limpiar la encimera", "xp": 10},
        {"nombre": "Limpiar la vitro", "xp": 10},
    ],
    "📅 Tareas Semanales": [
        {"nombre": "Cambiar las sábanas de la cama y de la cuna", "xp": 40},
        {"nombre": "Limpiar el acuario", "xp": 50},
        {"nombre": "Desinfectar el arenero", "xp": 30},
        {"nombre": "Limpiar el baño completo", "xp": 50},
        {"nombre": "Limpiar y desinfectar el fregadero", "xp": 25},
        {
            "nombre": "Limpiar la cocina (incluyendo puertas de armarios)",
            "xp": 50,
        },
        {"nombre": "Limpiar el sofá y rascador del gato (aspirar)", "xp": 30},
        {"nombre": "Barrer y fregar la planta de arriba", "xp": 40},
        {"nombre": "Quitar el polvo del despacho", "xp": 20},
        {"nombre": "Quitar el polvo del dormitorio", "xp": 20},
        {"nombre": "Quitar el polvo del salón", "xp": 20},
    ],
    "🗓️ Tareas Mensuales": [
        {"nombre": "Limpiar horno, microondas y freidora de aire", "xp": 80},
        {"nombre": "Lavar las toallas", "xp": 30},
        {"nombre": "Quitar el polvo de puertas y ventanas", "xp": 40},
        {"nombre": "Limpiar las lámparas y ventiladores", "xp": 40},
        {"nombre": "Limpiar el recogedor", "xp": 10},
        {"nombre": "Limpiar el baño de arriba completo", "xp": 50},
        {"nombre": "Limpiar los rodapiés", "xp": 40},
        {"nombre": "Limpiar los enchufes e interruptores", "xp": 30},
        {"nombre": "Revisar frigorífico y tirar comida caducada", "xp": 40},
        {"nombre": "Limpiar los pomos de las puertas", "xp": 20},
        {"nombre": "Limpiar los azulejos del baño y cocina", "xp": 80},
        {"nombre": "Quitar el polvo de los radiadores", "xp": 40},
    ],
    "🏆 Tareas Anuales (Grandes Desafíos)": [
        {"nombre": "Lavar las cortinas", "xp": 100},
        {"nombre": "Limpieza a fondo de la cocina", "xp": 200},
        {"nombre": "Ordenar y limpiar el trastero", "xp": 300},
        {"nombre": "Pintar las zonas deterioradas de la pared", "xp": 250},
        {"nombre": "Limpiar las ventanas por dentro y por fuera", "xp": 150},
        {"nombre": "Limpiar el frigorífico a fondo", "xp": 150},
        {"nombre": "Girar el colchón", "xp": 50},
        {"nombre": "Limpiar las persianas", "xp": 100},
        {"nombre": "Limpiar los filtros del aire acondicionado", "xp": 80},
        {"nombre": "Quitar las telarañas de esquinas y techo", "xp": 50},
        {"nombre": "Revisar y tirar juguetes", "xp": 30},
        {"nombre": "Limpiar el colchón", "xp": 60},
        {"nombre": "Mover mueble de la televisión y limpiar detrás", "xp": 100},
        {"nombre": "Descongelar el congelador", "xp": 150},
        {"nombre": "Mover el frigorífico y limpiar detrás", "xp": 100},
    ],
}

# Inicializar valores por defecto para tareas bases
for tareas_categoria in BASE_TAREAS.values():
  for tarea in tareas_categoria:
    tarea.setdefault("repetible", False)
    tarea.setdefault("max_repeticiones", 1)

# TAREAS se inicializa como una copia profunda de BASE_TAREAS
TAREAS = copy.deepcopy(BASE_TAREAS)

RECOMPENSAS = [
    {"nombre": "🎬 Elegir película / serie el fin de semana", "coste": 100},
    {"nombre": "🍕 Pedir comida a domicilio favorita", "coste": 300},
    {"nombre": "🎟️ Pase 'Libre de tarea diaria' por 1 día", "coste": 400},
    {"nombre": "☕ Tarde libre + café/capricho asegurado", "coste": 600},
    {"nombre": "🍽️ Cena especial en restaurante", "coste": 1200},
    {"nombre": "🎁 Capricho personal o regalo mensual", "coste": 2500},
]

PERIODOS = ["daily", "weekly", "monthly", "yearly"]
NOMBRES_PERIODOS = {
    "daily": "Diaria",
    "weekly": "Semanal",
    "monthly": "Mensual",
    "yearly": "Anual",
}


def cargar_niveles():
  logger.info(f"Cargando niveles desde {LEVELS_FILE}...")
  with open(LEVELS_FILE, "r", encoding="utf-8") as f:
    niveles = json.load(f)["niveles"]
    logger.info(f"Se cargaron {len(niveles)} niveles exitosamente.")
    return niveles


NIVELES = cargar_niveles()


def calcular_nivel(xp):
  """Calcula el nivel usando la progresión configurable de niveles.json."""
  logger.debug(f"Calculando nivel para XP: {xp}")
  nivel_actual = NIVELES[0]
  for nivel in NIVELES:
    if xp >= nivel["xp_minimo"]:
      nivel_actual = nivel
    else:
      break
  logger.debug(f"Nivel calculado: {nivel_actual['nivel']} ({nivel_actual['titulo']})")
  return (
      nivel_actual["nivel"],
      nivel_actual["titulo"],
      nivel_actual["xp_siguiente"],
  )


def periodo_tarea(categoria, momento):
  """Devuelve la clave del periodo vigente para una tarea periódica."""
  categorias = list(TAREAS.keys())
  if categoria not in categorias[:4]:
    return None
  indice_categoria = categorias.index(categoria)
  if indice_categoria == 0:  # Diaria
    return momento.strftime("%Y-%m-%d")
  if indice_categoria == 1:  # Semanal: lunes a domingo (semana ISO)
    calendario_iso = momento.isocalendar()
    return f"{calendario_iso.year}-W{calendario_iso.week:02d}"
  if indice_categoria == 2:  # Mensual
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
  if not tarea.get("repetible", tarea.get("repeatable", False)):
    return 1
  return max(1, int(tarea.get("max_repeticiones", 1)))


def incorporar_tareas_personalizadas(datos):
  """Añade las tareas guardadas a sus categorías periódicas."""
  logger.info("Incorporando tareas personalizadas...")
  # Restaurar las tareas bases en la misma instancia de diccionario (mutacion in-place)
  for cat in BASE_TAREAS:
    TAREAS[cat] = copy.deepcopy(BASE_TAREAS[cat])
  categorias_periodos = dict(zip(PERIODOS, list(TAREAS.keys())[:4]))
  count = 0
  for tarea in datos.get("tareas_personalizadas", []):
    categoria = categorias_periodos.get(tarea.get("periodo"))
    if not categoria or not tarea.get("id"):
      continue
    TAREAS[categoria].append({
        "id": tarea["id"],
        "nombre": tarea.get("nombre", "Tarea sin nombre"),
        "xp": int(tarea.get("xp", 0)),
        "repetible": bool(tarea.get("repetible", False)),
        "max_repeticiones": max(1, int(tarea.get("max_repeticiones", 1))),
        "personalizada": True,
    })
    count += 1
  logger.info(f"Se incorporaron {count} tareas personalizadas correctamente.")

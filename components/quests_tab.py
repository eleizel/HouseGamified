import streamlit as st
from datetime import datetime
from core.data_manager import cargar_datos, guardar_datos
from core.game_logic import (
    TAREAS,
    limite_tarea,
    completaciones_tarea_en_periodo,
    veces_completada_en_periodo,
    calcular_nivel,
)
from core.logger_config import get_logger

logger = get_logger(__name__)


@st.dialog("Confirmar finalización de misión")
def confirmar_tarea_dialog(tarea, categoria, usuario_actual):
  st.write(f"¿Seguro que has completado la misión **{tarea['nombre']}**?")
  st.write(f"Esto te otorgará ⭐ **{tarea['xp']} XP** y puntos de recompensa.")
  from core.data_manager import update_user_stats
  
  col1, col2 = st.columns(2)
  with col1:
    if st.button("Sí, confirmar", use_container_width=True, type="primary"):
      logger.info(f"Usuario {usuario_actual} confirmó completación de misión: {tarea['nombre']} ({categoria}), XP: {tarea['xp']}")

      # Determine username_db
      datos = st.session_state.datos
      username_db = next((u for u, c in datos["cuentas"].items() if c["name"] == usuario_actual), usuario_actual.lower())

      # 1. Update stats in DB
      info_user = datos["usuarios"][usuario_actual]
      xp_nuevo = info_user["xp"] + tarea["xp"]
      puntos_nuevo = info_user["puntos"] + tarea["xp"]
      nivel_nuevo, _, _ = calcular_nivel(xp_nuevo)

      log_entry = {
          "tipo": "tarea_completada",
          "tarea": tarea["nombre"],
          "xp": tarea["xp"],
          "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
          "categoria": categoria,
      }

      update_user_stats(username_db, tarea["xp"], tarea["xp"], nivel_nuevo, log_entry)

      # 2. Update local session state
      info_user["xp"] = xp_nuevo
      info_user["puntos"] = puntos_nuevo
      info_user["nivel"] = nivel_nuevo
      info_user["historial"].append(log_entry)

      logger.info(f"Misión completada registrada para {usuario_actual}. Nuevo XP: {info_user['xp']}, Nivel: {info_user['nivel']}")
      st.balloons()
      st.success(f"¡+{tarea['xp']} XP y puntos para {usuario_actual}!")
      st.rerun()
  with col2:
    if st.button("Cancelar", use_container_width=True):
      logger.debug(f"Usuario {usuario_actual} canceló la confirmación de misión.")
      st.rerun()


def render_quests_tab(datos, usuario_actual):
  st.header("📋 Tablón de Misiones")
  categoria = st.selectbox("Selecciona Categoría", list(TAREAS.keys()))
  st.subheader(categoria)

  ahora = datetime.now()
  for idx, tarea in enumerate(TAREAS[categoria]):
    max_repeticiones = limite_tarea(tarea)
    jugadores_completaron = completaciones_tarea_en_periodo(
        datos, tarea["nombre"], categoria, ahora
    )
    veces_completada = len(jugadores_completaron)
    completada_en_periodo = veces_completada >= max_repeticiones
    conteo_jugadores = {}
    for jugador in jugadores_completaron:
      conteo_jugadores[jugador] = conteo_jugadores.get(jugador, 0) + 1
    resumen_jugadores = ", ".join(
        f"{jugador} ({cantidad})" if cantidad > 1 else jugador
        for jugador, cantidad in conteo_jugadores.items()
    )
    texto_boton = (
        f"Completada por {resumen_jugadores}"
        if completada_en_periodo
        else f"Completar ({veces_completada}/{max_repeticiones})"
    )
    col1, col2, col3 = st.columns([4, 1, 1.5])
    with col1:
      st.markdown(f"**{tarea['nombre']}**")
    with col2:
      st.markdown(f"⭐ `{tarea['xp']} XP`")
    with col3:
      if st.button(
          f"✅ {texto_boton}",
          key=f"btn_{categoria}_{idx}",
          disabled=completada_en_periodo,
      ):
        confirmar_tarea_dialog(tarea, categoria, usuario_actual)
    st.divider()

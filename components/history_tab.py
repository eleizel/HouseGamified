import streamlit as st
from datetime import datetime


def render_history_tab(datos):
  st.header("Historial de todos los jugadores")
  acciones = []
  for jugador, datos_jugador in datos["usuarios"].items():
    for log in datos_jugador.get("historial", []):
      try:
        fecha_orden = datetime.strptime(log.get("fecha", "")[:16], "%Y-%m-%d %H:%M")
      except (TypeError, ValueError):
        fecha_orden = datetime.min
      acciones.append((fecha_orden, jugador, log))

  acciones.sort(key=lambda accion: accion[0], reverse=True)
  if acciones:
    for _, jugador, log in acciones:
      tipo = log.get("tipo", "tarea_completada")
      if tipo == "recompensa_canjeada":
        st.write(
            f"**{log['fecha']}** — **{jugador}** canjeó la recompensa "
            f"**{log['recompensa']}** (`-{log['coste']} puntos`)"
        )
      elif tipo == "recompensa_disfrutada":
        st.write(
            f"**{log['fecha']}** — **{jugador}** disfrutó la recompensa "
            f"**{log['recompensa']}**"
        )
      else:
        st.write(
            f"**{log['fecha']}** — **{jugador}** completó {log['tarea']} "
            f"(`+{log['xp']} XP y puntos`)"
        )
  else:
    st.info("Aún no hay acciones registradas.")

import streamlit as st
from core.game_logic import calcular_nivel


def render_ranking_tab(datos):
  st.header("🏆 Tabla de Clasificación")
  ranking_data = []
  for user, info in datos["usuarios"].items():
    lvl, tit, _ = calcular_nivel(info["xp"])
    ranking_data.append({
        "Jugador": user,
        "XP Total": info["xp"],
        "Nivel": f"Nivel {lvl} - {tit}",
        "Misiones Completadas": len(info["historial"]),
    })
  st.table(sorted(ranking_data, key=lambda x: x["XP Total"], reverse=True))

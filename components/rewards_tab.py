import streamlit as st
from datetime import datetime
from core.data_manager import guardar_datos
from core.game_logic import RECOMPENSAS


def render_rewards_tab(datos, usuario_actual):
  st.header("🛍️ Tienda de Recompensas")
  info_user = datos["usuarios"][usuario_actual]
  puntos_actual = info_user["puntos"]
  st.write(f"Puntos disponibles de **{usuario_actual}**: `{puntos_actual} puntos`")

  for idx, rec in enumerate(RECOMPENSAS):
    col1, col2, col3 = st.columns([4, 1, 1.5])
    with col1:
      st.markdown(f"**{rec['nombre']}**")
    with col2:
      st.markdown(f"🏷️ `{rec['coste']} puntos`")
    with col3:
      puede_comprar = puntos_actual >= rec["coste"]
      if st.button(f"🛒 Canjear", key=f"rec_{idx}", disabled=not puede_comprar):
        info_user["puntos"] -= rec["coste"]
        fecha_canje = datetime.now().strftime("%Y-%m-%d %H:%M")
        info_user["recompensas"].append({
            "recompensa": rec["nombre"],
            "coste": rec["coste"],
            "fecha_canje": fecha_canje,
            "estado": "ongoing",
        })
        info_user["historial"].append({
            "tipo": "recompensa_canjeada",
            "recompensa": rec["nombre"],
            "coste": rec["coste"],
            "fecha": fecha_canje,
        })
        datos["recompensas_canjeadas"].append({
            "usuario": usuario_actual,
            "recompensa": rec["nombre"],
            "coste": rec["coste"],
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        guardar_datos(datos)
        st.snow()
        st.success(f"¡Recompensa '{rec['nombre']}' canjeada!")
        st.rerun()
    st.divider()

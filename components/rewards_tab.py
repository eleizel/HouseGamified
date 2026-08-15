from core.data_manager import redeem_reward
from core.game_logic import RECOMPENSAS
from core.logger_config import get_logger
from datetime import datetime
import streamlit as st

logger = get_logger(__name__)


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
        logger.info(f"Usuario {usuario_actual} está canjeando recompensa: {rec['nombre']} (coste: {rec['coste']} puntos)")

        datos = st.session_state.datos
        username_db = next((u for u, c in datos["cuentas"].items() if c["name"] == usuario_actual), usuario_actual.lower())

        info_user["puntos"] -= rec["coste"]
        fecha_canje = datetime.now().strftime("%Y-%m-%d %H:%M")

        reward_data = {
            "recompensa": rec["nombre"],
            "coste": rec["coste"],
            "fecha_canje": fecha_canje,
            "estado": "ongoing",
        }

        # 1. Update in DB
        redeem_reward(username_db, reward_data)

        # 2. Update local state
        info_user["recompensas"].append(reward_data)
        info_user["historial"].append({
            "tipo": "recompensa_canjeada",
            "recompensa": rec["nombre"],
            "coste": rec["coste"],
            "fecha": fecha_canje,
        })

        logger.info(f"Recompensa '{rec['nombre']}' canjeada con éxito por {usuario_actual}. Puntos restantes: {info_user['puntos']}")
        st.snow()
        st.success(f"¡Recompensa '{rec['nombre']}' canjeada!")
        st.rerun()
    st.divider()

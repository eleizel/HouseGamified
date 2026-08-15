import streamlit as st
import bcrypt
from datetime import datetime
from core.data_manager import guardar_datos
from core.game_logic import calcular_nivel
from core.logger_config import get_logger

logger = get_logger(__name__)


def render_sidebar(datos, username, authenticator):
  cuenta_actual = datos["cuentas"][username]
  usuario_actual = cuenta_actual["name"]

  # Sidebar - Selección de Usuario
  st.sidebar.title("🎮 Perfil de Jugador")
  st.sidebar.write(f"¡Bienvenido/a  {usuario_actual}!")
  try:
    authenticator.logout("Cerrar sesión", location="sidebar")
  except TypeError:
    authenticator.logout("Cerrar sesión", "sidebar")

  if cuenta_actual.get("role") == "admin":
    with st.sidebar.expander("Administración", expanded=False):
      nuevo_usuario = st.text_input("Nombre del nuevo jugador:")
      nueva_contrasena = st.text_input(
          "Contraseña del nuevo jugador:", type="password"
      )
      if st.button("Crear jugador") and nuevo_usuario and nueva_contrasena:
        nombre_jugador = nuevo_usuario.strip()
        username_nuevo = nombre_jugador.lower().replace(" ", "_")
        if nombre_jugador in datos["usuarios"] or username_nuevo in datos["cuentas"]:
          st.error("Ese jugador ya existe.")
        else:
          datos["usuarios"][nombre_jugador] = {
              "xp": 0,
              "puntos": 0,
              "nivel": 1,
              "historial": [],
              "recompensas": [],
          }
          datos["cuentas"][username_nuevo] = {
              "name": nombre_jugador,
              "email": f"{username_nuevo}@house-gamified.local",
              "password": bcrypt.hashpw(
                  nueva_contrasena.encode("utf-8"), bcrypt.gensalt()
              ).decode("utf-8"),
              "role": "player",
          }
          guardar_datos(datos)
          logger.info(f"Nuevo jugador creado: {nombre_jugador} (username: {username_nuevo})")
          st.success(f"Jugador {nombre_jugador} creado.")
          st.rerun()

  info_user = datos["usuarios"][usuario_actual]
  xp_actual = info_user["xp"]
  puntos_actual = info_user["puntos"]
  nivel, titulo_nivel, xp_siguiente = calcular_nivel(xp_actual)

  st.sidebar.markdown("---")
  st.sidebar.subheader(f"👤 {usuario_actual}")
  st.sidebar.write(f"**Nivel {nivel}:** {titulo_nivel}")
  progreso = 1.0 if xp_siguiente is None else min(xp_actual / xp_siguiente, 1.0)
  st.sidebar.progress(progreso)
  if xp_siguiente is None:
    st.sidebar.caption("Nivel máximo alcanzado (99)")
  else:
    st.sidebar.caption(f"Siguiente nivel: {xp_actual} / {xp_siguiente} XP")
  st.sidebar.write(f"**XP Total:** {xp_actual} pts")
  st.sidebar.write(f"**Puntos para recompensas:** {puntos_actual} pts")

  st.sidebar.subheader("Recompensas en curso")
  recompensas_en_curso = [
      recompensa for recompensa in info_user["recompensas"]
      if recompensa.get("estado") == "ongoing"
  ]
  if recompensas_en_curso:
    for idx, recompensa in enumerate(recompensas_en_curso):
      st.sidebar.write(
          f"**{recompensa['recompensa']}**  " +
          f"(canjeada: {recompensa['fecha_canje']})"
      )
      if st.sidebar.button(
          "Marcar como disfrutada",
          key=f"disfrutar_{usuario_actual}_{idx}",
      ):
        datos = st.session_state.datos
        username_db = next((u for u, c in datos["cuentas"].items() if c["name"] == usuario_actual), usuario_actual.lower())

        fecha_disfrutada = datetime.now().strftime("%Y-%m-%d %H:%M")

        # 1. Update in DB
        mark_reward_enjoyed(username_db, recompensa["id"], fecha_disfrutada)

        # 2. Update local state
        recompensa["estado"] = "completed"
        recompensa["fecha_disfrutada"] = fecha_disfrutada
        info_user["historial"].append({
            "tipo": "recompensa_disfrutada",
            "recompensa": recompensa["recompensa"],
            "fecha": fecha_disfrutada,
        })

        logger.info(f"Recompensa marcada como disfrutada por {usuario_actual}: {recompensa['recompensa']}")
        st.sidebar.success("Recompensa marcada como disfrutada.")
        st.rerun()

  else:
    st.sidebar.caption("No hay recompensas pendientes.")

  st.sidebar.subheader("Últimas recompensas disfrutadas")
  recompensas_disfrutadas = [
      recompensa for recompensa in info_user["recompensas"]
      if recompensa.get("estado") == "completed"
  ]
  if recompensas_disfrutadas:
    for recompensa in reversed(recompensas_disfrutadas[-3:]):
      st.sidebar.write(
          f"~~{recompensa['recompensa']}~~  " +
          f"({recompensa.get('fecha_disfrutada', 'sin fecha')})"
      )
  else:
    st.sidebar.caption("Aún no has disfrutado recompensas.")

import streamlit as st
import streamlit_authenticator as stauth

# Core imports
from core.data_manager import cargar_datos
from core.logger_config import get_logger

logger = get_logger(__name__)
logger.info("Iniciando aplicación Streamlit de HouseGamified...")

# Components imports
from components.sidebar import render_sidebar
from components.quests_tab import render_quests_tab
from components.rewards_tab import render_rewards_tab
from components.history_tab import render_history_tab
from components.ranking_tab import render_ranking_tab
from components.admin_tab import render_admin_tab

# Configuración de la página
st.set_page_config(
    page_title="Gestor de Tareas Gamificado",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicialización de datos
if "datos" not in st.session_state:
  st.session_state.datos = cargar_datos()

datos = st.session_state.datos

# Asegurarse de que todos los usuarios tengan campos necesarios
for usuario in datos.get("usuarios", {}).values():
  usuario.setdefault("puntos", usuario.get("xp", 0))
  usuario.setdefault("recompensas", [])

# Configuración del autenticador
authenticator = stauth.Authenticate(
    {"usernames": datos["cuentas"]},
    "house_gamified_auth",
    "house_gamified_cookie_key_7f4c2d9a8b1e6f3c",
    cookie_expiry_days=30,
    auto_hash=False,
)

try:
  login_result = authenticator.login(location="main")
except TypeError:
  login_result = authenticator.login("Login", "main")

if isinstance(login_result, tuple):
  nombre_autenticado, estado_autenticacion, username = login_result
else:
  nombre_autenticado = st.session_state.get("name")
  estado_autenticacion = st.session_state.get("authentication_status")
  username = st.session_state.get("username")

if estado_autenticacion is False:
  logger.warning("Intento de inicio de sesión fallido: usuario o contraseña incorrectos.")
  st.error("Usuario o contraseña incorrectos.")
  st.stop()
if estado_autenticacion is not True:
  logger.info("Esperando credenciales de usuario...")
  st.info("Introduce tus credenciales para continuar.")
  st.stop()

cuenta_actual = datos["cuentas"][username]
usuario_actual = cuenta_actual["name"]
logger.info(f"Usuario autenticado exitosamente: {username} ({usuario_actual}), rol: {cuenta_actual.get('role')}")

# Renderizar sidebar
render_sidebar(datos, username, authenticator)

# Contenido principal
st.title("🏡 Home Quest: Gamificación del Hogar")
st.caption(
    "¡Transforma las tareas domésticas en experiencia, niveles y recompensas!"
)

# Configurar pestañas
etiquetas_tabs = [
    "📋 Lista de Misiones",
    "🛍️ Tienda de Recompensas",
    "📜 Historial",
    "📊 Ranking",
]

if cuenta_actual.get("role") == "admin":
  etiquetas_tabs.append("⚙️ Administración")

logger.info(f"Renderizando pestañas principales para {usuario_actual}...")

tabs = st.tabs(etiquetas_tabs)
tab1, tab2, tab3, tab4 = tabs[:4]
tab_admin = tabs[4] if cuenta_actual.get("role") == "admin" else None

with tab1:
  render_quests_tab(datos, usuario_actual)

with tab2:
  render_rewards_tab(datos, usuario_actual)

with tab3:
  render_history_tab(datos)

with tab4:
  render_ranking_tab(datos)

if tab_admin is not None:
  with tab_admin:
    render_admin_tab(datos)

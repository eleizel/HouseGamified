import os
import streamlit as st
from core.achievements_manager import get_video_path_for_logro

CATEGORY_BADGES = {
    "rutina": "🔄 Rutina",
    "habilidad": "⚡ Habilidad",
    "hitos": "🏆 Hitos",
    "cooperativo": "🤝 Cooperativo",
}


@st.dialog("🎉 ¡Nuevo Logro Desbloqueado!")
def show_achievement_unlock_dialog(logro: dict):
    categoria = logro.get("categoria", "")
    badge = CATEGORY_BADGES.get(categoria, categoria.capitalize() if categoria else "General")

    st.subheader(f"🏆 {logro.get('nombre', 'Logro')}")
    st.markdown(f"**Categoría:** `{badge}`")
    st.write(logro.get("descripcion", ""))

    video_path = get_video_path_for_logro(logro.get("id", ""))
    if video_path and os.path.exists(video_path):
        st.video(video_path)
    else:
        st.info("🎬 Video de recompensa no disponible localmente.")

    if st.button("¡Genial!", type="primary", use_container_width=True):
        if (
            "logros_pendientes_mostrar" in st.session_state
            and st.session_state["logros_pendientes_mostrar"]
        ):
            st.session_state["logros_pendientes_mostrar"].pop(0)
        st.rerun()


def check_and_render_achievement_dialog():
    """Checks if there are pending achievements to celebrate and renders the dialog."""
    pendientes = st.session_state.get("logros_pendientes_mostrar", [])
    if pendientes:
        logro = pendientes[0]
        st.balloons()
        show_achievement_unlock_dialog(logro)

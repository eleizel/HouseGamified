from datetime import datetime
import os
import streamlit as st
from core.achievements_manager import (
    get_all_logros,
    get_user_logros_unlocked,
    calcular_progreso_logro,
    get_video_path_for_logro,
    parse_fecha,
)
from core.logger_config import get_logger

logger = get_logger(__name__)

CATEGORY_MAP = {
    "todas": "Todas las Categorías",
    "rutina": "🔄 Rutina",
    "habilidad": "⚡ Habilidad",
    "hitos": "🏆 Hitos",
    "cooperativo": "🤝 Cooperativo",
}


def format_unlock_date(date_raw) -> str:
    """Formats unlock date for presentation."""
    if not date_raw:
        return "Fecha desconocida"
    dt = parse_fecha(str(date_raw))
    if dt:
        return dt.strftime("%d/%m/%Y %H:%M")
    return str(date_raw)[:16]


def render_achievements_tab(datos: dict, usuario_actual: str):
    st.header("🏆 Galería de Logros")
    st.caption("¡Supera desafíos, mantén tus rachas y desbloquea recompensas en video!")

    # Resolve username_db
    username_db = next(
        (u for u, c in datos.get("cuentas", {}).items() if c.get("name") == usuario_actual),
        usuario_actual.lower(),
    )

    all_logros = get_all_logros()
    if not all_logros:
        st.warning("No se pudo cargar el catálogo de logros.")
        return

    unlocked_records = get_user_logros_unlocked(username_db)
    unlocked_map = {r["logro_id"]: r for r in unlocked_records}

    total_logros = len(all_logros)
    total_desbloqueados = len(unlocked_map)
    porcentaje = int((total_desbloqueados / total_logros) * 100) if total_logros > 0 else 0

    # User stats and history for progress calculation
    user_info = datos.get("usuarios", {}).get(usuario_actual, {})
    user_stats = {
        "xp": user_info.get("xp", 0),
        "puntos": user_info.get("puntos", 0),
        "nivel": user_info.get("nivel", 1),
    }
    user_historial = user_info.get("historial", [])
    user_recompensas = user_info.get("recompensas", [])

    # Compile all history for coop criteria
    all_historial = []
    for u_name, u_data in datos.get("usuarios", {}).items():
        u_db = next(
            (u for u, c in datos.get("cuentas", {}).items() if c.get("name") == u_name),
            u_name.lower(),
        )
        for h in u_data.get("historial", []):
            entry = dict(h)
            entry["username"] = u_db
            all_historial.append(entry)

    # --- Header Progress and Filters ---
    st.markdown("### 📊 Progreso General")
    st.progress(min(1.0, total_desbloqueados / total_logros) if total_logros > 0 else 0.0)
    st.markdown(
        f"Has desbloqueado **{total_desbloqueados}** de **{total_logros}** logros "
        f"(`{porcentaje}%` completado)"
    )

    st.markdown("---")

    col_filter, col_search = st.columns([1, 2])
    with col_filter:
        cat_keys = ["todas", "rutina", "habilidad", "hitos", "cooperativo"]
        categoria_sel = st.selectbox(
            "Filtrar por categoría",
            cat_keys,
            format_func=lambda k: CATEGORY_MAP.get(k, k),
        )
    with col_search:
        search_query = st.text_input("🔍 Buscar logros", placeholder="Nombre o descripción...").strip().lower()

    # Filter items
    filtered_logros = []
    for l in all_logros:
        if categoria_sel != "todas" and l.get("categoria") != categoria_sel:
            continue
        if search_query:
            nombre = l.get("nombre", "").lower()
            desc = l.get("descripcion", "").lower()
            if search_query not in nombre and search_query not in desc:
                continue
        filtered_logros.append(l)

    # Partition into unlocked and locked
    desbloqueados = [l for l in filtered_logros if l["id"] in unlocked_map]
    bloqueados = [l for l in filtered_logros if l["id"] not in unlocked_map]

    # --- SECTION 1: Unlocked Achievements ---
    st.subheader(f"🏆 Logros Desbloqueados ({len(desbloqueados)})")
    if not desbloqueados:
        st.info("No hay logros desbloqueados en esta selección.")
    else:
        for logro in desbloqueados:
            record = unlocked_map[logro["id"]]
            fecha_str = format_unlock_date(record.get("fecha_desbloqueo"))
            cat_badge = CATEGORY_MAP.get(logro.get("categoria", ""), logro.get("categoria", "").capitalize())

            with st.container(border=True):
                col_left, col_right = st.columns([3, 2])
                with col_left:
                    st.markdown(f"#### 🏆 {logro.get('nombre')}")
                    st.caption(f"Categoría: **{cat_badge}** | 📅 Desbloqueado: `{fecha_str}`")
                    st.write(logro.get("descripcion", ""))

                with col_right:
                    video_path = get_video_path_for_logro(logro["id"])
                    if video_path and os.path.exists(video_path):
                        st.video(video_path)
                    else:
                        st.info("🎬 Video de recompensa no disponible localmente.")

    st.markdown("---")

    # --- SECTION 2: Locked Achievements ---
    st.subheader(f"🔒 Logros por Desbloquear ({len(bloqueados)})")
    if not bloqueados:
        st.success("¡Enhorabuena! Has desbloqueado todos los logros en esta selección.")
    else:
        for logro in bloqueados:
            cat_badge = CATEGORY_MAP.get(logro.get("categoria", ""), logro.get("categoria", "").capitalize())
            actual, target = calcular_progreso_logro(
                logro=logro,
                user_stats=user_stats,
                user_historial=user_historial,
                user_recompensas=user_recompensas,
                all_historial=all_historial,
                username_db=username_db,
            )
            prog_ratio = min(1.0, actual / target) if target > 0 else 0.0

            with st.container(border=True):
                col_info, col_prog = st.columns([3, 1.5])
                with col_info:
                    st.markdown(f"**🔒 {logro.get('nombre')}**")
                    st.caption(f"Categoría: **{cat_badge}**")
                    st.markdown(f"*{logro.get('descripcion', '')}*")

                with col_prog:
                    st.markdown(f"**Progreso:** `{actual} / {target}`")
                    st.progress(prog_ratio)

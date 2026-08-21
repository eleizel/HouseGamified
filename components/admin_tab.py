import streamlit as st
import uuid
from core.data_manager import get_supabase_client
from core.game_logic import PERIODOS, NOMBRES_PERIODOS, fetch_db_data
from core.logger_config import get_logger

logger = get_logger(__name__)

def render_admin_tab(datos):
    st.header("⚙️ Panel de Administración")
    st.caption("Gestiona las tareas y recompensas disponibles para todos los jugadores.")
    
    supabase = get_supabase_client()
    
    tab_tareas, tab_recompensas = st.tabs(["📋 Tareas", "🎁 Recompensas"])
    
    with tab_tareas:
        render_crud_tareas(supabase, datos)
        
    with tab_recompensas:
        render_crud_recompensas(supabase, datos)

def render_crud_tareas(supabase, datos):
    st.subheader("Gestión de Tareas")
    
    # --- CREAR TAREA ---
    with st.expander("➕ Crear nueva tarea"):
        with st.form("crear_tarea_admin"):
            nombre = st.text_input("Nombre de la tarea")
            xp = st.number_input("XP otorgada", min_value=1, value=10, step=1)
            periodo = st.selectbox(
                "Periodo", PERIODOS, format_func=lambda p: NOMBRES_PERIODOS[p]
            )
            repetible = st.checkbox("Tarea repetible", value=False)
            max_repeticiones = st.number_input(
                "Máximo de veces por periodo",
                min_value=1,
                value=1,
                step=1,
                disabled=not repetible,
            )
            
            if st.form_submit_button("Guardar nueva tarea"):
                if not nombre.strip():
                    st.error("El nombre no puede estar vacío.")
                else:
                    nueva_tarea = {
                        "id": uuid.uuid4().hex,
                        "nombre": nombre.strip(),
                        "xp": int(xp),
                        "periodo": periodo,
                        "repetible": repetible,
                        "max_repeticiones": int(max_repeticiones) if repetible else 1,
                        "personalizada": True
                    }
                    supabase.table("tareas").insert(nueva_tarea).execute()
                    fetch_db_data.clear()
                    st.success(f"Tarea '{nombre}' creada.")
                    st.rerun()

    # --- LISTA, BÚSQUEDA, FILTROS Y PAGINACIÓN ---
    st.subheader("Tareas Existentes")
    tareas = supabase.table("tareas").select("*").execute().data
    
    if not tareas:
        st.info("No hay tareas registradas.")
        return

    # Controles de Búsqueda y Filtros
    col_search, col_filter_period, col_filter_type = st.columns([2, 1.5, 1.5])
    search_query = col_search.text_input("🔍 Buscar tarea", placeholder="Nombre...", key="admin_search_tareas")
    
    periodo_options = ["Todos"] + PERIODOS
    selected_periodo = col_filter_period.selectbox(
        "Periodo", 
        periodo_options, 
        format_func=lambda p: "Todos los periodos" if p == "Todos" else NOMBRES_PERIODOS[p], 
        key="admin_filter_periodo_tareas"
    )
    
    tipo_options = ["Todas", "Repetibles", "Únicas", "Personalizadas"]
    selected_tipo = col_filter_type.selectbox("Tipo", tipo_options, key="admin_filter_tipo_tareas")
    
    # Filtrar tareas
    filtered_tareas = []
    for t in tareas:
        if search_query and search_query.lower() not in t["nombre"].lower():
            continue
        if selected_periodo != "Todos" and t["periodo"] != selected_periodo:
            continue
        if selected_tipo == "Repetibles" and not t.get("repetible", False):
            continue
        if selected_tipo == "Únicas" and t.get("repetible", False):
            continue
        if selected_tipo == "Personalizadas" and not t.get("personalizada", False):
            continue
        filtered_tareas.append(t)
        
    total_items = len(filtered_tareas)
    if total_items == 0:
        st.warning("No se encontraron tareas con los filtros seleccionados.")
        return
        
    # Controles de Paginación
    if "admin_page_num_tareas" not in st.session_state:
        st.session_state["admin_page_num_tareas"] = 1

    col_page_size, col_page_num = st.columns([1, 1])
    items_per_page = col_page_size.selectbox("Por página", [5, 10, 20, 50], index=1, key="admin_page_size_tareas")
    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
    
    if st.session_state["admin_page_num_tareas"] > total_pages:
        st.session_state["admin_page_num_tareas"] = total_pages
    if st.session_state["admin_page_num_tareas"] < 1:
        st.session_state["admin_page_num_tareas"] = 1
    
    def update_page_tareas():
        st.session_state["admin_page_num_tareas"] = st.session_state["admin_page_selectbox_tareas"]

    if total_pages > 1:
        col_page_num.selectbox(
            "Página", 
            range(1, total_pages + 1), 
            index=st.session_state["admin_page_num_tareas"] - 1, 
            key="admin_page_selectbox_tareas",
            on_change=update_page_tareas
        )
    
    page_num = st.session_state["admin_page_num_tareas"]
    
    st.caption(f"Mostrando {min(items_per_page, total_items - (page_num - 1) * items_per_page)} de {total_items} tareas (Página {page_num} de {total_pages})")
    
    start_idx = (page_num - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_tareas = filtered_tareas[start_idx:end_idx]
    
    for tarea in page_tareas:
        with st.expander(f"{tarea['nombre']} ({NOMBRES_PERIODOS.get(tarea['periodo'], tarea['periodo'])})"):
            with st.form(f"editar_tarea_{tarea['id']}"):
                col1, col2 = st.columns(2)
                nombre_edit = col1.text_input("Nombre", value=tarea["nombre"], key=f"n_{tarea['id']}")
                xp_edit = col2.number_input("XP", min_value=1, value=int(tarea["xp"]), step=1, key=f"x_{tarea['id']}")
                
                periodo_edit = st.selectbox(
                    "Periodo", PERIODOS, index=PERIODOS.index(tarea["periodo"]) if tarea["periodo"] in PERIODOS else 0, 
                    format_func=lambda p: NOMBRES_PERIODOS[p], key=f"p_{tarea['id']}"
                )
                
                repetible_edit = st.checkbox("Repetible", value=bool(tarea["repetible"]), key=f"r_{tarea['id']}")
                max_rep_edit = st.number_input(
                    "Máximo repeticiones", min_value=1, value=max(1, int(tarea["max_repeticiones"])), 
                    step=1, disabled=not repetible_edit, key=f"m_{tarea['id']}"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.form_submit_button("Guardar cambios"):
                    supabase.table("tareas").update({
                        "nombre": nombre_edit.strip(),
                        "xp": int(xp_edit),
                        "periodo": periodo_edit,
                        "repetible": repetible_edit,
                        "max_repeticiones": int(max_rep_edit) if repetible_edit else 1,
                    }).eq("id", tarea["id"]).execute()
                    fetch_db_data.clear()
                    st.success("Tarea actualizada.")
                    st.rerun()
                
                if col_btn2.form_submit_button("Eliminar", type="primary"):
                    supabase.table("tareas").delete().eq("id", tarea["id"]).execute()
                    fetch_db_data.clear()
                    st.success("Tarea eliminada.")
                    st.rerun()

    # Botones de navegación al pie de la sección de tareas
    if total_pages > 1:
        st.markdown("---")
        col_first, col_prev, col_next, col_last = st.columns(4)
        if col_first.button("⏮️ Primera", disabled=(page_num <= 1), key="btn_first_tareas", use_container_width=True):
            st.session_state["admin_page_num_tareas"] = 1
            st.rerun()
        if col_prev.button("◀️ Anterior", disabled=(page_num <= 1), key="btn_prev_tareas", use_container_width=True):
            st.session_state["admin_page_num_tareas"] = max(1, page_num - 1)
            st.rerun()
        if col_next.button("Siguiente ▶️", disabled=(page_num >= total_pages), key="btn_next_tareas", use_container_width=True):
            st.session_state["admin_page_num_tareas"] = min(total_pages, page_num + 1)
            st.rerun()
        if col_last.button("Última ⏭️", disabled=(page_num >= total_pages), key="btn_last_tareas", use_container_width=True):
            st.session_state["admin_page_num_tareas"] = total_pages
            st.rerun()

def render_crud_recompensas(supabase, datos):
    st.subheader("Gestión de Recompensas")
    
    # --- CREAR RECOMPENSA ---
    with st.expander("➕ Crear nueva recompensa"):
        with st.form("crear_recompensa_admin"):
            nombre = st.text_input("Nombre de la recompensa")
            coste = st.number_input("Coste en puntos", min_value=0, value=100, step=10)
            
            if st.form_submit_button("Guardar nueva recompensa"):
                if not nombre.strip():
                    st.error("El nombre no puede estar vacío.")
                else:
                    nueva_rec = {
                        "nombre": nombre.strip(),
                        "coste": int(coste),
                        "personalizada": True
                    }
                    supabase.table("recompensas").insert(nueva_rec).execute()
                    fetch_db_data.clear()
                    st.success(f"Recompensa '{nombre}' creada.")
                    st.rerun()
                    
    # --- LISTA, BÚSQUEDA, FILTROS Y PAGINACIÓN ---
    st.subheader("Recompensas Existentes")
    recompensas = supabase.table("recompensas").select("*").execute().data
    
    if not recompensas:
        st.info("No hay recompensas registradas.")
        return

    # Controles de Búsqueda y Filtros
    col_search_rec, col_filter_rec_type, col_filter_rec_cost = st.columns([2, 1.5, 1.5])
    search_query_rec = col_search_rec.text_input("🔍 Buscar recompensa", placeholder="Nombre...", key="admin_search_recs")
    
    tipo_rec_options = ["Todas", "Personalizadas", "Del Sistema"]
    selected_tipo_rec = col_filter_rec_type.selectbox("Origen", tipo_rec_options, key="admin_filter_tipo_recs")
    
    coste_max_filter = col_filter_rec_cost.number_input("Coste máximo (0 = sin límite)", min_value=0, value=0, step=50, key="admin_filter_coste_recs")
    
    # Filtrar recompensas
    filtered_recs = []
    for rec in recompensas:
        if search_query_rec and search_query_rec.lower() not in rec["nombre"].lower():
            continue
        if selected_tipo_rec == "Personalizadas" and not rec.get("personalizada", False):
            continue
        if selected_tipo_rec == "Del Sistema" and rec.get("personalizada", False):
            continue
        if coste_max_filter > 0 and rec.get("coste", 0) > coste_max_filter:
            continue
        filtered_recs.append(rec)
        
    total_items_rec = len(filtered_recs)
    if total_items_rec == 0:
        st.warning("No se encontraron recompensas con los filtros seleccionados.")
        return
        
    # Controles de Paginación
    if "admin_page_num_recs" not in st.session_state:
        st.session_state["admin_page_num_recs"] = 1

    col_page_size_rec, col_page_num_rec = st.columns([1, 1])
    items_per_page_rec = col_page_size_rec.selectbox("Por página", [5, 10, 20, 50], index=1, key="admin_page_size_recs")
    total_pages_rec = max(1, (total_items_rec + items_per_page_rec - 1) // items_per_page_rec)
    
    if st.session_state["admin_page_num_recs"] > total_pages_rec:
        st.session_state["admin_page_num_recs"] = total_pages_rec
    if st.session_state["admin_page_num_recs"] < 1:
        st.session_state["admin_page_num_recs"] = 1

    def update_page_recs():
        st.session_state["admin_page_num_recs"] = st.session_state["admin_page_selectbox_recs"]

    if total_pages_rec > 1:
        col_page_num_rec.selectbox(
            "Página", 
            range(1, total_pages_rec + 1), 
            index=st.session_state["admin_page_num_recs"] - 1, 
            key="admin_page_selectbox_recs",
            on_change=update_page_recs
        )

    page_num_rec = st.session_state["admin_page_num_recs"]
    
    st.caption(f"Mostrando {min(items_per_page_rec, total_items_rec - (page_num_rec - 1) * items_per_page_rec)} de {total_items_rec} recompensas (Página {page_num_rec} de {total_pages_rec})")
    
    start_idx_rec = (page_num_rec - 1) * items_per_page_rec
    end_idx_rec = start_idx_rec + items_per_page_rec
    page_recs = filtered_recs[start_idx_rec:end_idx_rec]
    
    for rec in page_recs:
        with st.expander(f"{rec['nombre']} ({rec['coste']} puntos)"):
            with st.form(f"editar_rec_{rec['id']}"):
                nombre_edit = st.text_input("Nombre", value=rec["nombre"], key=f"rn_{rec['id']}")
                coste_edit = st.number_input("Coste", min_value=0, value=int(rec["coste"]), step=10, key=f"rc_{rec['id']}")
                
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.form_submit_button("Guardar cambios"):
                    supabase.table("recompensas").update({
                        "nombre": nombre_edit.strip(),
                        "coste": int(coste_edit)
                    }).eq("id", rec["id"]).execute()
                    fetch_db_data.clear()
                    st.success("Recompensa actualizada.")
                    st.rerun()
                    
                if col_btn2.form_submit_button("Eliminar", type="primary"):
                    supabase.table("recompensas").delete().eq("id", rec["id"]).execute()
                    fetch_db_data.clear()
                    st.success("Recompensa eliminada.")
                    st.rerun()

    # Botones de navegación al pie de la sección de recompensas
    if total_pages_rec > 1:
        st.markdown("---")
        col_first_rec, col_prev_rec, col_next_rec, col_last_rec = st.columns(4)
        if col_first_rec.button("⏮️ Primera", disabled=(page_num_rec <= 1), key="btn_first_recs", use_container_width=True):
            st.session_state["admin_page_num_recs"] = 1
            st.rerun()
        if col_prev_rec.button("◀️ Anterior", disabled=(page_num_rec <= 1), key="btn_prev_recs", use_container_width=True):
            st.session_state["admin_page_num_recs"] = max(1, page_num_rec - 1)
            st.rerun()
        if col_next_rec.button("Siguiente ▶️", disabled=(page_num_rec >= total_pages_rec), key="btn_next_recs", use_container_width=True):
            st.session_state["admin_page_num_recs"] = min(total_pages_rec, page_num_rec + 1)
            st.rerun()
        if col_last_rec.button("Última ⏭️", disabled=(page_num_rec >= total_pages_rec), key="btn_last_recs", use_container_width=True):
            st.session_state["admin_page_num_recs"] = total_pages_rec
            st.rerun()

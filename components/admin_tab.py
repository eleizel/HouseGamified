import streamlit as st
import uuid
from core.data_manager import get_supabase_client
from core.game_logic import PERIODOS, NOMBRES_PERIODOS
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
                    st.success(f"Tarea '{nombre}' creada.")
                    st.rerun()

    # --- LISTA Y EDITAR/ELIMINAR ---
    st.subheader("Tareas Existentes")
    tareas = supabase.table("tareas").select("*").execute().data
    
    for tarea in tareas:
        with st.expander(f"{tarea['nombre']} ({NOMBRES_PERIODOS.get(tarea['periodo'], tarea['periodo'])})"):
            with st.form(f"editar_tarea_{tarea['id']}"):
                col1, col2 = st.columns(2)
                nombre_edit = col1.text_input("Nombre", value=tarea["nombre"], key=f"n_{tarea['id']}")
                xp_edit = col2.number_input("XP", min_value=1, value=int(tarea["xp"]), step=1, key=f"x_{tarea['id']}")
                
                periodo_edit = st.selectbox(
                    "Periodo", PERIODOS, index=PERIODOS.index(tarea["periodo"]), 
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
                    st.success("Tarea actualizada.")
                    st.rerun()
                
                if col_btn2.form_submit_button("Eliminar", type="primary"):
                    supabase.table("tareas").delete().eq("id", tarea["id"]).execute()
                    st.success("Tarea eliminada.")
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
                    st.success(f"Recompensa '{nombre}' creada.")
                    st.rerun()
                    
    # --- LISTA Y EDITAR/ELIMINAR ---
    st.subheader("Recompensas Existentes")
    recompensas = supabase.table("recompensas").select("*").execute().data
    
    for rec in recompensas:
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
                    st.success("Recompensa actualizada.")
                    st.rerun()
                    
                if col_btn2.form_submit_button("Eliminar", type="primary"):
                    supabase.table("recompensas").delete().eq("id", rec["id"]).execute()
                    st.success("Recompensa eliminada.")
                    st.rerun()

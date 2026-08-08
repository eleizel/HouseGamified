import streamlit as st
import uuid
from core.data_manager import guardar_datos
from core.game_logic import PERIODOS, NOMBRES_PERIODOS


def render_admin_tab(datos):
  st.header("Administrar tareas")
  st.caption("Las tareas nuevas se aplican a todos los jugadores.")
  with st.form("crear_tarea"):
    st.subheader("Crear nueva tarea")
    nombre_nueva_tarea = st.text_input("Nombre de la tarea")
    xp_nueva_tarea = st.number_input("XP otorgada", min_value=1, value=10, step=1)
    periodo_nueva_tarea = st.selectbox(
        "Periodo", PERIODOS, format_func=lambda periodo: NOMBRES_PERIODOS[periodo]
    )
    repetible_nueva_tarea = st.checkbox("Tarea repetible", value=False)
    max_repeticiones_nueva = st.number_input(
        "Máximo de veces por periodo",
        min_value=1,
        value=1,
        step=1,
        key="crear_max_repeticiones",
        help="Se aplicará cuando Tarea repetible esté activada.",
    )
    crear_tarea = st.form_submit_button("Crear tarea")

  if crear_tarea:
    nombre_nueva_tarea = nombre_nueva_tarea.strip()
    nombres_existentes = {
        tarea["nombre"].casefold()
        for tarea in datos.get("tareas_personalizadas", [])
    }
    if not nombre_nueva_tarea:
      st.error("El nombre de la tarea no puede estar vacío.")
    elif nombre_nueva_tarea.casefold() in nombres_existentes:
      st.error("Ya existe una tarea personalizada con ese nombre.")
    else:
      datos["tareas_personalizadas"].append({
          "id": uuid.uuid4().hex,
          "nombre": nombre_nueva_tarea,
          "xp": int(xp_nueva_tarea),
          "periodo": periodo_nueva_tarea,
          "repetible": repetible_nueva_tarea,
          "max_repeticiones": (
              int(max_repeticiones_nueva) if repetible_nueva_tarea else 1
          ),
      })
      guardar_datos(datos)
      st.success("Tarea creada correctamente.")
      st.rerun()

  st.divider()
  st.subheader("Actualizar o eliminar tareas")
  tareas_personalizadas = datos.get("tareas_personalizadas", [])
  if not tareas_personalizadas:
    st.info("Todavía no hay tareas personalizadas.")
  else:
    tarea_seleccionada = st.selectbox(
        "Selecciona una tarea",
        tareas_personalizadas,
        format_func=lambda tarea: (
            f"{tarea['nombre']} ({NOMBRES_PERIODOS.get(tarea['periodo'], tarea['periodo'])})"
        ),
    )
    with st.form("editar_tarea"):
      nombre_editado = st.text_input("Nombre", value=tarea_seleccionada["nombre"])
      xp_editado = st.number_input(
          "XP otorgada", min_value=1, value=int(tarea_seleccionada["xp"]), step=1
      )
      periodo_editado = st.selectbox(
          "Periodo",
          PERIODOS,
          index=PERIODOS.index(tarea_seleccionada["periodo"]),
          format_func=lambda periodo: NOMBRES_PERIODOS[periodo],
      )
      repetible_editado = st.checkbox(
          "Tarea repetible",
          value=bool(tarea_seleccionada.get("repetible", False)),
      )
      max_repeticiones_editado = st.number_input(
          "Máximo de veces por periodo",
          min_value=1,
          value=max(1, int(tarea_seleccionada.get("max_repeticiones", 1))),
          step=1,
          key=f"editar_max_repeticiones_{tarea_seleccionada['id']}",
          help="Se aplicará cuando Tarea repetible esté activada.",
      )
      guardar_cambios = st.form_submit_button("Guardar cambios")

    if guardar_cambios:
      nombre_editado = nombre_editado.strip()
      if not nombre_editado:
        st.error("El nombre de la tarea no puede estar vacío.")
      else:
        tarea_seleccionada.update({
            "nombre": nombre_editado,
            "xp": int(xp_editado),
            "periodo": periodo_editado,
            "repetible": repetible_editado,
            "max_repeticiones": (
                int(max_repeticiones_editado) if repetible_editado else 1
            ),
        })
        guardar_datos(datos)
        st.success("Tarea actualizada correctamente.")
        st.rerun()

    confirmar_eliminacion = st.checkbox("Confirmo que quiero eliminar esta tarea")
    if st.button("Eliminar tarea", disabled=not confirmar_eliminacion):
      datos["tareas_personalizadas"] = [
          tarea for tarea in tareas_personalizadas
          if tarea["id"] != tarea_seleccionada["id"]
      ]
      guardar_datos(datos)
      st.success("Tarea eliminada correctamente.")
      st.rerun()

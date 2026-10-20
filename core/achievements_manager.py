from datetime import datetime, timedelta
import os
from core.data_manager import get_supabase_client
from core.logger_config import get_logger

logger = get_logger(__name__)

VIDEO_BASE_PATH = os.path.join("resources", "achievements", "video")


def parse_fecha(fecha_str: str) -> datetime | None:
    """Safely parse a date string from history or timestamps."""
    if not fecha_str or not isinstance(fecha_str, str):
        return None
    try:
        # Standard format: 'YYYY-MM-DD HH:MM'
        return datetime.strptime(fecha_str[:16], "%Y-%m-%d %H:%M")
    except Exception:
        try:
            # ISO format: 'YYYY-MM-DDTHH:MM:SS...'
            return datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
        except Exception:
            try:
                # Date only: 'YYYY-MM-DD'
                return datetime.strptime(fecha_str[:10], "%Y-%m-%d")
            except Exception:
                return None


def get_all_logros() -> list[dict]:
    """Fetches all achievement catalog definitions from public.logros."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("logros").select("*").execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error al obtener el catálogo de logros: {e}")
        return []


def get_user_logros_unlocked(username_db: str) -> list[dict]:
    """Fetches unlocked achievements for a specific user from public.logros_usuario."""
    try:
        supabase = get_supabase_client()
        response = (
            supabase.table("logros_usuario")
            .select("*")
            .eq("username", username_db)
            .execute()
        )
        return response.data or []
    except Exception as e:
        logger.error(f"Error al obtener logros desbloqueados de {username_db}: {e}")
        return []


def calcular_progreso_logro(
    logro: dict,
    user_stats: dict,
    user_historial: list[dict],
    user_recompensas: list[dict],
    all_historial: list[dict] | None = None,
    username_db: str = "",
) -> tuple[int, int]:
    """
    Calculates (current_progress, target_value) for a given achievement.
    """
    criterio_tipo = logro.get("criterio_tipo")
    criterio_target = logro.get("criterio_target")
    target_valor = int(logro.get("criterio_valor") or 1)

    completed_tasks = [
        h for h in user_historial if h.get("tipo") == "tarea_completada"
    ]

    actual = 0

    if criterio_tipo == "tarea_especifica":
        actual = sum(
            1 for h in completed_tasks if h.get("tarea") == criterio_target
        )

    elif criterio_tipo == "total_tareas":
        actual = len(completed_tasks)

    elif criterio_tipo == "total_xp":
        actual = int(user_stats.get("xp") or 0)

    elif criterio_tipo == "nivel_alcanzado":
        actual = int(user_stats.get("nivel") or 1)

    elif criterio_tipo == "puntos_disponibles":
        actual = int(user_stats.get("puntos") or 0)

    elif criterio_tipo == "total_recompensas_canjeadas":
        hist_count = sum(
            1 for h in user_historial if h.get("tipo") == "recompensa_canjeada"
        )
        rec_count = len(user_recompensas)
        actual = max(hist_count, rec_count)

    elif criterio_tipo == "total_recompensas_disfrutadas":
        hist_count = sum(
            1 for h in user_historial if h.get("tipo") == "recompensa_disfrutada"
        )
        rec_count = sum(
            1 for r in user_recompensas if r.get("estado") == "completed"
        )
        actual = max(hist_count, rec_count)

    elif criterio_tipo == "racha_dias":
        dates = set()
        for t in completed_tasks:
            dt = parse_fecha(t.get("fecha"))
            if dt:
                dates.add(dt.date())
        sorted_dates = sorted(dates)
        if not sorted_dates:
            actual = 0
        else:
            max_streak = 1
            curr_streak = 1
            for i in range(len(sorted_dates) - 1):
                if sorted_dates[i + 1] - sorted_dates[i] == timedelta(days=1):
                    curr_streak += 1
                    if curr_streak > max_streak:
                        max_streak = curr_streak
                elif sorted_dates[i + 1] == sorted_dates[i]:
                    continue
                else:
                    curr_streak = 1
            actual = max_streak

    elif criterio_tipo == "tareas_mismo_dia":
        tasks_by_day = {}
        for t in completed_tasks:
            dt = parse_fecha(t.get("fecha"))
            if dt:
                day_key = dt.strftime("%Y-%m-%d")
                tasks_by_day[day_key] = tasks_by_day.get(day_key, 0) + 1
        actual = max(tasks_by_day.values()) if tasks_by_day else 0

    elif criterio_tipo == "tareas_fin_de_semana":
        weekend_tasks = {}
        for t in completed_tasks:
            dt = parse_fecha(t.get("fecha"))
            if dt and dt.weekday() in (5, 6):  # Saturday=5, Sunday=6
                day_key = dt.strftime("%Y-%m-%d")
                weekend_tasks[day_key] = weekend_tasks.get(day_key, 0) + 1
        actual = max(weekend_tasks.values()) if weekend_tasks else 0

    elif criterio_tipo == "hora_especial_noche":
        count = 0
        for t in completed_tasks:
            dt = parse_fecha(t.get("fecha"))
            if dt and (dt.hour >= 23 or dt.hour < 5):
                count += 1
        actual = count

    elif criterio_tipo == "hora_especial_manana":
        count = 0
        for t in completed_tasks:
            dt = parse_fecha(t.get("fecha"))
            if dt and (dt.hour < 7 or (dt.hour == 7 and dt.minute < 30)):
                count += 1
        actual = count

    elif criterio_tipo == "coop_mismo_dia":
        if all_historial:
            all_completed = [
                h for h in all_historial if h.get("tipo") == "tarea_completada"
            ]
            coop_by_day = {}
            for t in all_completed:
                dt = parse_fecha(t.get("fecha"))
                u = t.get("username")
                if dt and u:
                    day_key = dt.strftime("%Y-%m-%d")
                    if day_key not in coop_by_day:
                        coop_by_day[day_key] = {}
                    coop_by_day[day_key][u] = coop_by_day[day_key].get(u, 0) + 1

            max_coop = 0
            for day, users_counts in coop_by_day.items():
                user_count = users_counts.get(username_db, 0)
                other_counts = [c for u, c in users_counts.items() if u != username_db]
                max_other = max(other_counts) if other_counts else 0
                coop_score = min(user_count, max_other)
                if coop_score > max_coop:
                    max_coop = coop_score
            actual = max_coop
        else:
            actual = 0

    elif criterio_tipo == "variedad_periodos":
        # Check if in any calendar month (YYYY-MM), all 4 periods were completed
        month_categories = {}
        for t in completed_tasks:
            dt = parse_fecha(t.get("fecha"))
            cat = t.get("categoria")
            if dt and cat:
                m_key = dt.strftime("%Y-%m")
                month_categories.setdefault(m_key, set()).add(cat)
        actual = (
            max(len(cats) for cats in month_categories.values())
            if month_categories
            else 0
        )

    return (actual, target_valor)


def verificar_y_otorgar_logros(username_db: str) -> list[dict]:
    """
    Evaluates criterion conditions for locked achievements and unlocks newly earned ones.
    Returns list of newly unlocked achievement dicts.
    """
    if not username_db:
        return []

    try:
        supabase = get_supabase_client()

        # 1. Fetch user's current unlocked achievements
        unlocked_records = get_user_logros_unlocked(username_db)
        unlocked_logro_ids = {r["logro_id"] for r in unlocked_records}

        # 2. Fetch all available achievements
        all_logros = get_all_logros()
        if not all_logros:
            return []

        # 3. Fetch user's stats
        user_res = (
            supabase.table("usuarios")
            .select("username, xp, puntos, nivel")
            .eq("username", username_db)
            .execute()
        )
        if not user_res.data:
            logger.warning(f"Usuario {username_db} no encontrado para verificación de logros.")
            return []
        user_stats = user_res.data[0]

        # 4. Fetch full activity logs
        user_hist_res = (
            supabase.table("historial")
            .select("*")
            .eq("username", username_db)
            .execute()
        )
        user_historial = user_hist_res.data or []

        user_rec_res = (
            supabase.table("recompensas_usuario")
            .select("*")
            .eq("username", username_db)
            .execute()
        )
        user_recompensas = user_rec_res.data or []

        # Fetch all historial if coop achievements exist and are locked
        all_historial = None
        has_locked_coop = any(
            l["criterio_tipo"] == "coop_mismo_dia" and l["id"] not in unlocked_logro_ids
            for l in all_logros
        )
        if has_locked_coop:
            all_hist_res = supabase.table("historial").select("*").execute()
            all_historial = all_hist_res.data or []

        # 5. Evaluate criteria for locked achievements
        nuevos_logros = []
        for logro in all_logros:
            logro_id = logro["id"]
            if logro_id in unlocked_logro_ids:
                continue

            actual, target = calcular_progreso_logro(
                logro=logro,
                user_stats=user_stats,
                user_historial=user_historial,
                user_recompensas=user_recompensas,
                all_historial=all_historial,
                username_db=username_db,
            )

            if actual >= target:
                # Grant achievement
                try:
                    insert_res = (
                        supabase.table("logros_usuario")
                        .insert(
                            {
                                "username": username_db,
                                "logro_id": logro_id,
                                "visto": False,
                            }
                        )
                        .execute()
                    )
                    logger.info(
                        f"🎉 ¡LOGRO DESBLOQUEADO! Usuario: {username_db}, Logro: '{logro.get('nombre')}' ({logro_id})"
                    )
                    nuevos_logros.append(logro)
                    unlocked_logro_ids.add(logro_id)
                except Exception as insert_err:
                    logger.error(
                        f"Error al insertar logro_usuario ({username_db}, {logro_id}): {insert_err}"
                    )

        return nuevos_logros

    except Exception as e:
        logger.error(f"Error durante verificar_y_otorgar_logros para {username_db}: {e}")
        return []


def get_video_path_for_logro(logro_id: str) -> str | None:
    """
    Returns the path to the local video file if it exists, otherwise None.
    """
    video_path = os.path.join(VIDEO_BASE_PATH, f"{logro_id}.mp4")
    if os.path.exists(video_path):
        return video_path
    return None

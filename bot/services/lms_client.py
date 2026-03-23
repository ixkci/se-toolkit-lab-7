import httpx
from config import LMS_API_BASE_URL, LMS_API_KEY


def get_headers() -> dict:
    return {"Authorization": f"Bearer {LMS_API_KEY}"}


def format_error(e: Exception) -> str:
    """Форматирует ошибку в человекочитаемый вид без сырого Traceback"""
    if isinstance(e, httpx.ConnectError):
        return f"Backend error: connection refused ({LMS_API_BASE_URL}). Check that the services are running."
    if isinstance(e, httpx.HTTPStatusError):
        return f"Backend error: HTTP {e.response.status_code}. The backend service may be down or rejected the request."
    return f"Backend error: {str(e)}"


def get_health() -> str:
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{LMS_API_BASE_URL}/items/", headers=get_headers(), timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            return f"Backend is healthy. {len(data)} items available."
    except Exception as e:
        return format_error(e)


def get_labs() -> str:
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{LMS_API_BASE_URL}/items/", headers=get_headers(), timeout=5.0
            )
            response.raise_for_status()
            data = response.json()

            # Фильтруем только лабораторные работы
            labs = [item for item in data if item.get("type") == "lab"]

            if not labs:
                return "No labs available."

            result = ["Available labs:"]
            for lab in labs:
                lab_id = lab.get("id", "Unknown")
                lab_name = lab.get("title", "Unknown")
                result.append(f"- Lab 0{lab_id} — {lab_name}")
            return "\n".join(result)
    except Exception as e:
        return format_error(e)


def get_scores(lab_id: str) -> str:
    if not lab_id:
        return "Please provide a lab ID. Example: /scores lab-04"

    try:
        with httpx.Client() as client:
            response = client.get(
                f"{LMS_API_BASE_URL}/analytics/pass-rates?lab={lab_id}",
                headers=get_headers(),
                timeout=5.0,
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                return f"No score data found for {lab_id}."

            result = [f"Pass rates for {lab_id}:"]
            for item in data:
                task_name = item.get("task", "Unknown Task")
                pass_rate = item.get("avg_score", 0)
                attempts = item.get("attempts", 0)
                result.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
            return "\n".join(result)
    except Exception as e:
        return format_error(e)

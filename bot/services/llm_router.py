import sys
import httpx
import json
from config import (
    LLM_API_BASE_URL,
    LLM_API_KEY,
    LLM_API_MODEL,
    LMS_API_BASE_URL,
    LMS_API_KEY,
)

# P1.2: Определяем 9 инструментов для LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "Get a list of all labs and tasks",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get enrolled students and groups",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets) for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group scores and student counts for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by score for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"},
                    "limit": {
                        "type": "integer",
                        "description": "Number of students, e.g. 5",
                    },
                },
                "required": ["lab", "limit"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Refresh data from autochecker",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def execute_tool(name: str, args: dict) -> dict:
    """Выполняет реальный запрос к LMS API на основе выбора LLM"""
    headers = {"Authorization": f"Bearer {LMS_API_KEY}"}
    try:
        if name == "get_items":
            res = httpx.get(f"{LMS_API_BASE_URL}/items/", headers=headers, timeout=10.0)
        elif name == "get_learners":
            res = httpx.get(
                f"{LMS_API_BASE_URL}/learners/", headers=headers, timeout=10.0
            )
        elif name == "get_scores":
            res = httpx.get(
                f"{LMS_API_BASE_URL}/analytics/scores",
                params=args,
                headers=headers,
                timeout=10.0,
            )
        elif name == "get_pass_rates":
            res = httpx.get(
                f"{LMS_API_BASE_URL}/analytics/pass-rates",
                params=args,
                headers=headers,
                timeout=10.0,
            )
        elif name == "get_timeline":
            res = httpx.get(
                f"{LMS_API_BASE_URL}/analytics/timeline",
                params=args,
                headers=headers,
                timeout=10.0,
            )
        elif name == "get_groups":
            res = httpx.get(
                f"{LMS_API_BASE_URL}/analytics/groups",
                params=args,
                headers=headers,
                timeout=10.0,
            )
        elif name == "get_top_learners":
            res = httpx.get(
                f"{LMS_API_BASE_URL}/analytics/top-learners",
                params=args,
                headers=headers,
                timeout=10.0,
            )
        elif name == "get_completion_rate":
            res = httpx.get(
                f"{LMS_API_BASE_URL}/analytics/completion-rate",
                params=args,
                headers=headers,
                timeout=10.0,
            )
        elif name == "trigger_sync":
            res = httpx.post(
                f"{LMS_API_BASE_URL}/pipeline/sync",
                headers=headers,
                json={},
                timeout=10.0,
            )
        else:
            return {"error": "Unknown tool"}

        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}


def route_intent(user_text: str) -> str:
    """P1.4: Главный цикл работы с LLM (Multi-step reasoning)"""
    messages = [
        {
            "role": "system",
            "content": "You are a helpful LMS data assistant. Use the provided tools to fetch real data to answer the user's question. If you don't know the answer, call a tool to find out. Format your final answer nicely.",
        },
        {"role": "user", "content": user_text},
    ]

    # Максимум 5 шагов, чтобы избежать бесконечного цикла
    for _ in range(5):
        payload = {
            "model": LLM_API_MODEL,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
        }
        headers = {"Authorization": f"Bearer {LLM_API_KEY}"}

        try:
            # Стучимся к Qwen
            response = httpx.post(
                f"{LLM_API_BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
        except Exception as e:
            return f"LLM Connection error: {str(e)}"

        data = response.json()
        message = data["choices"][0]["message"]

        # Если LLM решила вызвать инструмент(ы)
        if message.get("tool_calls"):
            messages.append(message)  # Обязательно сохраняем контекст
            for tool_call in message["tool_calls"]:
                name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])

                # Печатаем дебаг в stderr (как требует задание)
                print(f"[tool] LLM called: {name}({args})", file=sys.stderr)

                result = execute_tool(name, args)
                print(f"[tool] Result: {len(str(result))} bytes", file=sys.stderr)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(result),
                    }
                )

            print(
                f"[summary] Feeding {len(message['tool_calls'])} tool results back to LLM",
                file=sys.stderr,
            )
            # Цикл продолжается, отправляем результаты обратно в LLM
        else:
            # Инструменты не нужны, возвращаем текстовый ответ пользователю
            return message.get("content", "I couldn't generate an answer.")

    return "Error: Reached maximum reasoning steps."

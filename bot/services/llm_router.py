import sys
import httpx
import json
from config import LLM_API_BASE_URL, LLM_API_KEY, LLM_API_MODEL, LMS_API_BASE_URL, LMS_API_KEY

TOOLS = [
    {"type": "function", "function": {"name": "get_items", "description": "Get a list of all labs and tasks", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_learners", "description": "Get enrolled students and groups", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_scores", "description": "Get score distribution (4 buckets) for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_pass_rates", "description": "Get per-task average scores and attempt counts for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_timeline", "description": "Get submissions per day for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_groups", "description": "Get per-group scores and student counts for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "get_top_learners", "description": "Get top N learners by score for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}, "limit": {"type": "integer", "description": "Number of students, e.g. 5"}}, "required": ["lab", "limit"]}}},
    {"type": "function", "function": {"name": "get_completion_rate", "description": "Get completion rate percentage for a lab", "parameters": {"type": "object", "properties": {"lab": {"type": "string", "description": "Lab ID, e.g. 'lab-04'"}}, "required": ["lab"]}}},
    {"type": "function", "function": {"name": "trigger_sync", "description": "Refresh data from autochecker", "parameters": {"type": "object", "properties": {}}}}
]

def execute_tool(name: str, args: dict) -> dict:
    headers = {"Authorization": f"Bearer {LMS_API_KEY}"}
    try:
        if name == "get_items":
            res = httpx.get(f"{LMS_API_BASE_URL}/items/", headers=headers, timeout=10.0)
        elif name == "get_learners":
            res = httpx.get(f"{LMS_API_BASE_URL}/learners/", headers=headers, timeout=10.0)
        elif name == "get_scores":
            res = httpx.get(f"{LMS_API_BASE_URL}/analytics/scores", params=args, headers=headers, timeout=10.0)
        elif name == "get_pass_rates":
            res = httpx.get(f"{LMS_API_BASE_URL}/analytics/pass-rates", params=args, headers=headers, timeout=10.0)
        elif name == "get_timeline":
            res = httpx.get(f"{LMS_API_BASE_URL}/analytics/timeline", params=args, headers=headers, timeout=10.0)
        elif name == "get_groups":
            res = httpx.get(f"{LMS_API_BASE_URL}/analytics/groups", params=args, headers=headers, timeout=10.0)
        elif name == "get_top_learners":
            res = httpx.get(f"{LMS_API_BASE_URL}/analytics/top-learners", params=args, headers=headers, timeout=10.0)
        elif name == "get_completion_rate":
            res = httpx.get(f"{LMS_API_BASE_URL}/analytics/completion-rate", params=args, headers=headers, timeout=10.0)
        elif name == "trigger_sync":
            res = httpx.post(f"{LMS_API_BASE_URL}/pipeline/sync", headers=headers, json={}, timeout=10.0)
        else:
            return {"error": "Unknown tool"}

        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def route_intent(user_text: str) -> str:
    print(f"[debug] Routing intent for: {user_text}", file=sys.stderr)
    messages = [
        {"role": "system", "content": "You are a helpful LMS data assistant. Use tools to fetch real data to answer the user's question."},
        {"role": "user", "content": user_text}
    ]

    for _ in range(5):
        payload = {
            "model": LLM_API_MODEL,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto"
        }
        headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
        
        try:
            response = httpx.post(f"{LLM_API_BASE_URL}/chat/completions", json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
        except Exception as e:
            err_msg = f"LLM Connection error: {str(e)}"
            print(f"[debug] {err_msg}", file=sys.stderr)
            return err_msg

        data = response.json()
        message = data["choices"][0]["message"]

        if message.get("tool_calls"):
            messages.append(message)
            for tool_call in message["tool_calls"]:
                name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                
                print(f"[tool] LLM called: {name}({args})", file=sys.stderr)

                result = execute_tool(name, args)
                print(f"[tool] Result length: {len(str(result))} chars", file=sys.stderr)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result)
                })
            
            print(f"[summary] Feeding {len(message['tool_calls'])} tool results back to LLM", file=sys.stderr)
        else:
            return message.get("content", "I couldn't generate an answer.")
            
    return "Error: Reached maximum reasoning steps."

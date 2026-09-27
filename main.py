import os
from google import genai
from dotenv import load_dotenv
import json
from Tools import get_load, get_substations

load_dotenv() 

get_substations_function = {
    "type": "function",
    "name": "get_substations",
    "description": "Get the list of substations for a given name.",
    "parameters": {
        "type": "object",
        "properties": {
            "name":{"type": "string", "enum": ["Neuenhagen", "Wolmirstedt"]}
        },
        "required": ["name"],
    }
}
get_load_function = {
    "type": "function",
    "name": "get_load",
    "description": "Get load of an inidividual substation based on substation id",
    "parameters": {
        "type": "object",
        "properties": {
            "substation_id":{"type": "string", "description": "the substaion id, e.g :'SS-001'. To get valid ID get_substations needs to be queried"}
        },
        "required": ["substation_id"],
    }
}

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
)

TOOLS = [get_substations_function, get_load_function]
FUNCTIONS = {"get_substations": get_substations, "get_load": get_load}
MAX_ITERS = 10

def show(label, data):
    print(f"\n===== {label} =====")
    print(json.dumps(data, indent=2, default=str))


print("enter prompt:")
user_input: str = input()

history = [
    {"type": "user_input", "content": [{"type": "text", "text": user_input}]},
]

turn = 0
while True:
    turn += 1
    if turn > MAX_ITERS:
        raise RuntimeError(f"exceeded {MAX_ITERS} tool-calling rounds")
    show(f"TURN {turn}: REQUEST HISTORY ({len(history)} steps)", history)

    interaction = client.interactions.create(
        store=False,
        model="gemini-3.8-flash",
        input=history,  # type: ignore
        tools=TOOLS,
    )

    steps = interaction.steps or []  # type: ignore
    show(f"TURN {turn}: RESPONSE STEPS", [s.model_dump(mode="json", exclude_none=True) for s in steps])

    history.extend(s.model_dump(mode="json", exclude_none=True) for s in steps)

    function_calls = [s for s in steps if s.type == "function_call"]
    if not function_calls:
        break

    for call in function_calls:
        func = FUNCTIONS.get(call.name)
        is_error = True
        if func is None:
            result = f"unknown tool: {call.name}"
        else:
            try:
                result = json.dumps(func(**call.arguments))
                is_error = False
            except Exception as e:
                result = f"{call.name} failed: {type(e).__name__}: {e}"
        function_result = {
            "type": "function_result",
            "name": call.name,
            "call_id": call.id,
            "result": result,
            "is_error": is_error,
        }
        show(f"TURN {turn}: RAN {call.name}", function_result)
        history.append(function_result)

show("FINAL ANSWER", interaction.output_text)  # type: ignore

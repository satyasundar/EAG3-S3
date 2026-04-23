"""
Smart Shopping Assistant Agent — Python prototype
Uses the NEW google-genai SDK with manual function calling loop.

Install: pip install google-genai requests beautifulsoup4
Run:     python agent.py
"""

import os
import json
import time
import requests
from google import genai
from google.genai import types

# ============================================================
# CONFIG
# ============================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # from Google AI Studio
SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # from serper.dev

MODEL_NAME = "gemini-3.1-flash-lite-preview"
# MODEL_NAME = "gemini-3-flash-preview"
# MODEL_NAME = "gemini-2.5-flash-lite"
# MODEL_NAME = "gemini-2.5-flash"
#MODEL_NAME = "gemma-4-31b-it"
# MODEL_NAME = "gemma-4-26b-a4b-it"

MAX_ITERATIONS = 5
THROTTLE_SECONDS = 6


# ============================================================
# TOOLS — actual Python implementations
# ============================================================

def get_current_product():
    """In the Chrome extension, this reads the DOM. Here we hardcode."""
    return {
        "name": "Sony WH-1000XM5 Wireless Headphones",
        "price_inr": 29990,
        "site": "amazon.in",
        "url": "https://www.amazon.in/dp/B09XS7JWHH"
    }


def search_web(query: str):
    """Search the web using Serper.dev (Google results as JSON)."""
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "gl": "in", "num": 8}

    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    data = resp.json()

    results = []
    for item in data.get("organic", [])[:8]:
        results.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "link": item.get("link"),
        })
    return {"query": query, "results": results}


def fetch_page_text(url: str):
    """Fetch a URL and return the first chunk of its visible text."""
    try:
        from bs4 import BeautifulSoup
        headers = {"User-Agent": "Mozilla/5.0 (shopping-agent)"}
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return {"url": url, "text": text[:3000]}
    except Exception as e:
        return {"url": url, "error": str(e)}


TOOL_REGISTRY = {
    "get_current_product": get_current_product,
    "search_web": search_web,
    "fetch_page_text": fetch_page_text,
}


# ============================================================
# TOOL SCHEMAS — what the LLM sees
# ============================================================

get_current_product_decl = types.FunctionDeclaration(
    name="get_current_product",
    description="Get the product the user is currently viewing (name, price, site, url). Call this FIRST.",
    parameters_json_schema={"type": "object", "properties": {}},
)

search_web_decl = types.FunctionDeclaration(
    name="search_web",
    description=(
        "Search the web. Use for finding prices on other sites "
        "(e.g. 'Sony WH-1000XM5 price India') or for finding reviews "
        "(e.g. 'Sony WH-1000XM5 reddit review problems')."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"],
    },
)

fetch_page_text_decl = types.FunctionDeclaration(
    name="fetch_page_text",
    description="Fetch the text content of a specific URL. Use when a search snippet isn't enough.",
    parameters_json_schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Full URL to fetch"}
        },
        "required": ["url"],
    },
)

tools = [types.Tool(function_declarations=[
    get_current_product_decl,
    search_web_decl,
    fetch_page_text_decl,
])]


# ============================================================
# SYSTEM PROMPT
# ============================================================
SYSTEM_PROMPT = """You are a smart shopping assistant.

Your job: given a product the user is viewing, decide if they should BUY IT HERE, BUY IT ELSEWHERE, or SKIP.

Process:
1. Call get_current_product() to see what they're looking at.
2. Call search_web() to compare prices on other Indian sites (Flipkart, Croma, Reliance Digital).
3. Call search_web() again to check reviews — look for Reddit threads or mentions of problems.
4. Optionally call fetch_page_text() on one important result if a snippet isn't enough.
5. Give a clear verdict: recommendation, best price & where, key pros, key cons.

Rules:
- Prefer Indian sources (prices in ₹).
- Use at most 5 tool calls total.
- When you have enough info, stop calling tools and give the final verdict.
- Be concise — the user wants a decision, not an essay.
"""


# ============================================================
# AGENT LOOP
# ============================================================

def run_agent():
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Disable automatic function calling — WE control the loop,
    # which is the whole point of the assignment.
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=tools,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    # The growing conversation history. Every turn we append to this.
    history = [
        types.Content(role="user", parts=[types.Part(text="Should I buy this product?")])
    ]

    print("=" * 60)
    print("🛒 SMART SHOPPING AGENT")
    print("=" * 60)

    print(f"\n MODEL NAME : ")

    for iteration in range(MAX_ITERATIONS):
        print(f"\n───── Iteration {iteration + 1} ─────")
        print(f"\n [waiting {THROTTLE_SECONDS} to respect the rate limit ...")
        time.sleep(THROTTLE_SECONDS)
        # --- Call the LLM with the FULL history ---
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=history,
            config=config,
        )

        # Extract parts from the response
        candidate = response.candidates[0]
        parts = candidate.content.parts or []

        tool_calls = []
        text_output = ""
        for part in parts:
            if getattr(part, "function_call", None) and part.function_call.name:
                tool_calls.append(part.function_call)
            elif getattr(part, "text", None):
                text_output += part.text

        if text_output.strip():
            print(f"\n💭 LLM reasoning:\n{text_output.strip()}")

        # --- If no tool calls, we're done ---
        if not tool_calls:
            print("\n" + "=" * 60)
            print("✅ FINAL VERDICT")
            print("=" * 60)
            print(text_output.strip())
            return text_output

        # --- Append the model's response to history ---
        history.append(types.Content(role="model", parts=parts))

        # --- Execute each tool call and collect results ---
        tool_response_parts = []
        for call in tool_calls:
            tool_name = call.name
            tool_args = dict(call.args) if call.args else {}

            print(f"\n🔧 Tool call: {tool_name}({tool_args})")

            if tool_name in TOOL_REGISTRY:
                try:
                    result = TOOL_REGISTRY[tool_name](**tool_args)
                except Exception as e:
                    result = {"error": str(e)}
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            preview = json.dumps(result, ensure_ascii=False)
            print(f"📥 Result: {preview[:400]}{'...' if len(preview) > 400 else ''}")

            tool_response_parts.append(types.Part.from_function_response(
                name=tool_name,
                response=result,
            ))

        # --- Append tool results to history as a "user" turn ---
        history.append(types.Content(role="user", parts=tool_response_parts))

    print("\n⚠️ Hit max iterations without a final verdict.")
    return None


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    if not GEMINI_API_KEY or not SERPER_API_KEY:
        print("❌ Set GEMINI_API_KEY and SERPER_API_KEY env vars first.")
        print("   Gemini: https://aistudio.google.com/app/apikey")
        print("   Serper: https://serper.dev")
        exit(1)

    run_agent() 
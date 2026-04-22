"""
Smart shopping assistant. Python prototype.
Run: uv run agent.py
"""

import os
import json
import requests
from google import genai
from dotenv import load_dotenv


# ================================================
# CONFIG
# ================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

MAX_ITERATIONS = 5

print("\n LLM Used: ", GEMINI_MODEL)
client = genai.Client(api_key=GEMINI_API_KEY)

# ================================================
# SIMPLE LLM RUN
# ================================================

# response = client.models.generate_content(model=GEMINI_MODEL, contents="Tell me a joke")
# print(response.text)

# ================================================
# THINKING LLM RUN
# ================================================
# from google.genai import types

# response = client.models.generate_content(
#     model=GEMINI_MODEL,
#     contents="What is 2 raised to the pwoer of 5?",
#     config=types.GenerateContentConfig(
#         thinking_config=types.ThinkingConfig(include_thoughts=True)
#     ),
# )

# print("\n === FINAL ANSWER ====")
# print(response.text)

# ================================================
# TOOLS - these are what agent can call
# ================================================

def get_current_product():
    """
    In the Chrome extension, this reads the product from the page DOM.
    For the Python prototype, we hardcode a realistic example.
    """
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
    payload = {"q": query, "gl": "in", "num": 8}  # gl=in -> India results
    
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    data = resp.json()

    # Keep only fields the LLM actually needs — saves tokens
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
        headers = {"User-Agent": "Mozilla/5.0 (shopping-agent)"}
        resp = requests.get(url, headers=headers, timeout=15)
        # Very naive text extraction — good enough for prototype.
        # For better results, use BeautifulSoup: pip install beautifulsoup4
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return {"url": url, "text": text[:3000]}  # cap to keep context small
    except Exception as e:
        return {"url": url, "error": str(e)}


# Registry: maps tool names (what the LLM says) to actual Python functions
TOOL_REGISTRY = {
    "get_current_product": get_current_product,
    "search_web": search_web,
    "fetch_page_text": fetch_page_text,
}

# ============================================================
# TOOL SCHEMAS — what the LLM sees about each tool
# ============================================================
TOOL_DECLARATIONS = [
    {
        "name": "get_current_product",
        "description": "Get the product the user is currently viewing (name, price, site, url). Call this FIRST.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "search_web",
        "description": (
            "Search the web. Use for finding prices on other sites "
            "(e.g. 'Sony WH-1000XM5 price India') or for finding reviews "
            "(e.g. 'Sony WH-1000XM5 reddit review problems')."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_page_text",
        "description": "Fetch the text content of a specific URL. Use when a search snippet isn't enough and you need to read a page in depth.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Full URL to fetch"}
            },
            "required": ["url"],
        },
    },
]


# ============================================================
# SYSTEM PROMPT
# ============================================================
SYSTEM_PROMPT = """You are a smart shopping assistant.

Your job: given a product the user is viewing, decide if they should BUY IT HERE, BUY IT ELSEWHERE, or SKIP.

Follow this process:
1. Call get_current_product() to see what they're looking at.
2. Call search_web() to compare prices on other Indian sites (Flipkart, Croma, Reliance Digital, etc.).
3. Call search_web() again to check reviews — look for Reddit threads or detailed reviews mentioning problems.
4. Optionally call fetch_page_text() on one important result if you need more detail.
5. Give a clear verdict with: recommendation, best price found & where, key pros, key cons.

Rules:
- Prefer Indian sources (prices in ₹).
- Do not call more than 5 tools total.
- When you have enough info, stop calling tools and give the final verdict.
- Be concise in the final verdict — the user wants a decision, not an essay.
"""



# ============================================================
# AGENT LOOP
# ============================================================

def run_agent():
    """Runs the multi-turn agent loop and prints each step."""
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        tools=[{"function_declarations": TOOL_DECLARATIONS}],
        system_instruction=SYSTEM_PROMPT,
    )
    
    # This is the "history" — grows every turn. Matches the assignment requirement.
    history = [
        {"role": "user", "parts": [{"text": "Should I buy this product?"}]}
    ]
    
    print("=" * 60)
    print("🛒 SMART SHOPPING AGENT")
    print("=" * 60)
    
    for iteration in range(MAX_ITERATIONS):
        print(f"\n───── Iteration {iteration + 1} ─────")
        
        # --- Step 1: Call the LLM with the FULL history ---
        response = model.generate_content(history)
        candidate = response.candidates[0]
        parts = candidate.content.parts
        
        # --- Step 2: Inspect what the LLM produced ---
        tool_calls = []
        text_output = ""
        for part in parts:
            if hasattr(part, "function_call") and part.function_call.name:
                tool_calls.append(part.function_call)
            elif hasattr(part, "text") and part.text:
                text_output += part.text
        
        # Print the LLM's reasoning text (if any)
        if text_output.strip():
            print(f"\n💭 LLM reasoning:\n{text_output.strip()}")
        
        # --- Step 3: If no tool calls, we're done ---
        if not tool_calls:
            print("\n" + "=" * 60)
            print("✅ FINAL VERDICT")
            print("=" * 60)
            print(text_output.strip())
            return text_output
        
        # --- Step 4: Append the LLM's response to history ---
        history.append({"role": "model", "parts": parts})
        
        # --- Step 5: Execute each tool call and append results ---
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
            
            # Print a short preview so the reasoning chain is visible
            preview = json.dumps(result, ensure_ascii=False)
            print(f"📥 Result: {preview[:400]}{'...' if len(preview) > 400 else ''}")
            
            tool_response_parts.append({
                "function_response": {
                    "name": tool_name,
                    "response": result,
                }
            })
        
        # Append all tool results as a single "user" turn (Gemini's convention)
        history.append({"role": "user", "parts": tool_response_parts})
    
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


# 🛒 Smart Shopping Agent

An agentic AI Chrome extension that analyzes any Amazon India product page and tells you whether to **buy it here**, **buy it elsewhere**, or **skip it** — by comparing prices across Indian retailers and checking real reviews, all through a live, visible reasoning chain.

---

## ✨ What It Does

You're shopping on Amazon India. You see a product. You wonder:

- Is this a good price?
- Is it cheaper somewhere else?
- What do real users say about it?

Click the extension icon. Watch the agent reason through those exact questions in real time — every thought, every tool call, every result — and deliver a verdict.

### Example run

```
───── Iteration 1 ─────
💭 I need to first see what product the user is looking at.
🔧 Tool call: get_current_product()
📥 Result: { name: "Sony WH-1000XM5", price: ₹29,990, site: "amazon.in" }

───── Iteration 2 ─────
💭 Got the product. Now I'll search for prices on other Indian sites.
🔧 Tool call: search_web({ query: "Sony WH-1000XM5 price India" })
📥 Result: Flipkart: ₹27,490 | Croma: ₹28,999 | Reliance Digital: ₹29,490

───── Iteration 3 ─────
💭 Flipkart is ₹2,500 cheaper. Let me check reviews for any issues.
🔧 Tool call: search_web({ query: "Sony WH-1000XM5 reddit review problems" })
📥 Result: Mostly positive; some users report weaker ANC in windy conditions

✅ Verdict: BUY ELSEWHERE
- Best price: ₹27,490 on Flipkart (save ₹2,500)
- Pros: Excellent ANC, 30-hour battery, comfortable
- Cons: ANC slightly weaker than XM4 in windy conditions
```

---

## 🧠 The Agentic Concept

This project demonstrates a core pattern in agentic AI:

> **An LLM cannot answer the question alone → so it calls tools → observes results → calls more tools → eventually synthesizes a final answer.**

The agent:

1. **Cannot answer without tools** — it doesn't know today's prices or recent reviews
2. **Runs multiple LLM calls** (up to 5 iterations) in a loop
3. **Passes the complete history** to every call, so the model sees everything that's happened so far
4. **Decides for itself** when to call a tool vs. when to stop and give the verdict
5. **Exposes its reasoning chain** — every intermediate step is streamed to the UI, not just the final answer

### The Loop

```
┌─────────────────────────────────────────────┐
│  User clicks "Analyze this product"         │
│          ↓                                  │
│  ┌─────────────────────────────────┐        │
│  │ Call Gemini with FULL history   │←─┐     │
│  └─────────────────────────────────┘  │     │
│          ↓                            │     │
│  Does response have a tool call?      │     │
│     │                                 │     │
│     ├── YES → Execute tool            │     │
│     │         Append result to history│     │
│     │         (pause 5s for rate limit)┘    │
│     │                                       │
│     └── NO  → Render final verdict          │
└─────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Choice |
|---|---|
| LLM | Google Gemini (`gemini-3-flash-preview`) via REST API |
| Search | [Serper.dev](https://serper.dev) Google Search API (free tier) |
| UI | Chrome Extension (Manifest V3) with Side Panel |
| Languages | Vanilla JavaScript (extension), Python (prototype) |

No frameworks, no build step. The extension is pure HTML/CSS/JS loaded directly into Chrome.

---

## 📂 Project Structure

```
EAG3-S3/
├── agent.py                    # Python prototype (stand-alone CLI version)
├── .env.example                # Template for Python env vars
├── shopping-agent/             # Chrome extension
│   ├── manifest.json           # Extension config (permissions, side panel)
│   ├── background.js           # Agent loop — Gemini calls, tool execution
│   ├── content.js              # Runs inside Amazon pages, extracts product DOM
│   ├── popup.html              # Side panel UI
│   ├── popup.js                # Renders reasoning chain cards
│   ├── popup.css               # Styling
│   ├── config.example.js       # Template for extension API keys
│   ├── config.js               # ⚠️ Your real keys (gitignored)
│   └── icons/                  # Extension icons (16/48/128 px)
└── README.md
```

---

## 🧰 The Agent's Tools

The LLM has exactly three tools available to it:

### `get_current_product()`
Reads the product details (name, price, URL) from the active Amazon.in tab's DOM. Implemented in `content.js`, called via Chrome message passing.

### `search_web(query)`
Calls Serper.dev to get Google search results. The agent uses this for both price comparison and review research.

### `fetch_page_text(url)`
Fetches and extracts the visible text of any URL. Used when a search snippet isn't detailed enough.

The agent chooses **which** tool to call and **what** to pass — nothing is hard-coded.

---

## 🚀 Getting Started

### 1. Prerequisites

- **Chrome 114+** (for the Side Panel API)
- A **Gemini API key** → [Google AI Studio](https://aistudio.google.com/app/apikey) (free tier)
- A **Serper.dev API key** → [serper.dev](https://serper.dev) (2,500 free searches)

### 2. Clone the Repo

```bash
git clone https://github.com/satyasundar/EAG3-S3.git
cd EAG3-S3
```

### 3. Set Up the Chrome Extension

```bash
cd shopping-agent
cp config.example.js config.js
```

Edit `config.js` and paste your real API keys:

```javascript
export const GEMINI_API_KEY = "your_gemini_key";
export const SERPER_API_KEY = "your_serper_key";
export const MODEL_NAME = "gemini-3-flash-preview";
export const MAX_ITERATIONS = 5;
export const THROTTLE_MS = 5000;
```

> ⚠️ `config.js` is gitignored. Never commit it.

### 4. Load the Extension into Chrome

1. Open `chrome://extensions/`
2. Toggle **Developer mode** (top right)
3. Click **Load unpacked** → select the `shopping-agent/` folder
4. Pin the extension to your toolbar (optional)

### 5. Use It

1. Open any Amazon India product page, e.g. `https://www.amazon.in/dp/B09XS7JWHH`
2. Click the extension icon → the Side Panel opens
3. Click **Analyze this product**
4. Watch the agent reason through the decision

---

## 🐍 Running the Python Prototype

If you want to play with the agent logic without the browser, use the standalone Python version:

```bash
uv init
uv add google-genai requests beautifulsoup4 python-dotenv
cp .env.example .env
# Edit .env with your keys
uv run agent.py
```

The Python version uses a hardcoded product for testing, but runs the exact same agent loop. Useful for iterating on prompts before touching the extension.

---

## ⚙️ How It Works — A Walkthrough

### The Three Contexts of a Chrome Extension

An extension runs code in three isolated contexts that communicate via messages:

| Context | File | What runs here |
|---|---|---|
| **Content script** | `content.js` | Injected into the Amazon tab; reads the product DOM |
| **Background (service worker)** | `background.js` | The agent loop — calls Gemini and Serper |
| **Side Panel UI** | `popup.html` / `popup.js` | Renders the reasoning chain cards |

The flow:

```
Popup → (message) → Background → (message) → Content script → DOM
                         ↓
                   Gemini REST API
                         ↓
                   Serper REST API
                         ↓
Popup ← (stream of steps) ← Background
```

### The Growing History

Every iteration passes the **entire conversation history** to Gemini:

```javascript
// Iteration 1:  [user]
// Iteration 2:  [user, model, tool_result]
// Iteration 3:  [user, model, tool_result, model, tool_result]
// ...
```

This is what makes the agent "stateful" across iterations despite the LLM being stateless. Every call to Gemini sees the full context of what's happened.

### The Reasoning-Chain UI

Every meaningful step — iteration start, thinking text, tool call, tool result, final verdict — is streamed from `background.js` to the side panel via `chrome.runtime.sendMessage`. The UI renders each as a colored card, giving the user a live view of the agent's decision process.

### Rate Limit Handling

Gemini's free tier is rate-limited (~15 requests/min). The loop pauses `THROTTLE_MS` milliseconds between iterations to stay safely under the limit. The pause is configurable in `config.js`.

---

## 🔮 Future Ideas

- Support Flipkart and other Indian retailers
- Cache previous analyses (so re-running on the same product is instant)
- Let the agent check "buy vs wait" by looking at price history
- Options page for users to paste their own API keys
- Export the reasoning chain as Markdown for sharing

---

## 📜 License

MIT — free to learn from, fork, and break.
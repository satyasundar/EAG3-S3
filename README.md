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
Shopping Agent
Analyze again
🛒 Agent started with gemma-4-31b-it
───── Iteration 1 ─────
💭 Thinking
The user is asking if they should buy the product they are currently viewing.
I need to follow the process outlined in the system instructions:
1. Call `get_current_product()` to identify the product.
2. Search for prices on other Indian sites (Flipkart, Croma, Reliance Digital).
3. Search for reviews/problems (Reddit).
4. Synthesize the information and provide a verdict (BUY IT HERE, BUY IT ELSEWHERE, or SKIP).

Let's start with step 1.
🔧 Tool call: get_current_product
{}
📥 Result: get_current_product
{
  "name": "Sony HT-G700 3.1ch 4K Dolby Atmos/DTS:X Soundbar for TV with Wireless subwoofer, 3.1ch Home Theater System (400W, Surround Sound,Bluetooth Connectivity, HDMI & Optical Connectivity, 4k HDR) - Black",
  "price_text": "₹24990.00",
  "price_inr": 24990,
  "site": "amazon.in",
  "url": "https://www.amazon.in/Sony-HT-G700-3-1-Channel-Dolby-Atmos/dp/B0856M2T37/?_encoding=UTF8&pd_rd_w=3SiY7&content-id=amzn1.sym.9edad6de-f85d-41dd-a893-96a2a0223a93%3Aamzn1.symc.b1464ab7-6d6a-4fc8-be8f-f2e9b...
⌛️ Waiting for 6s to respect rate limits...
───── Iteration 2 ─────
💭 Thinking
The product is the Sony HT-G700 Soundbar.
Price: ₹24,990 on Amazon.in.

Now I need to:
1. Compare prices on other Indian sites (Flipkart, Croma, Reliance Digital).
2. Check for reviews and common problems (Reddit, etc.).
🔧 Tool call: search_web
{
  "query": "Sony HT-G700 price India Flipkart Croma Reliance Digital"
}
📥 Result: search_web
{
  "query": "Sony HT-G700 price India Flipkart Croma Reliance Digital",
  "results": [
    {
      "title": "Buy SONY HT-G700 400W Bluetooth Soundbar with Remote (Dolby ...",
      "snippet": "SONY HT-G700 400W Bluetooth Soundbar with Remote (Dolby Digital, 3.1 Channel, Black) ; MRP: ₹51,990.00 ; Super Savings (5 OFFERS) ; IDFC Bank. 7.5% Upto Rs 7500 ...",
      "link": "https://www.croma.com/sony-ht-g700-400w-bluetooth-soundbar-with-remote-dolby-digital-3-1-channel-black-/p/227255?srsltid=Afm...
🔧 Tool call: search_web
{
  "query": "Sony HT-G700 soundbar review reddit problems"
}
📥 Result: search_web
{
  "query": "Sony HT-G700 soundbar review reddit problems",
  "results": [
    {
      "title": "Sony HT-G700 sound issues - Reddit",
      "snippet": "Yep, everything you're experiencing is normal for this soundbar. I brought the same one and I have the same issue. It's really annoying because ...",
      "link": "https://www.reddit.com/r/sony/comments/t1j1ay/sony_htg700_sound_issues/"
    },
    {
      "title": "Sony HT-G700 Soundbar Review - RTINGS.com",
      "snippet": "The Sony HT-G700 i...
⌛️ Waiting for 6s to respect rate limits...
───── Iteration 3 ─────
💭 Thinking
Price Comparison:
- Amazon: ₹24,990
- Flipkart: ₹24,990 (with an offer showing it could be as low as ₹21,840)
- Croma: Lists an MRP of ₹51,990 (actual selling price not explicitly in snippet but likely higher or similar).

Reviews/Problems:
- Reddit: Mentions of "sound issues" being common/normal for this model.
- RTINGS: "Satisfactory for mixed use," "boomy sound profile," "lacks thumpy low-bass."

Analysis:
The price is identical on Amazon and Flipkart, though Flipkart might have bank offers bringing it down to ₹21,840.
However, the feedback on the sound quality (boomy, lacks punchy bass) and reported sound issues on Reddit are red flags.

Verdict thinking:
The price is decent for a Sony brand soundbar, but if the user wants high-quality audio, the "boomy" sound and reported issues might make it a "SKIP" or "BUY ELSEWHERE" (look for a better model). But since the user is asking about *this* product, I should evaluate if the value is there.

Let's double check if there's a better alternative in a similar price range (like Samsung or JBL) just to be a "smart" assistant, but the core task is to decide if they should buy *this* product.

Actually, I have enough to give a verdict.
Recommendation: SKIP or BUY ELSEWHERE (Flipkart for a slightly better price if they really want it, but generally maybe not the best choice for the money).
Wait, the Reddit thread is quite old (t1j1ay - wait, let me look at the dates if possible. The snippet says "everything you're experiencing is normal").
The RTINGS review is professional and mentions the "boomy" profile.

I will recommend BUY ELSEWHERE (Flipkart for a potential ₹21,840 price) but warn them about the sound profile. Or, if the quality is a major concern, SKIP.

Actually, for ₹25k, there are often better options. But the prompt asks for a decision on *this* product.

Verdict:
- Best Price: ₹21,840 (Flipkart, with offers) vs ₹24,990 (Amazon).
- Pros: Brand value, Dolby Atmos/DTS:X support, decent for casual TV watching.
- Cons: Boomy sound, lacks deep bass punch, reported sound issues on Reddit.

Final decision: BUY ELSEWHERE (Flipkart) if the user is set on this model, but overall a "SKIP" if they want high-fidelity sound. I'll frame it as "BUY ELSEWHERE" for the price but with a strong warning.

Wait, I can check if there is a newer version or a better alternative in the same price range quickly to provide a better recommendation. But I've already used 3 tool calls (get_current_product, search_web x2). I have 2 left. I'll do one quick search for "Best soundbar under 25000 India 2024" to see if this is still competitive.
🔧 Tool call: search_web
{
  "query": "best soundbar under 25000 India 2024 reddit"
}
📥 Result: search_web
{
  "query": "best soundbar under 25000 India 2024 reddit",
  "results": [
    {
      "title": "[India] Best Soundbar under ₹25K in 2025? Samsung Q600F vs ...",
      "snippet": "I've heard mixed reviews — some say Samsung's B series is better for music and Q for movies, others mention JBL being punchy but less immersive.",
      "link": "https://www.reddit.com/r/Soundbars/comments/1mf0dpp/india_best_soundbar_under_25k_in_2025_samsung/"
    },
    {
      "title": "Best Soundbars under 25000(IN...
⌛️ Waiting for 6s to respect rate limits...
───── Iteration 4 ─────
💭 Thinking
The Sony HT-G700 is priced at ₹24,990.
Flipkart offers it for the same price, but with bank offers, it can go down to ₹21,840.
However, reviews from RTINGS and Reddit suggest it has a "boomy" sound profile and lacks thumpy bass, with some users experiencing "normal" (meaning common) sound issues.
Alternatives in the ₹20k-30k range include the Samsung Q-series (like Q600) and LG options, which are often cited as better for specific uses (movies/music).

Verdict:
The price on Amazon is standard, but Flipkart is potentially cheaper. However, given the performance reviews (boomy sound, lack of deep bass, reported issues), this isn't the "best" option in its class.

Recommendation: **BUY ELSEWHERE / SKIP**.
- Buy elsewhere (Flipkart) only if you are dead set on Sony and want the lower price (₹21,840).
- Skip if you want high-quality bass or a more balanced sound profile (Samsung Q600 is a strong alternative).

I have enough information.Verdict: **BUY ELSEWHERE (or SKIP)**

While the price is competitive, there are better options for your money in terms of sound quality.

**💰 Price Comparison**
*   **Amazon:** ₹24,990
*   **Flipkart:** ₹24,990 (Can drop to **₹21,840** with specific bank offers).
*   **Verdict on Price:** If you are determined to get this specific model, **Flipkart** is the better bet for a lower final price.

**✅ Pros**
*   **Brand Reliability:** Sony generally offers great build quality and support.
*   **Features:** Supports Dolby Atmos and DTS:X, which is great for a cinematic feel.
*   **Connectivity:** Good range of options (HDMI, Optical, Bluetooth).

**❌ Cons**
*   **Sound Profile:** Professional reviews (like RTINGS) describe the sound as "boomy," meaning it lacks the tight, punchy bass needed for high-end movies or music.
*   **Known Issues:** Reddit users have reported consistent sound issues that appear to be common for this specific model.
*   **Competition:** In the ₹20k–₹25k range, the **Samsung Q-series (e.g., Q600)** is often cited as having better clarity and a more immersive experience for movies.

**Final Advice:**
If you just want a branded soundbar for casual TV watching, buy it on **Flipkart** to save money. However, if you care about deep, clean bass and high-fidelity audio, **SKIP** this and look at the Samsung Q-series or LG alternatives.
✅ Verdict
The Sony HT-G700 is priced at ₹24,990.
Flipkart offers it for the same price, but with bank offers, it can go down to ₹21,840.
However, reviews from RTINGS and Reddit suggest it has a "boomy" sound profile and lacks thumpy bass, with some users experiencing "normal" (meaning common) sound issues.
Alternatives in the ₹20k-30k range include the Samsung Q-series (like Q600) and LG options, which are often cited as better for specific uses (movies/music).

Verdict:
The price on Amazon is standard, but Flipkart is potentially cheaper. However, given the performance reviews (boomy sound, lack of deep bass, reported issues), this isn't the "best" option in its class.

Recommendation: **BUY ELSEWHERE / SKIP**.
- Buy elsewhere (Flipkart) only if you are dead set on Sony and want the lower price (₹21,840).
- Skip if you want high-quality bass or a more balanced sound profile (Samsung Q600 is a strong alternative).

I have enough information.Verdict: **BUY ELSEWHERE (or SKIP)**

While the price is competitive, there are better options for your money in terms of sound quality.

**💰 Price Comparison**
*   **Amazon:** ₹24,990
*   **Flipkart:** ₹24,990 (Can drop to **₹21,840** with specific bank offers).
*   **Verdict on Price:** If you are determined to get this specific model, **Flipkart** is the better bet for a lower final price.

**✅ Pros**
*   **Brand Reliability:** Sony generally offers great build quality and support.
*   **Features:** Supports Dolby Atmos and DTS:X, which is great for a cinematic feel.
*   **Connectivity:** Good range of options (HDMI, Optical, Bluetooth).

**❌ Cons**
*   **Sound Profile:** Professional reviews (like RTINGS) describe the sound as "boomy," meaning it lacks the tight, punchy bass needed for high-end movies or music.
*   **Known Issues:** Reddit users have reported consistent sound issues that appear to be common for this specific model.
*   **Competition:** In the ₹20k–₹25k range, the **Samsung Q-series (e.g., Q600)** is often cited as having better clarity and a more immersive experience for movies.

**Final Advice:**
If you just want a branded soundbar for casual TV watching, buy it on **Flipkart** to save money. However, if you care about deep, clean bass and high-fidelity audio, **SKIP** this and look at the Samsung Q-series or LG alternatives.
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

| Component | Choice                                                         |
| --------- | -------------------------------------------------------------- |
| LLM       | Google Gemini (`gemini-3-flash-preview`) via REST API          |
| Search    | [Serper.dev](https://serper.dev) Google Search API (free tier) |
| UI        | Chrome Extension (Manifest V3) with Side Panel                 |
| Languages | Vanilla JavaScript (extension), Python (prototype)             |

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

| Context                         | File                      | What runs here                                      |
| ------------------------------- | ------------------------- | --------------------------------------------------- |
| **Content script**              | `content.js`              | Injected into the Amazon tab; reads the product DOM |
| **Background (service worker)** | `background.js`           | The agent loop — calls Gemini and Serper            |
| **Side Panel UI**               | `popup.html` / `popup.js` | Renders the reasoning chain cards                   |

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

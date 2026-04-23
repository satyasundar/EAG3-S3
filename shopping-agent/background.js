import {
  GEMINI_API_KEY,
  SERPER_API_KEY,
  MODEL_NAME,
  MAX_ITERATIONS,
  THROTTLE_MS,
} from "./config.js";

// ============================================================
// TOOL IMPLEMENTATIONS
// ============================================================

async function getCurrentProduct() {
  // Ask the content script (running in the active Amazon tab) for product info
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.url || !tab.url.includes("amazon.in")) {
    return { error: "Please open an amazon.in product page first." };
  }
  try {
    const result = await chrome.tabs.sendMessage(tab.id, {
      type: "GET_PRODUCT",
    });
    return result || { error: "No response from content script." };
  } catch (e) {
    return {
      error: `Content script not ready: ${e.message}. Try reloading the Amazon tab.`,
    };
  }
}

async function searchWeb({ query }) {
  const resp = await fetch("https://google.serper.dev/search", {
    method: "POST",
    headers: {
      "X-API-KEY": SERPER_API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ q: query, gl: "in", num: 8 }),
  });
  const data = await resp.json();
  const results = (data.organic || []).slice(0, 8).map((item) => ({
    title: item.title,
    snippet: item.snippet,
    link: item.link,
  }));
  return { query, results };
}

async function fetchPageText({ url }) {
  try {
    const resp = await fetch(url, {
      headers: { "User-Agent": "Mozilla/5.0 shopping-agent" },
    });
    const html = await resp.text();
    // Very naive text extraction — strip tags and whitespace
    const text = html
      .replace(/<script[\s\S]*?<\/script>/gi, " ")
      .replace(/<style[\s\S]*?<\/style>/gi, " ")
      .replace(/<[^>]+>/g, " ")
      .replace(/\s+/g, " ")
      .trim();
    return { url, text: text.slice(0, 3000) };
  } catch (e) {
    return { url, error: e.message };
  }
}

const TOOL_REGISTRY = {
  get_current_product: getCurrentProduct,
  search_web: searchWeb,
  fetch_page_text: fetchPageText,
};

// ============================================================
// TOOL DECLARATIONS (for Gemini)
// ============================================================

const TOOL_DECLARATIONS = [
  {
    name: "get_current_product",
    description:
      "Get the product the user is currently viewing (name, price, site, url). Call this FIRST.",
    parameters: { type: "object", properties: {} },
  },
  {
    name: "search_web",
    description:
      "Search the web. Use for finding prices on other sites (e.g. 'Sony WH-1000XM5 price India') or for finding reviews (e.g. 'Sony WH-1000XM5 reddit review problems').",
    parameters: {
      type: "object",
      properties: { query: { type: "string", description: "Search query" } },
      required: ["query"],
    },
  },
  {
    name: "fetch_page_text",
    description:
      "Fetch the text content of a specific URL. Use when a search snippet isn't enough.",
    parameters: {
      type: "object",
      properties: { url: { type: "string", description: "Full URL to fetch" } },
      required: ["url"],
    },
  },
];

// ============================================================
// SYSTEM PROMPT
// ============================================================

const SYSTEM_PROMPT = `You are a smart shopping assistant.

Your job: given a product the user is viewing, decide if they should BUY IT HERE, BUY IT ELSEWHERE, or SKIP.

CRITICAL — REASONING FORMAT:
Before EVERY tool call, you MUST first write a short reasoning paragraph explaining:
- What you've learned so far from previous tool results (if any)
- What you still need to find out
- Why the next tool call is the right next step

Structure every turn as:
  <1-3 sentences of reasoning>
  <then the tool call>

Never call a tool without reasoning text preceding it. This applies to EVERY iteration, not just the first.

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
- Be concise — the user wants a decision, not an essay.`;

// ============================================================
// GEMINI REST CALL
// ============================================================

async function callGemini(history) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${GEMINI_API_KEY}`;

  const body = {
    system_instruction: { parts: [{ text: SYSTEM_PROMPT }] },
    contents: history,
    tools: [{ function_declarations: TOOL_DECLARATIONS }],
    tool_config: { function_calling_config: { mode: "AUTO" } },
  };

  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const errText = await resp.text();
    throw new Error(`Gemini API error ${resp.status}: ${errText}`);
  }

  return await resp.json();
}

// ============================================================
// AGENT LOOP
// ============================================================

// Send a step to the popup so it can render it live
function sendStep(step) {
  chrome.runtime.sendMessage({ type: "AGENT_STEP", step }).catch(() => {
    // Popup might be closed — ignore
  });
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function runAgent() {
  const history = [
    { role: "user", parts: [{ text: "Should I buy this product?" }] },
  ];

  sendStep({ kind: "info", text: `🛒 Agent started with ${MODEL_NAME}` });

  for (let iteration = 0; iteration < MAX_ITERATIONS; iteration++) {
    //Respect Gemini free-tier rate limits: pause between iterations

    if (iteration > 0) {
      sendStep({
        kind: "info",
        text: `⌛️ Waiting for ${THROTTLE_MS / 1000}s to respect rate limits...`,
      });
      await sleep(THROTTLE_MS);
    }
    sendStep({ kind: "iteration", number: iteration + 1 });

    let response;
    try {
      response = await callGemini(history);
    } catch (e) {
      sendStep({ kind: "error", text: e.message });
      return;
    }

    const candidate = response.candidates?.[0];
    if (!candidate) {
      sendStep({ kind: "error", text: "No response from Gemini." });
      return;
    }

    const parts = candidate.content?.parts || [];
    const toolCalls = [];
    let textOutput = "";

    for (const part of parts) {
      if (part.functionCall) {
        toolCalls.push(part.functionCall);
      } else if (part.text) {
        textOutput += part.text;
      }
    }

    if (textOutput.trim()) {
      sendStep({ kind: "thinking", text: textOutput.trim() });
    }

    // No tool calls → final answer
    if (toolCalls.length === 0) {
      sendStep({
        kind: "final",
        text: textOutput.trim() || "(no text response)",
      });
      return;
    }

    // Append model's response to history
    history.push({ role: "model", parts });

    // Execute each tool call
    const toolResponseParts = [];
    for (const call of toolCalls) {
      const name = call.name;
      const args = call.args || {};

      sendStep({ kind: "tool_call", name, args });

      let result;
      if (TOOL_REGISTRY[name]) {
        try {
          result = await TOOL_REGISTRY[name](args);
        } catch (e) {
          result = { error: e.message };
        }
      } else {
        result = { error: `Unknown tool: ${name}` };
      }

      sendStep({ kind: "tool_result", name, result });

      toolResponseParts.push({
        functionResponse: { name, response: result },
      });
    }

    // Append tool results to history as a "user" turn
    history.push({ role: "user", parts: toolResponseParts });
  }

  sendStep({
    kind: "error",
    text: "Hit max iterations without a final verdict.",
  });
}

// ============================================================
// MESSAGE HANDLER — popup triggers the agent
// ============================================================

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "RUN_AGENT") {
    runAgent(); // fire and forget; steps are streamed via sendStep
    sendResponse({ started: true });
    return true;
  }
});

// open side panel when user clicks on the extension icon
chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch((err) => console.error(err));
});

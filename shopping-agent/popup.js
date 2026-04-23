const runBtn = document.getElementById("runBtn");
const stepsDiv = document.getElementById("steps");

function addCard(step) {
  const card = document.createElement("div");
  card.className = `card ${step.kind}`;

  let html = "";
  switch (step.kind) {
    case "iteration":
      html = `───── Iteration ${step.number} ─────`;
      break;
    case "info":
      html = step.text;
      break;
    case "thinking":
      html = `<span class="label">💭 Thinking</span><pre>${escapeHtml(step.text)}</pre>`;
      break;
    case "tool_call":
      html = `<span class="label">🔧 Tool call: ${step.name}</span><pre>${escapeHtml(JSON.stringify(step.args, null, 2))}</pre>`;
      break;
    case "tool_result":
      const preview = JSON.stringify(step.result, null, 2).slice(0, 500);
      html = `<span class="label">📥 Result: ${step.name}</span><pre>${escapeHtml(preview)}${preview.length >= 500 ? "..." : ""}</pre>`;
      break;
    case "final":
      html = `<span class="label">✅ Verdict</span><pre>${escapeHtml(step.text)}</pre>`;
      runBtn.disabled = false;
      runBtn.innerText = "Analyze again";
      break;
    case "error":
      html = `<span class="label">❌ Error</span><pre>${escapeHtml(step.text)}</pre>`;
      runBtn.disabled = false;
      runBtn.innerText = "Try again";
      break;
  }

  card.innerHTML = html;
  stepsDiv.appendChild(card);
  card.scrollIntoView({ behavior: "smooth", block: "end" });
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// Receive streamed steps from background
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "AGENT_STEP") addCard(msg.step);
});

runBtn.addEventListener("click", () => {
  stepsDiv.innerHTML = "";
  runBtn.disabled = true;
  runBtn.innerText = "Running...";
  chrome.runtime.sendMessage({ type: "RUN_AGENT" });
});
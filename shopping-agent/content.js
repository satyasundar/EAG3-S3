// Runs inside amazon.in product pages.
// Extracts product info from DOM when background requests it.

function extractProduct() {
  // Amazon.in product pages have these selectors (as of 2025)
  const nameEl = document.querySelector("#productTitle");
  const priceWhole = document.querySelector(".a-price-whole");
  const priceFraction = document.querySelector(".a-price-fraction");
  const priceSymbol = document.querySelector(".a-price-symbol");

  // Fallback: aria-labeled price
  const priceAria = document.querySelector(".a-price .a-offscreen");

  let priceText = null;
  let priceNumeric = null;

  if (priceWhole) {
    const whole = priceWhole.innerText.replace(/[^\d]/g, "");
    const fraction = priceFraction ? priceFraction.innerText.replace(/[^\d]/g, "") : "00";
    priceText = `${priceSymbol ? priceSymbol.innerText : "₹"}${whole}.${fraction}`;
    priceNumeric = parseFloat(`${whole}.${fraction}`);
  } else if (priceAria) {
    priceText = priceAria.innerText;
    const match = priceText.match(/[\d,]+\.?\d*/);
    if (match) priceNumeric = parseFloat(match[0].replace(/,/g, ""));
  }

  const name = nameEl ? nameEl.innerText.trim() : null;

  if (!name) {
    return { error: "Could not find product name. Is this an Amazon product page?" };
  }

  return {
    name,
    price_text: priceText,
    price_inr: priceNumeric,
    site: "amazon.in",
    url: window.location.href,
  };
}

// Listen for requests from the background script
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "GET_PRODUCT") {
    sendResponse(extractProduct());
    return true; // keeps the message channel open for async, though we're sync here
  }
});
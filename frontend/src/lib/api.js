export const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
const API_ROOT = API_BASE.replace(/\/+$/, "");
const REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 45000);

function wsBaseFromApi(apiBase) {
  return apiBase.replace(/^http/, "ws").replace(/\/$/, "");
}

async function post(path, payload = {}, timeoutMs = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);
  let response;
  try {
    response = await fetch(`${API_ROOT}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
  } catch (error) {
    if (error?.name === "AbortError") {
      throw new Error("Request timed out while waking backend. Please wait and retry.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.detail) {
        detail = String(body.detail);
      }
    } catch {
      // Keep generic detail fallback.
    }
    throw new Error(detail);
  }

  return response.json();
}

export function fetchLegalMoves(fen) {
  return post("/legal-moves", { fen });
}

export function movePosition(fen, move) {
  return post("/move", { fen, move });
}

export function analyzePosition(fen, maxDepth, timeLimitMs) {
  return post("/analyze", { fen, max_depth: maxDepth, time_limit_ms: timeLimitMs });
}

export function engineMovePosition(fen, maxDepth, timeLimitMs) {
  return post("/engine-move", { fen, max_depth: maxDepth, time_limit_ms: timeLimitMs });
}

export function resetPosition() {
  return post("/reset", {});
}

export function createSearchSocket() {
  return new WebSocket(`${wsBaseFromApi(API_ROOT)}/ws/search`);
}

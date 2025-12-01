const API_BASE =
  import.meta.env.VITE_BACKEND_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000/api";

export async function analyzeText(text: string, includeUrls = true) {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text, include_urls: includeUrls })
  });

  if (!response.ok) {
    const detail = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(detail.detail || "Failed to analyze text");
  }

  return response.json();
}

export async function scanScreen(includeUrls = true) {
  const response = await fetch(`${API_BASE}/scan-screen`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ include_urls: includeUrls })
  });

  if (!response.ok) {
    const detail = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(detail.detail || "Failed to scan screen");
  }

  return response.json();
}


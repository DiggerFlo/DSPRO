import { getResponse } from './mock.js';

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';
const API_URL  = import.meta.env.VITE_API_URL;

// ── Topics ────────────────────────────────────────────────────────────────────

/**
 * Fetch LLM-generated example questions from the backend.
 * Returns { de: string[], en: string[] } — empty arrays if unavailable.
 */
export async function fetchTopics() {
  if (USE_MOCK || !API_URL) return { de: [], en: [] };
  try {
    const res = await fetch(`${API_URL}/topics`);
    if (!res.ok) return { de: [], en: [] };
    return res.json();
  } catch {
    return { de: [], en: [] };
  }
}

// ── Streaming query ───────────────────────────────────────────────────────────

/**
 * Async generator that streams a RAG response token by token.
 *
 * Yields:
 *   { type: 'token',  content: string }
 *   { type: 'done',   sources: Source[], followUps: string[] }
 *
 * Source shape: { id, title, date, snippet, score, article_id, category, author }
 *
 * Pass an AbortSignal to cancel mid-stream.
 */
export async function* queryStream(question, signal) {
  if (USE_MOCK || !API_URL) {
    const data = getResponse(question);
    for (let i = 0; i < data.answer.length; i += 4) {
      if (signal?.aborted) return;
      yield { type: 'token', content: data.answer.slice(i, i + 4) };
      await new Promise(r => setTimeout(r, 18));
    }
    yield { type: 'done', sources: data.sources, followUps: data.followUps };
    return;
  }

  const res = await fetch(`${API_URL}/query/stream`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ question }),
    signal,
  });

  if (!res.ok) {
    const msg = await res.text().catch(() => res.statusText);
    throw new Error(`Backend-Fehler ${res.status}: ${msg}`);
  }

  const reader  = res.body.getReader();
  const decoder = new TextDecoder();
  let   buffer  = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      try { yield JSON.parse(line.slice(6)); } catch { /* skip malformed */ }
    }
  }
}

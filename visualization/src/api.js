import { getResponse } from './mock.js';

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';
const API_URL = import.meta.env.VITE_API_URL;

/**
 * Query the RAG backend.
 *
 * Returns a Promise<{ answer: string, sources: Source[], followUps: string[] }>
 *
 * Source shape:
 *   { id: number, title: string, date: string, snippet: string, score: number }
 *
 * To connect a real backend:
 *   1. Set VITE_API_URL in .env
 *   2. Set VITE_USE_MOCK=false in .env
 *   3. Adjust the fetch call below to match your API contract
 */
export async function query(question) {
  if (USE_MOCK || !API_URL) {
    await new Promise(r => setTimeout(r, 700 + Math.random() * 600));
    return getResponse(question);
  }

  const res = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

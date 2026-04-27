import { useState } from 'react';
import { SANS } from '../theme.js';

export default function CopyButton({ text, th }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <button
      onClick={handleCopy}
      style={{ background: "none", border: `1px solid ${th.border}`, cursor: "pointer", fontSize: 10, color: th.textMuted, fontFamily: SANS, padding: "3px 8px", borderRadius: 2, display: "flex", alignItems: "center", gap: 5, transition: "all 0.15s" }}
      onMouseEnter={e => { e.currentTarget.style.borderColor = th.text; e.currentTarget.style.color = th.text; }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = th.border; e.currentTarget.style.color = th.textMuted; }}
    >
      {copied ? (
        <>
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          Kopiert
        </>
      ) : (
        <>
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <rect x="9" y="9" width="13" height="13" rx="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
          </svg>
          Kopieren
        </>
      )}
    </button>
  );
}

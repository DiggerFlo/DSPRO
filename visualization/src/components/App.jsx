import { useState, useEffect, useRef, useCallback } from 'react';
import { getTheme, SANS } from '../theme.js';
import { I18N } from '../i18n.jsx';
import { queryStream, fetchTopics, fetchConfig, updateConfig } from '../api.js';
import Cite from './Cite.jsx';
import SourceCard from './SourceCard.jsx';
import CopyButton from './CopyButton.jsx';
import LoadingDots from './LoadingDots.jsx';
import { SunIcon, MoonIcon, ArrowIcon, ChevronUpIcon, HistoryIcon, SettingsIcon } from './Icons.jsx';

// v3: sessions instead of single Q&A entries
const HISTORY_KEY = 'nzz_history_v3';
const MAX_HISTORY  = 20;

function loadHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); } catch { return []; }
}
function saveHistory(list) {
  try { localStorage.setItem(HISTORY_KEY, JSON.stringify(list)); } catch {}
}
function fmtDate(ts) {
  return new Date(ts).toLocaleDateString('de-CH', { day: 'numeric', month: 'short' });
}

function renderInline(text, accent, dark, idPrefix) {
  return text.split(/(\*\*[^*\n]+\*\*|\[\d+(?:,\s*\d+)*\])/g).map((part, i) => {
    if (/^\*\*[^*]+\*\*$/.test(part)) return <strong key={i}>{part.slice(2, -2)}</strong>;
    const m = part.match(/^\[(\d+(?:,\s*\d+)*)\]$/);
    if (m) {
      const nums = m[1].split(',').map(n => +n.trim());
      return <span key={i}>{nums.map((n, j) => <Cite key={j} num={n} accent={accent} dark={dark} idPrefix={idPrefix} />)}</span>;
    }
    return <span key={i}>{part}</span>;
  });
}

const isBulletLine = l => l.startsWith('- ') || l.startsWith('* ');

function renderBody(text, accent, dark, idPrefix) {
  const serif = "'Source Serif 4',Georgia,serif";
  const lines = text.trim().split('\n');
  if (lines.some(isBulletLine)) {
    return (
      <ul style={{ margin: '4px 0 0 0', paddingLeft: 18, fontFamily: serif }}>
        {lines.filter(isBulletLine).map((item, i) => (
          <li key={i} style={{ marginBottom: 6 }}>
            {renderInline(item.slice(2), accent, dark, idPrefix)}
          </li>
        ))}
      </ul>
    );
  }
  return <div style={{ fontFamily: serif }}>{renderInline(text.trim(), accent, dark, idPrefix)}</div>;
}

function renderAnswer(text, accent, dark, idPrefix) {
  const clean      = text.replace(/\*\*Quellen\*\*[\s\S]*$/, '').trim();
  const SANS_LOCAL = 'Inter,system-ui,sans-serif';
  const serif      = "'Source Serif 4',Georgia,serif";

  return clean.split(/\n{2,}/).map((block, bIdx) => {
    const headingMatch = block.match(/^\*\*([^*\n]+)\*\*\s*\n?([\s\S]*)$/);
    if (headingMatch) {
      const [, heading, body] = headingMatch;
      return (
        <div key={bIdx} style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', fontFamily: SANS_LOCAL, marginBottom: 8, opacity: 0.55 }}>
            {heading}
          </div>
          {body.trim() && renderBody(body, accent, dark, idPrefix)}
        </div>
      );
    }
    if (isBulletLine(block.split('\n')[0])) {
      const items = block.split('\n').filter(isBulletLine);
      return (
        <ul key={bIdx} style={{ margin: '0 0 16px 0', paddingLeft: 18, fontFamily: serif }}>
          {items.map((item, i) => (
            <li key={i} style={{ marginBottom: 6 }}>
              {renderInline(item.slice(2), accent, dark, idPrefix)}
            </li>
          ))}
        </ul>
      );
    }
    return (
      <p key={bIdx} style={{ margin: '0 0 14px 0', fontFamily: serif }}>
        {renderInline(block, accent, dark, idPrefix)}
      </p>
    );
  });
}

// ── Toggle-Row für das Settings-Panel ─────────────────────────────────────────
function ToggleRow({ label, value, onChange, disabled, note, th }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: `1px solid ${th.border}` }}>
      <div>
        <span style={{ fontSize: 13, color: disabled ? th.textFaint : th.text, fontFamily: SANS }}>{label}</span>
        {note && <span style={{ fontSize: 10, color: th.textFaint, fontFamily: SANS, marginLeft: 6 }}>{note}</span>}
      </div>
      <button
        disabled={disabled}
        onClick={() => onChange(!value)}
        style={{
          width: 36, height: 20, borderRadius: 10, border: 'none', cursor: disabled ? 'not-allowed' : 'pointer',
          background: value && !disabled ? th.accent : th.borderLight,
          position: 'relative', transition: 'background 0.2s', flexShrink: 0,
          opacity: disabled ? 0.4 : 1,
        }}
      >
        <span style={{
          position: 'absolute', top: 2, left: value ? 18 : 2, width: 16, height: 16,
          borderRadius: '50%', background: '#fff', transition: 'left 0.2s',
        }} />
      </button>
    </div>
  );
}

function SliderRow({ label, value, min, max, step, onChange, th }) {
  return (
    <div style={{ padding: '10px 0', borderBottom: `1px solid ${th.border}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 13, color: th.text, fontFamily: SANS }}>{label}</span>
        <span style={{ fontSize: 12, fontWeight: 600, color: th.accent, fontFamily: SANS }}>{value}</span>
      </div>
      <input
        type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(step < 1 ? parseFloat(e.target.value) : parseInt(e.target.value))}
        style={{ width: '100%', accentColor: th.accent }}
      />
    </div>
  );
}

export default function App() {
  const [dark, setDark]   = useState(() => localStorage.getItem('nzz_dark') === '1');
  const th                = getTheme(dark);
  const [lang, setLang]   = useState('de');
  const t                 = I18N[lang];
  const serif             = `'Source Serif 4',Georgia,serif`;
  const maxWidth          = 980;

  // ── Core state ──────────────────────────────────────────────────────────────
  const [query_,          setQuery_]          = useState('');
  const [messages,        setMessages]        = useState([]);
  const [loading,         setLoading]         = useState(false);
  const [pendingQuestion, setPendingQuestion] = useState('');
  const [error,           setError]           = useState(null);

  // ── Session-basierter Verlauf ────────────────────────────────────────────────
  // Jede Session: { id, ts, messages: [{question, answer, sources, followUps}] }
  const [history,     setHistory]     = useState(loadHistory);
  const [showHistory, setShowHistory] = useState(false);
  const sessionIdRef = useRef(null); // aktuelle Session-ID

  // ── Runtime-Config (vom Backend geladen, im GUI änderbar) ───────────────────
  const [config, setConfig] = useState({
    use_full_article:   false,
    use_reranking:      true,
    top_k_retrieval:    10,
    top_k_final:        5,
    llm_temperature:    0.2,
    show_follow_ups:    true,
    reranker_available: true,
  });
  const [showSettings, setShowSettings] = useState(false);

  // ── Dynamic topics from backend ─────────────────────────────────────────────
  const [topics, setTopics] = useState([]);

  // ── UI state ────────────────────────────────────────────────────────────────
  const [showScrollTop,   setShowScrollTop]   = useState(false);
  const [welcomeClosing,  setWelcomeClosing]  = useState(false);
  const [showWelcome,     setShowWelcome]     = useState(() => !localStorage.getItem('nzz_welcome_seen'));
  const [isMobile,        setIsMobile]        = useState(() => window.innerWidth < 640);

  // ── Refs ────────────────────────────────────────────────────────────────────
  const inputRef           = useRef();
  const abortRef           = useRef(null);
  const lastMessageRef     = useRef();
  const generationRef      = useRef(0);
  const answerAccRef       = useRef('');

  // ── Load topics + config from backend on mount ───────────────────────────────
  useEffect(() => {
    fetchTopics().then(data => {
      if (data?.de?.length > 0) setTopics(data.de);
    });
    fetchConfig().then(cfg => {
      if (cfg) setConfig(prev => ({ ...prev, ...cfg }));
    });
  }, []);

  // ── Standard effects ────────────────────────────────────────────────────────
  useEffect(() => { inputRef.current?.focus(); }, []);

  useEffect(() => {
    document.title = messages.length > 0
      ? `${messages[messages.length - 1].question} – NZZ ContextAI`
      : 'NZZ ContextAI';
  }, [messages]);

  useEffect(() => {
    const h = () => setShowScrollTop(window.scrollY > 320);
    window.addEventListener('scroll', h);
    return () => window.removeEventListener('scroll', h);
  }, []);

  useEffect(() => {
    const h = () => setIsMobile(window.innerWidth < 640);
    window.addEventListener('resize', h);
    return () => window.removeEventListener('resize', h);
  }, []);

  useEffect(() => () => abortRef.current?.abort(), []);

  useEffect(() => {
    const h = e => {
      if (e.key !== 'Escape') return;
      if (showSettings) { setShowSettings(false); return; }
      if (showWelcome) { closeWelcome(); return; }
      if (messages.length > 0 && !loading) resetChat();
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [showSettings, showWelcome, messages.length, loading]);

  useEffect(() => {
    if (messages.length > 0)
      lastMessageRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, [messages.length]);

  useEffect(() => {
    document.body.className = dark ? 'dark' : '';
    document.body.style.background = th.bg;
    document.body.style.color = th.text;
  }, [dark, th.bg, th.text]);

  // ── Helpers ─────────────────────────────────────────────────────────────────
  const closeWelcome = () => {
    setWelcomeClosing(true);
    setTimeout(() => {
      localStorage.setItem('nzz_welcome_seen', '1');
      setShowWelcome(false);
      setWelcomeClosing(false);
    }, 240);
  };

  const toggleDark = () => setDark(d => {
    const n = !d;
    localStorage.setItem('nzz_dark', n ? '1' : '0');
    return n;
  });

  const resetChat = () => {
    abortRef.current?.abort();
    ++generationRef.current;
    sessionIdRef.current = null;
    setQuery_(''); setMessages([]); setLoading(false);
    setPendingQuestion(''); setError(null);
    document.title = 'NZZ ContextAI';
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const updateSetting = useCallback(async (key, value) => {
    const patch = { [key]: value };
    setConfig(prev => ({ ...prev, ...patch }));
    await updateConfig(patch);
  }, []);

  /** Restore a saved session from history without a new API call. */
  const restoreConversation = useCallback(session => {
    abortRef.current?.abort();
    ++generationRef.current;
    sessionIdRef.current = session.id;
    setQuery_(''); setLoading(false); setPendingQuestion(''); setError(null);
    setMessages(session.messages.map(m => ({ ...m, done: true })));
    document.title = `${session.messages[0].question} – NZZ ContextAI`;
    setTimeout(() => inputRef.current?.focus(), 50);
  }, []);

  /** Persist a completed Q&A to the current session (or start a new one). */
  const persistToHistory = useCallback((question, answer, sources, followUps) => {
    const msg = { question, answer, sources, followUps };
    setHistory(prev => {
      let next;
      if (sessionIdRef.current !== null) {
        // Zur bestehenden Session hinzufügen
        next = prev.map(s =>
          s.id === sessionIdRef.current
            ? { ...s, ts: Date.now(), messages: [...s.messages, msg] }
            : s
        );
      } else {
        // Neue Session starten
        const newSession = { id: Date.now(), ts: Date.now(), messages: [msg] };
        sessionIdRef.current = newSession.id;
        next = [newSession, ...prev].slice(0, MAX_HISTORY);
      }
      saveHistory(next);
      return next;
    });
  }, []);

  // ── Submit ───────────────────────────────────────────────────────────────────
  const submit = useCallback(q => {
    const question = (q || query_).trim();
    if (!question || loading) return;

    abortRef.current?.abort();
    abortRef.current    = new AbortController();
    const { signal }    = abortRef.current;
    const gen           = ++generationRef.current;
    answerAccRef.current = '';

    setQuery_(''); setLoading(true); setPendingQuestion(question); setError(null);

    (async () => {
      try {
        let firstToken = true;
        for await (const event of queryStream(question, signal)) {
          if (generationRef.current !== gen) break;

          if (event.type === 'token') {
            answerAccRef.current += event.content;
            if (firstToken) {
              firstToken = false;
              setLoading(false);
              setPendingQuestion('');
              setMessages(prev => [
                ...prev,
                { question, answer: event.content, sources: [], done: false },
              ]);
            } else {
              setMessages(prev => {
                const m = [...prev];
                m[m.length - 1] = { ...m[m.length - 1], answer: m[m.length - 1].answer + event.content };
                return m;
              });
            }

          } else if (event.type === 'done') {
            setMessages(prev => {
              const m = [...prev];
              m[m.length - 1] = {
                ...m[m.length - 1],
                sources:   event.sources,
                followUps: event.followUps,
                done:      true,
              };
              return m;
            });
            persistToHistory(question, answerAccRef.current, event.sources, event.followUps);
            inputRef.current?.focus();
          }
        }
      } catch (err) {
        if (err.name === 'AbortError') return;
        if (generationRef.current !== gen) return;
        setLoading(false);
        setPendingQuestion('');
        setError(err.message || 'Backend nicht erreichbar. Ist der API-Server gestartet?');
      }
    })();
  }, [query_, loading, persistToHistory]);

  const handleKey = e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit(); }
  };

  // ── Layout helpers ───────────────────────────────────────────────────────────
  const px          = isMobile ? '12px' : '24px';
  const showSidebar = showHistory && history.length > 0 && !isMobile;
  const examples    = topics.length > 0 ? topics : t.examples;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: th.bg, transition: 'background 0.2s,color 0.2s' }}>

      {/* ── 1. Utility bar ── */}
      <div style={{ background: th.utilBg, height: 32, display: 'flex', alignItems: 'center', flexShrink: 0 }}>
        <div style={{ maxWidth, margin: '0 auto', width: '100%', padding: `0 ${px}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <button
            onClick={() => setShowHistory(!showHistory)}
            title={t.history}
            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, padding: '2px 4px', color: showHistory ? '#fff' : th.utilText, transition: 'color 0.15s' }}
            onMouseEnter={e => e.currentTarget.style.color = '#fff'}
            onMouseLeave={e => e.currentTarget.style.color = showHistory ? '#fff' : th.utilText}
          >
            <HistoryIcon />
            {history.length > 0 && <span style={{ fontSize: 10, fontFamily: SANS, letterSpacing: '0.04em' }}>{history.length}</span>}
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {['de', 'en'].map(l => (
              <button key={l} onClick={() => setLang(l)} style={{ padding: '2px 8px', fontSize: 11, fontWeight: lang === l ? 600 : 400, fontFamily: SANS, border: 'none', background: 'none', cursor: 'pointer', color: lang === l ? '#fff' : th.utilText, letterSpacing: '0.04em', textTransform: 'uppercase', transition: 'color 0.15s' }}>
                {l}
              </button>
            ))}
            <button
              onClick={() => setShowSettings(true)}
              title={t.settingsTitle}
              style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', width: 24, height: 24, color: th.utilText, transition: 'color 0.15s' }}
              onMouseEnter={e => e.currentTarget.style.color = '#fff'}
              onMouseLeave={e => e.currentTarget.style.color = th.utilText}
            >
              <SettingsIcon c="currentColor" />
            </button>
            <button onClick={toggleDark} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', width: 24, height: 24 }}>
              {dark ? <SunIcon c="#888" /> : <MoonIcon c="#888" />}
            </button>
          </div>
        </div>
      </div>

      {/* ── 2. Main header ── */}
      <div style={{ background: '#111', borderBottom: '1px solid #222', flexShrink: 0 }}>
        <div style={{ maxWidth, margin: '0 auto', padding: `0 ${px}`, height: 52, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <button onClick={resetChat} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: `0 ${isMobile ? '0' : '24px'}`, display: 'flex', alignItems: 'center', gap: 12, height: 52 }}>
            <span style={{ fontFamily: "'Times New Roman',Georgia,serif", fontWeight: 700, fontSize: isMobile ? 20 : 26, letterSpacing: '0.01em', color: '#fff', lineHeight: 1 }}>NZZ</span>
            <span style={{ width: 1, height: isMobile ? 14 : 18, background: 'rgba(255,255,255,0.4)', display: 'block' }} />
            <span style={{ fontSize: isMobile ? 10 : 12, fontWeight: 600, color: 'rgba(255,255,255,0.9)', fontFamily: SANS, letterSpacing: '0.04em', textTransform: 'uppercase' }}>ContextAI</span>
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {(messages.length > 0 || loading) && (
              <button
                onClick={resetChat}
                className="fade-up"
                style={{ background: 'none', border: `1px solid ${th.border}`, cursor: 'pointer', fontSize: 11, color: th.textMuted, fontFamily: SANS, padding: '4px 10px', letterSpacing: '0.03em', borderRadius: 2, transition: 'all 0.15s' }}
                onMouseEnter={e => { e.currentTarget.style.borderColor = '#fff'; e.currentTarget.style.color = '#fff'; }}
                onMouseLeave={e => { e.currentTarget.style.borderColor = th.border; e.currentTarget.style.color = th.textMuted; }}
              >
                {isMobile ? '↩' : `↩ ${t.newChat}`}
              </button>
            )}
            {!isMobile && (
              <button
                onClick={() => setShowWelcome(true)}
                style={{ fontSize: 9, fontWeight: 700, color: th.accent, fontFamily: SANS, letterSpacing: '0.1em', border: `1px solid ${th.accent}`, borderRadius: 2, padding: '2px 6px', background: 'none', cursor: 'pointer', transition: 'opacity 0.15s' }}
                onMouseEnter={e => e.currentTarget.style.opacity = '0.6'}
                onMouseLeave={e => e.currentTarget.style.opacity = '1'}
              >
                DEMO
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── 3. Body ── */}
      <div style={{ flex: 1, display: 'flex', maxWidth, margin: '0 auto', width: '100%', padding: `0 ${px}` }}>

        {/* History sidebar */}
        {showSidebar && (
          <aside className="slide-in" style={{ width: 210, flexShrink: 0, borderRight: `1px solid ${th.border}`, paddingTop: 24, paddingRight: 16, paddingBottom: 24, transition: 'border-color 0.2s' }}>
            <div style={{ fontSize: 9, fontWeight: 700, color: th.textMuted, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 12, fontFamily: SANS }}>{t.history}</div>
            {history.map((session) => (
              <button
                key={session.id}
                onClick={() => restoreConversation(session)}
                style={{ display: 'block', width: '100%', textAlign: 'left', background: 'none', border: 'none', borderBottom: `1px solid ${th.border}`, cursor: 'pointer', padding: '9px 0', lineHeight: 1.45, transition: 'color 0.1s' }}
                onMouseEnter={e => e.currentTarget.style.color = th.accent}
                onMouseLeave={e => e.currentTarget.style.color = th.textMid}
              >
                <div style={{ fontSize: 12, color: 'inherit', fontFamily: serif, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 180 }}>
                  {session.messages[0].question}
                </div>
                <div style={{ fontSize: 10, color: th.textFaint, fontFamily: SANS, marginTop: 2, display: 'flex', gap: 6 }}>
                  <span>{fmtDate(session.ts)}</span>
                  {session.messages.length > 1 && (
                    <span>· {session.messages.length} Fragen</span>
                  )}
                </div>
              </button>
            ))}
          </aside>
        )}

        <main style={{ flex: 1, paddingTop: 32, paddingBottom: 80, paddingLeft: showSidebar ? 24 : 0, maxWidth: 660 }}>

          {/* Empty state */}
          {messages.length === 0 && !loading && !error && (
            <div className="fade-up">
              <h1 style={{ fontFamily: serif, fontSize: isMobile ? 22 : 30, fontWeight: 600, lineHeight: 1.2, color: th.text, marginBottom: 10, letterSpacing: '-0.02em' }}>{t.headline}</h1>
              <p style={{ fontSize: 14, color: th.textMid, lineHeight: 1.7, marginBottom: 28, fontFamily: SANS, maxWidth: 520 }}>{t.subhead}</p>
              <div style={{ borderTop: `2px solid ${th.text}`, paddingTop: 16, transition: 'border-color 0.2s' }}>
                <div style={{ fontSize: 9, fontWeight: 700, color: th.textMuted, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 14, fontFamily: SANS }}>{t.examplesLabel}</div>
                {examples.map((q, i) => (
                  <button key={i} onClick={() => submit(q)} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, width: '100%', background: 'none', border: 'none', borderBottom: `1px solid ${th.border}`, padding: '13px 0', cursor: 'pointer', textAlign: 'left', transition: 'color 0.12s', color: th.text }}
                    onMouseEnter={e => { e.currentTarget.style.color = th.accent; e.currentTarget.querySelector('.arr').style.color = th.accent; }}
                    onMouseLeave={e => { e.currentTarget.style.color = th.text; e.currentTarget.querySelector('.arr').style.color = th.textFaint; }}
                  >
                    <span className="arr" style={{ color: th.textFaint, fontSize: 13, flexShrink: 0, marginTop: 2, transition: 'color 0.12s', fontFamily: SANS }}>→</span>
                    <span style={{ fontSize: 14, color: 'inherit', lineHeight: 1.5, fontFamily: serif }}>{q}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Error state */}
          {error && !loading && (
            <div className="fade-up" style={{ padding: '20px 0' }}>
              <div style={{ border: `1px solid ${th.border}`, borderLeft: `3px solid #c0392b`, padding: '14px 16px', background: th.surface }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: '#c0392b', fontFamily: SANS, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 6 }}>Fehler</div>
                <div style={{ fontSize: 13, color: th.textMid, fontFamily: SANS, lineHeight: 1.6 }}>{error}</div>
                <button onClick={() => setError(null)} style={{ marginTop: 12, fontSize: 11, color: th.textMuted, fontFamily: SANS, background: 'none', border: `1px solid ${th.border}`, padding: '4px 10px', cursor: 'pointer' }}>
                  Schliessen
                </button>
              </div>
            </div>
          )}

          {/* Conversation */}
          {messages.map((msg, idx) => {
            const idPrefix = `msg-${idx}`;
            const isLast   = idx === messages.length - 1;
            return (
              <div key={idx} ref={isLast ? lastMessageRef : null} className="fade-up" style={{ marginBottom: 56, paddingTop: idx > 0 ? 32 : 0, borderTop: idx > 0 ? `1px solid ${th.border}` : 'none' }}>
                <div style={{ borderTop: `2px solid ${th.text}`, paddingTop: 14, marginBottom: 16, transition: 'border-color 0.2s' }}>
                  <div style={{ fontSize: 9, fontWeight: 700, color: th.textMuted, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 8, fontFamily: SANS }}>{t.queryLabel}</div>
                  <p style={{ fontFamily: serif, fontSize: isMobile ? 16 : 20, fontWeight: 600, color: th.text, lineHeight: 1.3, letterSpacing: '-0.015em' }}>„{msg.question}"</p>
                </div>
                <div style={{ fontSize: 16, lineHeight: 1.9, color: th.text, marginBottom: msg.done ? 32 : 0, fontFamily: serif, fontWeight: 400 }}>
                  {renderAnswer(msg.answer, th.accent, dark, idPrefix)}
                  {!msg.done && <span className="cursor" style={{ background: th.accent }} />}
                </div>
                {msg.done && (
                  <div className="fade-up">
                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8 }}>
                      <CopyButton text={msg.answer} th={th} />
                    </div>
                    <div style={{ borderTop: `2px solid ${th.text}`, paddingTop: 12, transition: 'border-color 0.2s' }}>
                      <div style={{ fontSize: 9, fontWeight: 700, color: th.textMuted, letterSpacing: '0.12em', textTransform: 'uppercase', fontFamily: SANS }}>{t.sourcesLabel}</div>
                    </div>
                    {msg.sources.map((s, i) => (
                      <SourceCard key={s.id} source={s} index={i} th={th} serif={serif} relevanceLabel={t.relevance} dark={dark} idPrefix={idPrefix} />
                    ))}
                    {config.show_follow_ups && msg.followUps?.length > 0 && isLast && !loading && (
                      <div className="fade-up" style={{ marginTop: 28 }}>
                        <div style={{ fontSize: 9, fontWeight: 700, color: th.textMuted, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 10, fontFamily: SANS }}>{t.followUpsLabel}</div>
                        {msg.followUps.map((q, i) => (
                          <button key={i} onClick={() => submit(q)} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, width: '100%', background: 'none', border: 'none', borderBottom: `1px solid ${th.border}`, padding: '11px 0', cursor: 'pointer', textAlign: 'left', transition: 'color 0.12s', color: th.textMid }}
                            onMouseEnter={e => { e.currentTarget.style.color = th.text; e.currentTarget.querySelector('.arr').style.color = th.text; }}
                            onMouseLeave={e => { e.currentTarget.style.color = th.textMid; e.currentTarget.querySelector('.arr').style.color = th.textFaint; }}
                          >
                            <span className="arr" style={{ color: th.textFaint, fontSize: 12, flexShrink: 0, marginTop: 2, transition: 'color 0.12s', fontFamily: SANS }}>→</span>
                            <span style={{ fontSize: 13, color: 'inherit', lineHeight: 1.5, fontFamily: serif }}>{q}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {/* Loading state */}
          {loading && (
            <div className="fade-up" style={{ marginBottom: 56, paddingTop: messages.length > 0 ? 32 : 0, borderTop: messages.length > 0 ? `1px solid ${th.border}` : 'none' }}>
              <div style={{ borderTop: `2px solid ${th.text}`, paddingTop: 14, marginBottom: 16 }}>
                <div style={{ fontSize: 9, fontWeight: 700, color: th.textMuted, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 8, fontFamily: SANS }}>{t.queryLabel}</div>
                <p style={{ fontFamily: serif, fontSize: isMobile ? 16 : 20, fontWeight: 600, color: th.text, lineHeight: 1.3, letterSpacing: '-0.015em' }}>„{pendingQuestion}"</p>
              </div>
              <LoadingDots color={th.accent} label={t.generating} />
            </div>
          )}
        </main>
      </div>

      {/* ── 4. Input bar ── */}
      <div style={{ position: 'sticky', bottom: 0, background: `linear-gradient(transparent,${th.bg} 32%)`, padding: `16px ${px} 22px`, transition: 'background 0.2s' }}>
        <div style={{ maxWidth, margin: '0 auto' }}>
          <div style={{ paddingLeft: showSidebar ? 234 : 0 }}>
            <div
              style={{ display: 'flex', background: th.inputBg, border: `1px solid ${th.borderLight}`, borderTop: `2px solid ${th.text}`, overflow: 'hidden', transition: 'border-color 0.15s,background 0.2s', boxShadow: `0 1px 8px rgba(0,0,0,${dark ? 0.35 : 0.05})` }}
              onFocusCapture={e => e.currentTarget.style.borderTopColor = th.accent}
              onBlurCapture={e => e.currentTarget.style.borderTopColor = th.text}
            >
              <input
                ref={inputRef}
                value={query_}
                onChange={e => setQuery_(e.target.value)}
                onKeyDown={handleKey}
                placeholder={t.placeholder}
                style={{ flex: 1, padding: '12px 14px', fontSize: 16, border: 'none', outline: 'none', background: 'transparent', fontFamily: serif, color: th.text }}
              />
              <button
                onClick={() => submit()}
                disabled={loading || !query_.trim()}
                style={{ padding: `0 ${isMobile ? '12px' : '18px'}`, border: 'none', borderLeft: `1px solid ${th.border}`, background: loading || !query_.trim() ? th.border : th.accent, color: dark ? '#000' : '#fff', cursor: loading || !query_.trim() ? 'not-allowed' : 'pointer', fontFamily: SANS, fontWeight: 700, fontSize: 12, letterSpacing: '0.04em', textTransform: 'uppercase', opacity: loading || !query_.trim() ? 0.6 : 1, transition: 'all 0.15s', display: 'flex', alignItems: 'center', gap: 7, flexShrink: 0 }}
              >
                {loading ? '…' : isMobile ? <ArrowIcon /> : t.search}
                {!loading && !isMobile && <ArrowIcon />}
              </button>
            </div>
            <div style={{ marginTop: 6, fontSize: 10, color: th.textFaint, paddingLeft: 1, fontFamily: SANS, letterSpacing: '0.02em' }}>{t.hint}</div>
          </div>
        </div>
      </div>

      {/* ── 5. Footer ── */}
      <div style={{ background: th.footerBg, borderTop: `1px solid ${th.border}`, padding: `16px ${px}`, transition: 'background 0.2s,border-color 0.2s' }}>
        <div style={{ maxWidth, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexDirection: isMobile ? 'column' : 'row', gap: isMobile ? 12 : 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <a href="https://www.nzz.ch" target="_blank" rel="noopener noreferrer"
              style={{ fontFamily: "'Times New Roman',Georgia,serif", fontWeight: 700, fontSize: 16, letterSpacing: '0.01em', color: th.textMid, textDecoration: 'none', transition: 'color 0.15s' }}
              onMouseEnter={e => e.currentTarget.style.color = th.text}
              onMouseLeave={e => e.currentTarget.style.color = th.textMid}
            >NZZ</a>
            <span style={{ color: th.textFaint, fontFamily: SANS, fontSize: 13 }}>|</span>
            <a href="https://www.hslu.ch" target="_blank" rel="noopener noreferrer"
              style={{ fontSize: 16, fontWeight: 900, color: th.textMid, fontFamily: SANS, letterSpacing: '0.02em', textDecoration: 'none', transition: 'color 0.15s' }}
              onMouseEnter={e => e.currentTarget.style.color = th.text}
              onMouseLeave={e => e.currentTarget.style.color = th.textMid}
            >HSLU</a>
          </div>
          <a href="https://github.com/DiggerFlo/DSPRO" target="_blank" rel="noopener noreferrer"
            style={{ fontSize: 11, color: th.textMuted, fontFamily: SANS, textDecoration: 'none', transition: 'color 0.15s' }}
            onMouseEnter={e => e.currentTarget.style.color = th.text}
            onMouseLeave={e => e.currentTarget.style.color = th.textMuted}
          >
            {t.footerProject} ↗
          </a>
        </div>
      </div>

      {/* ── Scroll to top ── */}
      {showScrollTop && (
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          className="fade-up"
          style={{ position: 'fixed', bottom: isMobile ? 90 : 100, right: isMobile ? 12 : 20, zIndex: 100, width: 40, height: 40, borderRadius: '50%', background: th.surface, border: `1px solid ${th.border}`, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: `0 2px 12px rgba(0,0,0,${dark ? 0.4 : 0.1})`, transition: 'all 0.15s' }}
          onMouseEnter={e => e.currentTarget.style.borderColor = th.text}
          onMouseLeave={e => e.currentTarget.style.borderColor = th.border}
          title="Nach oben"
        >
          <ChevronUpIcon color={th.textMid} />
        </button>
      )}

      {/* ── Settings modal ── */}
      {showSettings && (
        <div
          onClick={() => setShowSettings(false)}
          style={{ position: 'fixed', inset: 0, zIndex: 200, background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(3px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}
        >
          <div className="fade-up" onClick={e => e.stopPropagation()} style={{ background: th.surface, maxWidth: 420, width: '100%', boxShadow: '0 16px 48px rgba(0,0,0,0.28)', overflow: 'hidden' }}>
            <div style={{ background: '#111', padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: 12, fontWeight: 700, color: '#fff', fontFamily: SANS, letterSpacing: '0.08em', textTransform: 'uppercase' }}>{t.settingsTitle}</span>
              <button onClick={() => setShowSettings(false)} style={{ background: 'none', border: 'none', color: 'rgba(255,255,255,0.6)', cursor: 'pointer', fontSize: 18, lineHeight: 1 }}>×</button>
            </div>
            <div style={{ padding: '8px 20px 20px' }}>
              <ToggleRow
                label={t.settingsFollowUps}
                value={config.show_follow_ups}
                onChange={v => updateSetting('show_follow_ups', v)}
                th={th}
              />
              <ToggleRow
                label={t.settingsFullArticle}
                value={config.use_full_article}
                onChange={v => updateSetting('use_full_article', v)}
                th={th}
              />
              <ToggleRow
                label={t.settingsReranking}
                value={config.use_reranking}
                onChange={v => updateSetting('use_reranking', v)}
                disabled={!config.reranker_available}
                note={!config.reranker_available ? `(${t.settingsRerankerUnavailable})` : undefined}
                th={th}
              />
              <SliderRow
                label={t.settingsTopKRetrieval}
                value={config.top_k_retrieval}
                min={5} max={30} step={1}
                onChange={v => updateSetting('top_k_retrieval', v)}
                th={th}
              />
              <SliderRow
                label={t.settingsTopKFinal}
                value={config.top_k_final}
                min={1} max={10} step={1}
                onChange={v => updateSetting('top_k_final', v)}
                th={th}
              />
              <SliderRow
                label={t.settingsTemperature}
                value={config.llm_temperature}
                min={0} max={1} step={0.05}
                onChange={v => updateSetting('llm_temperature', v)}
                th={th}
              />
              <button
                onClick={() => setShowSettings(false)}
                style={{ marginTop: 16, width: '100%', padding: '10px', background: th.accent, color: dark ? '#000' : '#fff', border: 'none', fontSize: 12, fontWeight: 700, fontFamily: SANS, cursor: 'pointer', letterSpacing: '0.04em', textTransform: 'uppercase' }}
              >
                {t.settingsClose}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Welcome modal ── */}
      {showWelcome && (
        <div
          onClick={closeWelcome}
          className={welcomeClosing ? 'fade-out' : ''}
          style={{ position: 'fixed', inset: 0, zIndex: 200, background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(3px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}
        >
          <div className={welcomeClosing ? 'fade-out' : 'fade-up'} onClick={e => e.stopPropagation()} style={{ background: th.surface, maxWidth: 480, width: '100%', boxShadow: '0 16px 48px rgba(0,0,0,0.28)', overflow: 'hidden' }}>
            <div style={{ background: '#111', padding: '16px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ fontFamily: "'Times New Roman',Georgia,serif", fontWeight: 700, fontSize: 20, letterSpacing: '0.01em', color: '#fff' }}>NZZ</span>
                <span style={{ width: 1, height: 16, background: 'rgba(255,255,255,0.4)', display: 'block' }} />
                <span style={{ fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.9)', fontFamily: SANS, letterSpacing: '0.04em', textTransform: 'uppercase' }}>ContextAI</span>
              </div>
              <span style={{ fontSize: 9, fontWeight: 700, color: 'rgba(255,255,255,0.7)', fontFamily: SANS, letterSpacing: '0.1em', border: '1px solid rgba(255,255,255,0.4)', padding: '1px 6px' }}>HSLU · DSPRO1</span>
            </div>
            <div style={{ padding: '24px 24px 20px' }}>
              <h2 style={{ fontFamily: serif, fontSize: 20, fontWeight: 600, color: th.text, marginBottom: 12, lineHeight: 1.25, letterSpacing: '-0.01em' }}>{t.welcomeTitle}</h2>
              <p style={{ fontSize: 13, color: th.textMid, lineHeight: 1.75, marginBottom: 10, fontFamily: SANS }}>{t.welcomeP1}</p>
              <p style={{ fontSize: 13, color: th.textMid, lineHeight: 1.75, marginBottom: 18, fontFamily: SANS }}>{t.welcomeP2}</p>
              <div style={{ background: th.noteBg, border: `1px solid ${th.border}`, padding: '9px 12px', fontSize: 11, color: th.textMuted, marginBottom: 20, lineHeight: 1.6, fontFamily: SANS }}>{t.welcomeNote}</div>
              <button onClick={closeWelcome} style={{ width: '100%', padding: '11px', background: th.accent, color: dark ? '#000' : '#fff', border: 'none', fontSize: 13, fontWeight: 700, fontFamily: SANS, cursor: 'pointer', letterSpacing: '0.04em', textTransform: 'uppercase' }}>{t.welcomeBtn}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

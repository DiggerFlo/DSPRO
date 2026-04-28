import { useState } from 'react';

export default function SourceCard({ source, index, th, serif, relevanceLabel, dark, idPrefix }) {
  const [open, setOpen] = useState(false);
  const toggle = () => setOpen(o => !o);
  const handleKeyDown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } };

  return (
    <div
      id={`${idPrefix}-source-${source.id}`}
      className="fade-up"
      style={{ borderTop: `1px solid ${th.border}`, padding: '14px 0', animationDelay: `${index * 0.06}s` }}
    >
      <div
        role="button"
        tabIndex={0}
        aria-expanded={open}
        onClick={toggle}
        onKeyDown={handleKeyDown}
        onMouseEnter={e => e.currentTarget.style.opacity = '0.75'}
        onMouseLeave={e => e.currentTarget.style.opacity = '1'}
        style={{ cursor: 'pointer', display: 'grid', gridTemplateColumns: '22px 1fr 14px', gap: '0 10px', alignItems: 'start', transition: 'opacity 0.15s' }}
      >
        {/* Number badge */}
        <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: 22, height: 22, background: th.accent, color: dark ? '#000' : '#fff', fontSize: 10, fontWeight: 700, flexShrink: 0, marginTop: 2 }}>
          {source.id}
        </span>

        <div>
          {/* Title */}
          <div style={{ fontSize: 14, fontWeight: 600, color: th.text, lineHeight: 1.4, marginBottom: 5, fontFamily: serif }}>
            {source.title}
          </div>

          {/* Meta row: date · category · relevance bar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 11, color: th.textMuted, fontFamily: 'Inter,sans-serif' }}>
              {source.date}
            </span>
            {source.category && (
              <>
                <span style={{ fontSize: 11, color: th.textFaint }}>·</span>
                <span style={{ fontSize: 11, color: th.textMuted, fontFamily: 'Inter,sans-serif' }}>
                  {source.category}
                </span>
              </>
            )}
            {/* Relevance score from reranker */}
            <span style={{ fontSize: 11, color: th.textFaint }}>·</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ fontSize: 11, color: th.textMuted, fontFamily: 'Inter,sans-serif' }}>{relevanceLabel}:</span>
              <div style={{ width: 44, height: 2, background: th.borderLight, borderRadius: 1, overflow: 'hidden' }}>
                <div style={{ width: `${source.score}%`, height: '100%', background: th.accent }} />
              </div>
              <span style={{ fontSize: 11, fontWeight: 600, color: th.accent, fontFamily: 'Inter,sans-serif' }}>{source.score}%</span>
            </div>
          </div>

          {/* Expandable snippet */}
          {open && (
            <p className="slide-down" style={{ marginTop: 10, fontSize: 13, color: th.textMid, lineHeight: 1.7, fontFamily: 'Inter,sans-serif', borderLeft: `2px solid ${th.accent}`, paddingLeft: 10 }}>
              {source.snippet}
            </p>
          )}
        </div>

        <span style={{ color: th.textFaint, fontSize: 10, paddingTop: 5 }}>{open ? '▲' : '▼'}</span>
      </div>
    </div>
  );
}

export default function Cite({ num, accent, dark, idPrefix }) {
  const handleClick = () =>
    document.getElementById(`${idPrefix}-source-${num}`)?.scrollIntoView({ behavior: "smooth", block: "center" });

  return (
    <sup
      onClick={handleClick}
      title={`Zur Quelle ${num}`}
      style={{
        display: "inline-flex", alignItems: "center", justifyContent: "center",
        width: 16, height: 16, borderRadius: 2, background: accent,
        color: dark ? "#000" : "#fff", fontSize: 9, fontWeight: 700,
        fontFamily: "Inter,sans-serif", cursor: "pointer", verticalAlign: "super",
        margin: "0 1px", lineHeight: 1, userSelect: "none", transition: "opacity 0.1s",
      }}
      onMouseEnter={e => e.currentTarget.style.opacity = "0.75"}
      onMouseLeave={e => e.currentTarget.style.opacity = "1"}
    >
      {num}
    </sup>
  );
}

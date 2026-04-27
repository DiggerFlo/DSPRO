export default function LoadingDots({ color, label }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "28px 0" }}>
      {[1, 2, 3].map(i => (
        <span
          key={i}
          className={`dot${i}`}
          style={{ display: "inline-block", width: 5, height: 5, borderRadius: "50%", background: color }}
        />
      ))}
      <span style={{ fontSize: 12, color: "#999", fontFamily: "Inter,sans-serif", letterSpacing: "0.02em" }}>{label}</span>
    </div>
  );
}

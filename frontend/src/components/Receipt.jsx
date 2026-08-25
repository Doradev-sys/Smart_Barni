export default function Receipt({ lines, total, stamp = true, compact = false }) {
  return (
    <div className={`receipt ${compact ? 'receipt-compact' : ''}`}>
      <div className="receipt-logo">Barni</div>
      <div className="receipt-sub">Coffee · digital receipt</div>
      <hr />
      {lines.map((line, i) => (
        <div className="receipt-row" key={i}>
          <span>{line.label}</span>
          <b>{line.value}</b>
        </div>
      ))}
      <hr />
      <div className="receipt-total">
        <span>Total</span>
        <span>{total} birr</span>
      </div>
      {stamp && (
        <div className="stamp">
          PAID
          <br />
          BARNI
          <br />
          COFFEE
        </div>
      )}
    </div>
  )
}

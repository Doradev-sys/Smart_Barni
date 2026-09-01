import { useState } from 'react'
import { Panel, EmptyHint } from '../../components/ui'
import { useAppData } from '../../context/AppDataContext'
import { useToast } from '../../context/ToastContext'

export default function KitchenOrdersPage() {
  const { kitchenQueue, markKitchenDone } = useAppData()
  const { showToast } = useToast()
  const [expanded, setExpanded] = useState({})

  const toggle = (kitchenId) =>
    setExpanded((e) => ({ ...e, [kitchenId]: !e[kitchenId] }))

  const markReady = async (kitchenId) => {
    await markKitchenDone(kitchenId)
    showToast('Marked ready — waiter sees green card', 'success')
  }

  return (
    <div className="board single">
      <Panel title="Orders From Waiter">
        {kitchenQueue.length === 0 ? (
          <EmptyHint>No incoming orders</EmptyHint>
        ) : (
          <div className="kitchen-grid">
            {kitchenQueue.map((k) => {
              const rawIngredients = (k.ingredients || []).filter((i) => i.is_raw)
              const processedIngredients = (k.ingredients || []).filter((i) => !i.is_raw)
              const isOpen = !!expanded[k.kitchenId]
              return (
                <div
                  key={k.kitchenId}
                  className={`kitchen-card ${isOpen ? 'expanded' : ''}`}
                  onClick={() => toggle(k.kitchenId)}
                >
                  <div className="kitchen-top">
                    <span className="kitchen-name">{k.name}</span>
                    <span className="kitchen-id">{k.orderId}</span>
                  </div>
                  <div className="kitchen-meta">
                    Qty <span className="qty-box">×{k.qty}</span> · {k.side}
                    {k.source === 'online' && (
                      <span className="badge online" style={{ marginLeft: 6 }}>
                        Online
                      </span>
                    )}
                  </div>
                  <div className="kitchen-ingredients">
                    <div>
                      <div className="ing-col-title">Raw</div>
                      {rawIngredients.length
                        ? rawIngredients.map((i) => (
                            <div className="ing-row" key={i.name}>
                              {i.name} — {i.quantity}
                            </div>
                          ))
                        : <div className="ing-row">—</div>}
                    </div>
                    <div>
                      <div className="ing-col-title">Processed</div>
                      {processedIngredients.length
                        ? processedIngredients.map((i) => (
                            <div className="ing-row" key={i.name}>
                              {i.name} — {i.quantity}
                            </div>
                          ))
                        : <div className="ing-row">—</div>}
                    </div>
                  </div>
                  <button
                    className="done-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      markReady(k.kitchenId)
                    }}
                  >
                    Ready
                  </button>
                </div>
              )
            })}
          </div>
        )}
      </Panel>
    </div>
  )
}

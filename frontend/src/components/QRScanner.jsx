import { useState, useEffect, useRef, useCallback } from 'react'
import { Html5Qrcode } from 'html5-qrcode'

export default function QRScanner({ open, onClose, onScan }) {
  const [size, setSize] = useState(250)
  const [brightness, setBrightness] = useState(100)
  const [scanned, setScanned] = useState(null)
  const [error, setError] = useState('')
  const [starting, setStarting] = useState(false)
  const scannerRef = useRef(null)
  const containerRef = useRef(null)

  const stopScanner = useCallback(async () => {
    if (scannerRef.current) {
      try {
        await scannerRef.current.stop()
      } catch {}
      try {
        scannerRef.current.clear()
      } catch {}
      scannerRef.current = null
    }
  }, [])

  const startScanner = useCallback(async () => {
    if (!open || !containerRef.current) return
    setStarting(true)
    setError('')
    setScanned(null)
    await stopScanner()

    try {
      const scanner = new Html5Qrcode('qr-reader-region')
      scannerRef.current = scanner
      await scanner.start(
        { facingMode: 'environment' },
        {
          fps: 10,
          qrbox: { width: Math.min(size, 300), height: Math.min(size, 300) },
          aspectRatio: 1.0,
        },
        (decodedText) => {
          setScanned(decodedText)
          stopScanner()
        },
        () => {}
      )
    } catch (err) {
      setError('Camera access denied or unavailable. You can still enter data manually.')
    }
    setStarting(false)
  }, [open, size, stopScanner])

  useEffect(() => {
    if (open) {
      setTimeout(() => startScanner(), 200)
    } else {
      stopScanner()
    }
    return () => stopScanner()
  }, [open, startScanner, stopScanner])

  if (!open) return null

  return (
    <div className="qr-scanner-overlay">
      <div className="qr-scanner-modal">
        <div className="qr-scanner-header">
          <div className="qr-scanner-title">SCAN QR CODE</div>
          <button className="qr-scanner-close" onClick={() => { stopScanner(); onClose() }}>✕</button>
        </div>

        <div
          className="qr-scanner-viewport"
          style={{ filter: `brightness(${brightness}%)` }}
          ref={containerRef}
        >
          <div id="qr-reader-region" style={{ width: size, height: size }} />
          <div className="qr-scan-frame" style={{ width: size, height: size }}>
            <div className="qr-corner tl" />
            <div className="qr-corner tr" />
            <div className="qr-corner bl" />
            <div className="qr-corner br" />
          </div>
        </div>

        {starting && <div className="qr-scanner-status">Starting camera...</div>}
        {error && <div className="qr-scanner-error">{error}</div>}

        <div className="qr-controls">
          <div className="qr-control-row">
            <label className="qr-label">Size: {size}px</label>
            <input
              type="range"
              min="150"
              max="400"
              step="10"
              value={size}
              onChange={(e) => setSize(Number(e.target.value))}
              className="qr-slider"
            />
          </div>
          <div className="qr-control-row">
            <label className="qr-label">Brightness: {brightness}%</label>
            <input
              type="range"
              min="30"
              max="200"
              step="5"
              value={brightness}
              onChange={(e) => setBrightness(Number(e.target.value))}
              className="qr-slider"
            />
          </div>
        </div>

        {scanned && (
          <div className="qr-scanned-result">
            <div className="qr-scanned-label">Scanned:</div>
            <div className="qr-scanned-data">{scanned}</div>
            <div className="qr-scanned-actions">
              <button className="modal-primary-btn" onClick={() => { onScan(scanned); stopScanner(); onClose() }}>
                Use This Data
              </button>
              <button className="qr-scan-again" onClick={() => { setScanned(null); startScanner() }}>
                Scan Again
              </button>
            </div>
          </div>
        )}

        {!scanned && !error && (
          <div className="qr-scanner-hint">Point camera at a QR code</div>
        )}

        {error && (
          <div className="qr-manual-entry">
            <label className="field-label">Enter QR data manually</label>
            <input
              className="auth-input"
              placeholder="Paste or type QR content"
              id="qr-manual-input"
            />
            <button
              className="modal-primary-btn"
              onClick={() => {
                const val = document.getElementById('qr-manual-input')?.value
                if (val) { onScan(val); onClose() }
              }}
            >
              Submit
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

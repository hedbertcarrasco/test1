import React from 'react'

export default function App({ initialState }) {
  const status = initialState.status || 'unknown'
  const message = initialState.message || 'Loading...'

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif', padding: 24 }}>
      <h1>React + FastAPI on OpenShift</h1>
      <p><strong>API status:</strong> {status}</p>
      <p><strong>Message:</strong> {message}</p>
      <p style={{ marginTop: 16, fontSize: 12, opacity: 0.8 }}>
        Backend URL: <code>(BFF same-origin; no client API calls)</code>
      </p>
    </div>
  )
}

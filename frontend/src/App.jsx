import React, { useEffect, useState } from 'react'

const apiUrl = import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`

export default function App() {
  const [message, setMessage] = useState('Loading...')
  const [status, setStatus] = useState('unknown')

  useEffect(() => {
    async function load() {
      try {
        const healthRes = await fetch(`${apiUrl}/api/health`)
        const healthJson = await healthRes.json()
        setStatus(healthJson.status)

        const res = await fetch(`${apiUrl}/api/message`)
        const json = await res.json()
        setMessage(json.message)
      } catch (err) {
        setMessage('Failed to reach API')
        setStatus('error')
      }
    }
    load()
  }, [])

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif', padding: 24 }}>
      <h1>React + FastAPI on OpenShift</h1>
      <p><strong>API status:</strong> {status}</p>
      <p><strong>Message:</strong> {message}</p>
      <p style={{ marginTop: 16, fontSize: 12, opacity: 0.8 }}>
        Backend URL: <code>{apiUrl}</code>
      </p>
    </div>
  )
}

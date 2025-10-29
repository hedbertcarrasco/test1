import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

const initialState = (window.__INITIAL_STATE__ || {})

const root = createRoot(document.getElementById('root'))
root.render(<App initialState={initialState} />)

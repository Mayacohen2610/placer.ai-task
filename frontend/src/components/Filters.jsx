import React, { useEffect, useState, useRef } from 'react'

// Small multi-select with autocomplete using backend /api/distinct/{field}?q=...
function MultiSelect({ field, values, setValues, placeholder, multiEnabled }) {
  const [input, setInput] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [open, setOpen] = useState(false)
  const ref = useRef()

  useEffect(() => {
    if (!input) {
      setSuggestions([])
      return
    }
    let cancelled = false
    fetch(`/api/distinct/${field}?q=${encodeURIComponent(input)}`)
      .then(r => r.json())
      .then(data => { if (!cancelled) setSuggestions(data || []) })
      .catch(() => { if (!cancelled) setSuggestions([]) })
    return () => { cancelled = true }
  }, [input, field])

  // click outside to close
  useEffect(() => {
    function onDoc(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('click', onDoc)
    return () => document.removeEventListener('click', onDoc)
  }, [])

  function addValue(v) {
    if (!v) return
    if (!values.includes(v)) setValues([...values, v])
    setInput('')
    setSuggestions([])
    setOpen(false)
  }

  function removeValue(v) {
    setValues(values.filter(x => x !== v))
  }

  return (
    <div ref={ref} style={{ minWidth: 220 }}>
      <div style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>{placeholder}</div>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap', border: '1px solid #ddd', padding: 6, borderRadius: 6 }}>
        {values.map(v => (
          <div key={v} style={{ background: '#eee', padding: '4px 8px', borderRadius: 12, display: 'flex', gap: 6, alignItems: 'center' }}>
            <span style={{ fontSize: 13 }}>{v}</span>
            <button onClick={() => removeValue(v)} style={{ border: 'none', background: 'transparent', cursor: 'pointer' }}>✕</button>
          </div>
        ))}

        <input
          value={input}
          onChange={e => { setInput(e.target.value); setOpen(true) }}
          onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addValue(input.trim()) } }}
          placeholder="Type to search"
          style={{ border: 'none', outline: 'none', minWidth: 80 }}
          onFocus={() => setOpen(true)}
        />
      </div>

        {open && suggestions && suggestions.length > 0 && (
          <div style={{ border: '1px solid #ddd', borderRadius: 6, marginTop: 6, maxHeight: 200, overflow: 'auto', background: '#fff', zIndex: 50 }}>
            {suggestions.map(s => (
              <div key={s} onClick={() => {
                  if (multiEnabled) addValue(s)
                  else { setValues([s]); setOpen(false); setInput('') }
                }} style={{ padding: '6px 10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
                {multiEnabled ? <input type="checkbox" readOnly checked={values.includes(s)} /> : null}
                <span>{s}</span>
              </div>
            ))}
          </div>
        )}
    </div>
  )
}

// Filters component now exposes multi-selects for chain, category and dma plus open-only checkbox
export default function Filters({ chains, setChains, categories, setCategories, dmas, setDmas, openOnly, setOpenOnly, multiEnabled, setMultiEnabled }) {
  return (
    <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', border: '1px solid #eee', borderRadius: 12, padding: 12, flexWrap: 'wrap' }}>
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <label style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>
          <input type="checkbox" checked={multiEnabled} onChange={e => setMultiEnabled(e.target.checked)} />{' '}
          Multi-select enabled
        </label>
      </div>

      <MultiSelect field="chain" values={chains} setValues={setChains} placeholder="Chain" multiEnabled={multiEnabled} />
      <MultiSelect field="category" values={categories} setValues={setCategories} placeholder="Category" multiEnabled={multiEnabled} />
      <MultiSelect field="dma" values={dmas} setValues={setDmas} placeholder="DMA" multiEnabled={multiEnabled} />

      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <label style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>
          <input type="checkbox" checked={openOnly} onChange={e => setOpenOnly(e.target.checked)} />{' '}
          Show open only
        </label>
      </div>
    </div>
  )
}
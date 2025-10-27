import React from 'react'

export default function Filters({ pois, poi, setPoi, dateFrom, setDateFrom, dateTo, setDateTo }) {
  return (
    <div style={{ display: 'flex', gap: 12, alignItems: 'center', border: '1px solid #eee', borderRadius: 12, padding: 12 }}>
      <div>
        <div style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>POI</div>
        <select value={poi} onChange={e => setPoi(e.target.value)}>
          <option>All</option>
          {pois.map(p => <option key={p}>{p}</option>)}
        </select>
      </div>
      <div>
        <div style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>From</div>
        <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
      </div>
      <div>
        <div style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>To</div>
        <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} />
      </div>
    </div>
  )
}
import React from 'react'
// Filters component for selecting POI and date range.
// Purpose: provides dropdown and date inputs to filter visit data displayed in the dashboard.
// Interaction: calls setPoi, setDateFrom, and setDateTo callbacks to update parent component state.
// To modify: add more filter options or change styling as needed.

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

// exaple of add more filter - uncomment to use
/*
      <div>
        <div style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>DMA</div>
        <select value={dma} onChange={e => setDma(e.target.value)}>
          <option>All</option>
          {dmas.map(d => <option key={d}>{d}</option>)}
        </select>
      </div>  
*/      
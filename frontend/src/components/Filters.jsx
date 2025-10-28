import React from 'react'

// Minimal Filters component required by the task.
// Exposes three text filters (chain_name, dma, category) and a checkbox to show only open POIs.
export default function Filters({ chain, setChain, category, setCategory, dma, setDma, openOnly, setOpenOnly }) {
  return (
    <div style={{ display: 'flex', gap: 12, alignItems: 'center', border: '1px solid #eee', borderRadius: 12, padding: 12, flexWrap: 'wrap' }}>
      <div>
        <div style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>Chain</div>
        <input placeholder="All or chain name" value={chain} onChange={e => setChain(e.target.value)} />
      </div>

      <div>
        <div style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>Category</div>
        <input placeholder="All or category" value={category} onChange={e => setCategory(e.target.value)} />
      </div>

      <div>
        <div style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>DMA</div>
        <input placeholder="All or DMA" value={dma} onChange={e => setDma(e.target.value)} />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <label style={{ fontSize: 12, color: '#666', marginBottom: 6 }}>
          <input type="checkbox" checked={openOnly} onChange={e => setOpenOnly(e.target.checked)} />{' '}
          Show open only
        </label>
      </div>
    </div>
  )
}
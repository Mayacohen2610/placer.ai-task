import React, { useEffect, useState } from 'react'
import Filters from './components/Filters.jsx'

// Single-table POI dashboard with server-side pagination and three filters.
export default function App() {
  const [chain, setChain] = useState('')
  const [category, setCategory] = useState('')
  const [dma, setDma] = useState('')
  const [openOnly, setOpenOnly] = useState(false)

  const [items, setItems] = useState([])
  const [page, setPage] = useState(1)
  const [perPage, setPerPage] = useState(25)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function load() {
      setLoading(true)
      const q = new URLSearchParams()
      q.append('page', String(page))
      q.append('per_page', String(perPage))
      if (chain && chain.trim() !== '') q.append('chain', chain.trim())
      if (category && category.trim() !== '') q.append('category', category.trim())
      if (dma && dma.trim() !== '') q.append('dma', dma.trim())
      if (openOnly) q.append('open_status', 'open')
      const suffix = q.toString() ? `?${q.toString()}` : ''
      try {
        const res = await fetch(`/api/venues${suffix}`)
        const data = await res.json()
        setItems(data.items || [])
        setTotal(data.total || 0)
      } catch (e) {
        setItems([])
        setTotal(0)
      }
      setLoading(false)
    }
    load()
  }, [chain, category, dma, openOnly, page, perPage])

  // reset to page 1 when filters change
  useEffect(() => setPage(1), [chain, category, dma, openOnly, perPage])

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: 16, fontFamily: 'system-ui, Arial' }}>
      <h1 style={{ marginBottom: 8 }}>POI Table</h1>

      <Filters
        chain={chain}
        setChain={setChain}
        category={category}
        setCategory={setCategory}
        dma={dma}
        setDma={setDma}
        openOnly={openOnly}
        setOpenOnly={setOpenOnly}
      />

      <div style={{ marginTop: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <div>{loading ? 'Loading…' : `${total} venues`}</div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <label style={{ fontSize: 13 }}>Per page:
              <select value={perPage} onChange={e => setPerPage(Number(e.target.value))} style={{ marginLeft: 8 }}>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </label>
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1}>Prev</button>
            <div style={{ minWidth: 80, textAlign: 'center' }}>Page {page}</div>
            <button onClick={() => setPage(p => p + 1)} disabled={page * perPage >= total}>Next</button>
          </div>
        </div>

        <div style={{ border: '1px solid #eee', borderRadius: 8, overflow: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <Th>Name</Th><Th>Chain</Th><Th>Category</Th><Th>DMA</Th><Th>City</Th><Th>State</Th><Th>Visits</Th><Th>Is Open</Th>
              </tr>
            </thead>
            <tbody>
              {items.map((r) => (
                <tr key={r.id} style={{ borderTop: '1px solid #f0f0f0' }}>
                  <Td>{r.name}</Td>
                  <Td>{r.chain_name}</Td>
                  <Td>{r.category}</Td>
                  <Td>{r.dma}</Td>
                  <Td>{r.city}</Td>
                  <Td>{r.state}</Td>
                  <Td>{r.foot_traffic}</Td>
                  <Td>{r.date_closed ? 'No' : 'Yes'}</Td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function Th({ children }) {
  return <th style={{ textAlign: 'left', padding: '8px 10px', fontWeight: 600, fontSize: 13, background: '#fafafa', borderBottom: '1px solid #eee' }}>{children}</th>
}
function Td({ children }) {
  return <td style={{ padding: '8px 10px', fontSize: 13 }}>{children}</td>
}
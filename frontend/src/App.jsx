import React, { useEffect, useState } from 'react'
import Filters from './components/Filters.jsx'

// Single-table POI dashboard with server-side pagination and three filters.
export default function App() {
  const [chain, setChain] = useState([])
  const [category, setCategory] = useState([])
  const [dma, setDma] = useState([])
  const [openOnly, setOpenOnly] = useState(false)
  const [multiEnabled, setMultiEnabled] = useState(true)

  const [items, setItems] = useState([])
  const [summary, setSummary] = useState({ venues: 0, total_foot_traffic: 0 })
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
  // append multiple values for chain/category/dma
  if (Array.isArray(chain) && chain.length > 0) chain.forEach(c => q.append('chain', c))
  if (Array.isArray(category) && category.length > 0) category.forEach(c => q.append('category', c))
  if (Array.isArray(dma) && dma.length > 0) dma.forEach(d => q.append('dma', d))
      if (openOnly) q.append('open_status', 'open')
      const suffix = q.toString() ? `?${q.toString()}` : ''
      try {
        const [resV, resS] = await Promise.all([
          fetch(`/api/venues${suffix}`),
          fetch(`/api/venues/summary${suffix}`),
        ])
        const dataV = await resV.json()
        const dataS = await resS.json()
        setItems(dataV.items || [])
        setTotal(dataV.total || 0)
        setSummary({ venues: dataS.venues || 0, total_foot_traffic: dataS.total_foot_traffic || 0 })
      } catch (e) {
        setItems([])
        setTotal(0)
        setSummary({ venues: 0, total_foot_traffic: 0 })
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
        chains={chain}
        setChains={setChain}
        categories={category}
        setCategories={setCategory}
        dmas={dma}
        setDmas={setDma}
        openOnly={openOnly}
        setOpenOnly={setOpenOnly}
        multiEnabled={multiEnabled}
        setMultiEnabled={setMultiEnabled}
      />

      <div style={{ marginTop: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <div style={{ display: 'flex', gap: 12 }}>
            <KpiCard title="Venues" value={loading ? '…' : summary.venues} />
            <KpiCard title="Total Foot Traffic" value={loading ? '…' : summary.total_foot_traffic} />
          </div>
          <div>{loading ? 'Loading…' : `${total} venues`}</div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <label style={{ fontSize: 13 }}>Per page:
              <select value={perPage} onChange={e => setPerPage(Number(e.target.value))} style={{ marginLeft: 8 }}>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </label>
            <button onClick={async () => {
              // build query suffix like the load effect
              const q = new URLSearchParams()
              if (Array.isArray(chain) && chain.length > 0) chain.forEach(c => q.append('chain', c))
              if (Array.isArray(category) && category.length > 0) category.forEach(c => q.append('category', c))
              if (Array.isArray(dma) && dma.length > 0) dma.forEach(d => q.append('dma', d))
              if (openOnly) q.append('open_status', 'open')
              const suffix = q.toString() ? `?${q.toString()}` : ''
              try {
                const res = await fetch(`/api/venues/export${suffix}`)
                if (!res.ok) throw new Error('Export failed')
                const blob = await res.blob()
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = 'venues.csv'
                document.body.appendChild(a)
                a.click()
                a.remove()
                window.URL.revokeObjectURL(url)
              } catch (e) {
                console.error('Export error', e)
                alert('Export failed')
              }
            }} style={{ marginLeft: 8 }}>Export CSV</button>
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

function KpiCard({ title, value }) {
  return (
    <div style={{ border: '1px solid #eee', borderRadius: 10, padding: 8, minWidth: 160 }}>
      <div style={{ fontSize: 12, color: '#666' }}>{title}</div>
      <div style={{ fontSize: 20, fontWeight: 700 }}>{value}</div>
    </div>
  )
}
import React, { useEffect, useMemo, useState } from 'react'
import Filters from './components/Filters.jsx'
import VisitsChart from './components/VisitsChart.jsx'

export default function App() {
  const [pois, setPois] = useState([])
  const [poi, setPoi] = useState('All')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [summary, setSummary] = useState({ rows: 0, total_visitors: 0, avg_visitors: 0, avg_dwell: 0 })
  const [rows, setRows] = useState([])

  useEffect(() => {
    fetch('/api/pois').then(r => r.json()).then(setPois).catch(()=>setPois([]))
  }, [])

  useEffect(() => {
    const q = new URLSearchParams()
    if (poi && poi !== 'All') q.append('poi', poi)
    if (dateFrom) q.append('date_from', dateFrom)
    if (dateTo) q.append('date_to', dateTo)
    const suffix = q.toString() ? `?${q.toString()}` : ''
    fetch(`/api/summary${suffix}`).then(r => r.json()).then(setSummary)
    fetch(`/api/visits${suffix}`).then(r => r.json()).then(setRows)
  }, [poi, dateFrom, dateTo])

  const chartData = useMemo(() => rows.map(r => ({ date: r.date, visitors: r.visitors })), [rows])

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: 16, fontFamily: 'system-ui, Arial' }}>
      <h1 style={{ marginBottom: 8 }}>Foot Traffic Dashboard</h1>
      <p style={{ color: '#555', marginTop: 0 }}>POIs, visits, and simple KPIs</p>

      <Filters
        pois={pois}
        poi={poi}
        setPoi={setPoi}
        dateFrom={dateFrom}
        setDateFrom={setDateFrom}
        dateTo={dateTo}
        setDateTo={setDateTo}
      />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginTop: 12 }}>
        <KpiCard title="Rows" value={summary.rows} />
        <KpiCard title="Total Visitors" value={summary.total_visitors} />
        <KpiCard title="Avg Visitors" value={summary.avg_visitors} />
        <KpiCard title="Avg Dwell (min)" value={summary.avg_dwell} />
      </div>

      <div style={{ marginTop: 24, padding: 12, border: '1px solid #eee', borderRadius: 8 }}>
        <h3 style={{ marginTop: 0 }}>Daily Visits</h3>
        <VisitsChart data={chartData} />
      </div>

      <div style={{ marginTop: 24 }}>
        <h3>Raw rows</h3>
        <div style={{ maxHeight: 240, overflow: 'auto', border: '1px solid #eee', borderRadius: 8 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <Th>POI</Th><Th>Date</Th><Th>Visitors</Th><Th>CBG</Th><Th>DMA</Th><Th>Dwell</Th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} style={{ borderTop: '1px solid #f0f0f0' }}>
                  <Td>{r.poi}</Td><Td>{r.date}</Td><Td>{r.visitors}</Td><Td>{r.cbg}</Td><Td>{r.dma}</Td><Td>{r.dwell}</Td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function KpiCard({ title, value }) {
  return (
    <div style={{ border: '1px solid #eee', borderRadius: 12, padding: 12 }}>
      <div style={{ fontSize: 12, color: '#666' }}>{title}</div>
      <div style={{ fontSize: 24, fontWeight: 700 }}>{value}</div>
    </div>
  )
}

function Th({ children }) {
  return <th style={{ textAlign: 'left', padding: '8px 10px', fontWeight: 600, fontSize: 13, background: '#fafafa', borderBottom: '1px solid #eee' }}>{children}</th>
}
function Td({ children }) {
  return <td style={{ padding: '8px 10px', fontSize: 13 }}>{children}</td>
}
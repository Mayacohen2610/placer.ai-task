import React from 'react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'


// VisitsChart component to display a bar chart of visits over time.
// Purpose: visualizes the number of visitors per date using a bar chart.
// Interaction: receives 'data' prop containing date and visitors count to render the chart.
// To modify: change chart type, add more data series, or adjust styling as needed.
export default function VisitsChart({ data }) {
  return (
    <div style={{ width: '100%', height: 320 }}>
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="visitors" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
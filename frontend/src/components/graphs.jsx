import React from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Line,
} from 'recharts'

/**
 * flexible chart for metrics.
 *
 * Renders a bar or line chart for provided data. Expects pre-aggregated input
 * (e.g. [{ chain: 'Walmart', foot_traffic: 1234 }, ...]).
 *
 * Props: data, xKey ('date'), valueKey ('visitors'), chartType ('bar'|'line'),
 * height, barColor/lineColor, xLabel, yLabel, tooltipFormatter.
 */
export default function VisitsChart({
  data = [],
  xKey = 'date',
  valueKey = 'visitors',
  chartType = 'bar',
  height = 320,
  barColor = '#8884d8',
  lineColor = '#8884d8',
  xLabel,
  yLabel,
  tooltipFormatter,
}) {
  // show a small placeholder when no data is provided — keeps UI stable
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <div style={{ width: '100%', height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#666' }}>
        No data to display
      </div>
    )
  }

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey={xKey}
            label={xLabel ? { value: xLabel, position: 'insideBottom', offset: -5 } : undefined}
          />
          <YAxis label={yLabel ? { value: yLabel, angle: -90, position: 'insideLeft' } : undefined} />
          <Tooltip formatter={tooltipFormatter} />
          {chartType === 'bar' ? (
            <Bar dataKey={valueKey} fill={barColor} />
          ) : (
            <Line type="monotone" dataKey={valueKey} stroke={lineColor} dot={false} />
          )}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
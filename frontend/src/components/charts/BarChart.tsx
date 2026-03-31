import {
  BarChart as ReBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

interface DataPoint {
  label: string
  value: number
}

interface Props {
  data: DataPoint[]
  color?: string
  horizontal?: boolean
}

export function BarChartComponent({ data, color = '#6366f1', horizontal = false }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ReBarChart
        data={data}
        layout={horizontal ? 'vertical' : 'horizontal'}
        margin={{ top: 4, right: 16, left: horizontal ? 80 : 0, bottom: horizontal ? 4 : 40 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        {horizontal ? (
          <>
            <XAxis type="number" tick={{ fontSize: 11 }} />
            <YAxis dataKey="label" type="category" tick={{ fontSize: 11 }} width={80} />
          </>
        ) : (
          <>
            <XAxis dataKey="label" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 11 }} />
          </>
        )}
        <Tooltip />
        <Bar dataKey="value" fill={color} radius={[2, 2, 0, 0]} />
      </ReBarChart>
    </ResponsiveContainer>
  )
}

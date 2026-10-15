import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'

const COLORS = [
  '#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
]

interface CategoryChartProps {
  data: { labels: string[]; values: number[] }
  className?: string
}

export const CategoryChart = ({ data, className }: CategoryChartProps) => {
  const chartData = data.labels.map((label, index) => ({
    name: label,
    value: data.values[index],
    color: COLORS[index % COLORS.length],
  }))

  const total = data.values.reduce((a, b) => a + b, 0)

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Books by Category</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid h-64 grid-cols-[minmax(0,1fr)_minmax(0,1fr)] items-center gap-3 sm:gap-4">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={48}
                outerRadius={68}
                paddingAngle={2}
                dataKey="value"
                nameKey="name"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                }}
                formatter={(value: number) => [value, 'books']}
              />
            </PieChart>
          </ResponsiveContainer>
          <ul className="min-w-0 space-y-2 text-sm" aria-label="Book counts by category">
            {chartData.map((entry) => (
              <li key={entry.name} className="flex min-w-0 items-start gap-2">
                <span
                  className="mt-1.5 h-2.5 w-2.5 flex-shrink-0 rounded-full"
                  style={{ backgroundColor: entry.color }}
                  aria-hidden="true"
                />
                <span className="min-w-0 flex-1 break-words [overflow-wrap:anywhere]">
                  {entry.name}
                </span>
                <span className="flex-shrink-0 text-muted-foreground">
                  {total ? `${((entry.value / total) * 100).toFixed(1)}%` : '0%'}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}
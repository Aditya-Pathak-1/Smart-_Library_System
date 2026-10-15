import React from 'react'
import { cn } from '../../lib/utils'
import { Card, CardContent } from '../ui/Card'
import { formatCurrency } from '../../lib/utils'

interface StatCardProps {
  title: string
  value: number | string
  icon: React.ReactNode
  trend?: { value: number; label: string }
  className?: string
  color?: 'primary' | 'success' | 'warning' | 'info' | 'destructive'
}

const colorClasses = {
  primary: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
  success: 'bg-green-500/10 text-green-600 dark:text-green-400',
  warning: 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400',
  info: 'bg-purple-500/10 text-purple-600 dark:text-purple-400',
  destructive: 'bg-red-500/10 text-red-600 dark:text-red-400',
}

export const StatCard = ({ title, value, icon, trend, className, color = 'primary' }: StatCardProps) => {
  return (
    <Card className={cn('overflow-hidden', className)}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold tracking-tight mt-1">
              {typeof value === 'number' && value >= 10000 ? 
                (value >= 1000000 ? (value / 1000000).toFixed(1) + 'M' : (value / 1000).toFixed(1) + 'K') : 
                value}
            </p>
            {trend && (
              <p className={cn('text-xs mt-1', trend.value >= 0 ? 'text-green-600' : 'text-red-600')}>
                {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
              </p>
            )}
          </div>
          <div className={cn('p-3 rounded-xl', colorClasses[color])}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
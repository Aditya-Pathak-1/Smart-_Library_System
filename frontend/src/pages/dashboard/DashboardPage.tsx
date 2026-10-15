import React, { useEffect, useState } from 'react'
import { BookOpen, Users, Book, User, AlertTriangle, TrendingUp, DollarSign, Clock, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Card, CardContent } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Skeleton } from '../../components/ui/Skeleton'
import { StatCard, IssueReturnChart, CategoryChart } from '../../components/charts'
import { reportsApi } from '../../services/api'
import { formatCurrency } from '../../lib/utils'
import type { DashboardStats, RecentActivityItem, OverdueBookItem } from '../../types'

const statCards = [
  { title: 'Total Books', icon: BookOpen, color: 'primary' as const, key: 'total_books' },
  { title: 'Available Books', icon: Book, color: 'success' as const, key: 'available_books' },
  { title: 'Issued Books', icon: Book, color: 'info' as const, key: 'issued_books' },
  { title: 'Total Members', icon: Users, color: 'primary' as const, key: 'total_members' },
  { title: 'Active Members', icon: Users, color: 'success' as const, key: 'active_members' },
  { title: 'Overdue Books', icon: AlertTriangle, color: 'destructive' as const, key: 'overdue_books' },
  { title: 'Outstanding Fines', icon: DollarSign, color: 'warning' as const, key: 'total_outstanding_fines', isCurrency: true },
  { title: 'Fines Collected', icon: DollarSign, color: 'success' as const, key: 'total_fines_collected', isCurrency: true },
]

export const DashboardPage = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [issueReturnChart, setIssueReturnChart] = useState<{ labels: string[]; issues: number[]; returns: number[] } | null>(null)
  const [categoryChart, setCategoryChart] = useState<{ labels: string[]; values: number[] } | null>(null)
  const [recentActivity, setRecentActivity] = useState<RecentActivityItem[]>([])
  const [overdueBooks, setOverdueBooks] = useState<OverdueBookItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = async () => {
    try {
      setLoading(true)
      const [statsRes, chartRes, categoryRes, activityRes, overdueRes] = await Promise.all([
        reportsApi.dashboardStats(),
        reportsApi.issueReturnChart(30),
        reportsApi.categoryChart(),
        reportsApi.recentActivity(10),
        reportsApi.overdueBooks(10),
      ])
      setStats(statsRes.data)
      setIssueReturnChart(chartRes.data)
      setCategoryChart(categoryRes.data)
      setRecentActivity(activityRes.data)
      setOverdueBooks(overdueRes.data)
    } catch (err) {
      setError('Failed to load dashboard data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">Overview of your library system</p>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {statCards.map(() => (
            <Card key={Math.random()}><CardContent className="p-6"><Skeleton className="h-8 w-32" /><Skeleton className="h-12 w-24 mt-2" /></CardContent></Card>
          ))}
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <Card><CardContent className="p-6"><Skeleton className="h-64 w-full" /></CardContent></Card>
          <Card><CardContent className="p-6"><Skeleton className="h-64 w-full" /></CardContent></Card>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Overview of your library system</p>
        </div>
        <Button variant="outline" onClick={fetchData} loading={loading}>
          Refresh
        </Button>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive text-sm">
          {error}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => {
          const value = stats?.[stat.key as keyof DashboardStats] ?? 0
          return (
            <StatCard
              key={stat.key}
              title={stat.title}
              value={stat.isCurrency ? formatCurrency(value as number) : value}
              icon={<stat.icon className="h-6 w-6" />}
              color={stat.color}
            />
          )
        })}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {issueReturnChart && <IssueReturnChart data={issueReturnChart} />}
        {categoryChart && <CategoryChart data={categoryChart} />}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
            {recentActivity.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">No recent activity</p>
            ) : (
              <div className="space-y-3">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3 p-3 hover:bg-muted/50 rounded-lg transition-colors">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      {activity.type === 'issue' && <ArrowUpRight className="h-5 w-5 text-primary" />}
                      {activity.type === 'return' && <ArrowDownRight className="h-5 w-5 text-green-600" />}
                      {activity.type === 'registration' && <User className="h-5 w-5 text-blue-600" />}
                      {activity.type === 'payment' && <DollarSign className="h-5 w-5 text-green-600" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{activity.description}</p>
                      <p className="text-xs text-muted-foreground">
                        {activity.user_name ? `by ${activity.user_name} • ` : ''}
                        {new Date(activity.date).toLocaleString()}
                      </p>
                    </div>
                    <Badge variant="outline" className="text-xs capitalize">{activity.type}</Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">Overdue / Due Soon</h3>
            {overdueBooks.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">No overdue books</p>
            ) : (
              <div className="space-y-3">
                {overdueBooks.map((book) => (
                  <div key={book.transaction_id} className="flex items-start justify-between gap-3 p-3 hover:bg-muted/50 rounded-lg transition-colors">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{book.book_title}</p>
                      <p className="text-xs text-muted-foreground">{book.member_name} ({book.member_id})</p>
                      <p className="text-xs text-muted-foreground">Due: {new Date(book.due_date).toLocaleDateString()}</p>
                    </div>
                    <div className="flex flex-col items-end gap-1">
                      <Badge variant={book.overdue_days > 0 ? 'destructive' : 'warning'}>
                        {book.overdue_days > 0 ? `${book.overdue_days} days overdue` : 'Due soon'}
                      </Badge>
                      <span className="text-sm font-medium text-destructive">
                        {formatCurrency(book.estimated_fine)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
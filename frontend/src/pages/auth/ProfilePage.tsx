import React, { useEffect, useState } from 'react'
import { BookOpen, DollarSign, AlertTriangle, Calendar, Mail, Phone, MapPin, Shield, User, Edit } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../components/ui/Tabs'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/Table'
import { membersApi, issuesApi, finesApi } from '../../services/api'
import { useAuth } from '../../contexts/AuthContext'
import type { Member, IssueTransaction, Fine } from '../../types'
import { formatDate, formatCurrency } from '../../lib/utils'

const statusColors = {
  active: 'success',
  inactive: 'secondary',
  suspended: 'destructive',
  expired: 'warning',
} as const

const issueStatusColors = {
  issued: 'info',
  returned: 'success',
  overdue: 'destructive',
  lost: 'secondary',
} as const

const fineStatusColors = {
  pending: 'warning',
  partial: 'info',
  paid: 'success',
  waived: 'secondary',
} as const

export const ProfilePage = () => {
  const { user } = useAuth()
  const [member, setMember] = useState<Member | null>(null)
  const [transactions, setTransactions] = useState<IssueTransaction[]>([])
  const [fines, setFines] = useState<Fine[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'transactions' | 'fines'>('overview')

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [memberRes, transactionsRes] = await Promise.all([
          membersApi.profile(),
          issuesApi.memberTransactions(0, { limit: 50 }), // Will need member ID
        ])
        setMember(memberRes.data)
        setTransactions(transactionsRes.data)
      } catch (error) {
        console.error('Failed to load profile', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Profile</h1>
          <p className="text-muted-foreground">View your library account details</p>
        </div>
        <Card><CardContent className="p-6 h-96"><div className="animate-pulse space-y-4"><div className="h-8 bg-muted rounded w-1/4"></div><div className="h-4 bg-muted rounded w-1/2"></div></div></CardContent></Card>
      </div>
    )
  }

  if (!member) return null

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">My Profile</h1>
        <p className="text-muted-foreground">View your library account details and activity</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary/10 rounded-xl">
                <Shield className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <Badge variant={statusColors[member.status as keyof typeof statusColors] || 'secondary'} className="text-base">
                  {member.status.charAt(0).toUpperCase() + member.status.slice(1)}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-xl">
                <BookOpen className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Currently Issued</p>
                <p className="text-2xl font-bold">{member.currently_issued_books || 0} / {member.max_books_allowed}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-yellow-100 rounded-xl">
                <AlertTriangle className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Overdue Books</p>
                <p className="text-2xl font-bold text-destructive">{member.overdue_books || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 rounded-xl">
                <DollarSign className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Outstanding Fines</p>
                <p className="text-2xl font-bold text-destructive">{formatCurrency(member.outstanding_fines)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="transactions">My Transactions ({transactions.length})</TabsTrigger>
          <TabsTrigger value="fines">My Fines</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Account Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <dl className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <dt className="text-sm text-muted-foreground">Member ID</dt>
                    <dd className="font-medium font-mono">{member.member_id}</dd>
                    <dt className="text-sm text-muted-foreground">Name</dt>
                    <dd className="font-medium">{member.first_name} {member.last_name}</dd>
                    <dt className="text-sm text-muted-foreground">Email</dt>
                    <dd className="font-medium">{member.email}</dd>
                    <dt className="text-sm text-muted-foreground">Phone</dt>
                    <dd className="font-medium">{member.phone || '—'}</dd>
                    <dt className="text-sm text-muted-foreground">Membership Type</dt>
                    <dd className="font-medium capitalize">{member.membership_type}</dd>
                    <dt className="text-sm text-muted-foreground">Member Since</dt>
                    <dd className="font-medium">{formatDate(member.registration_date)}</dd>
                    <dt className="text-sm text-muted-foreground">Expiry Date</dt>
                    <dd className="font-medium">{member.expiry_date ? formatDate(member.expiry_date) : '—'}</dd>
                    <dt className="text-sm text-muted-foreground">Max Books Allowed</dt>
                    <dd className="font-medium">{member.max_books_allowed}</dd>
                  </div>
                </dl>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Address</CardTitle>
              </CardHeader>
              <CardContent>
                <address className="not-italic whitespace-pre-wrap text-muted-foreground">
                  {member.address || 'No address provided'}
                </address>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="transactions">
          <Card>
            <CardContent className="pt-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Transaction ID</TableHead>
                    <TableHead>Book</TableHead>
                    <TableHead>Issue Date</TableHead>
                    <TableHead>Due Date</TableHead>
                    <TableHead>Return Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Fine</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {transactions.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                        No transactions found
                      </TableCell>
                    </TableRow>
                  ) : (
                    transactions.map((txn) => (
                      <TableRow key={txn.id}>
                        <TableCell className="font-mono text-sm">{txn.transaction_id}</TableCell>
                        <TableCell>{txn.book?.title || 'Unknown'}</TableCell>
                        <TableCell>{formatDate(txn.issue_date)}</TableCell>
                        <TableCell>{formatDate(txn.due_date)}</TableCell>
                        <TableCell>{txn.return_date ? formatDate(txn.return_date) : '—'}</TableCell>
                        <TableCell>
                          <Badge variant={issueStatusColors[txn.status as keyof typeof issueStatusColors] || 'secondary'}>
                            {txn.status.charAt(0).toUpperCase() + txn.status.slice(1)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {txn.fine_amount > 0 ? formatCurrency(txn.fine_amount) : '—'}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="fines">
          <Card>
            <CardContent className="pt-0">
              <p className="text-center text-muted-foreground py-8">Fine details will be shown here</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
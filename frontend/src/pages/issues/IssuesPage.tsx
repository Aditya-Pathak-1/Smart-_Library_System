import React, { useEffect, useState } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import { Plus, Search, Filter, ChevronDown, Edit, Trash2, Eye, RotateCcw, Calendar, BookOpen, User, AlertTriangle, DollarSign } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import { Badge } from '../../components/ui/Badge'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/Table'
import { Pagination } from '../../components/ui/Pagination'
import { Skeleton } from '../../components/ui/Skeleton'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from '../../components/ui/DropdownMenu'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../../components/ui/Dialog'
import { issuesApi, membersApi, booksApi } from '../../services/api'
import { toast } from 'sonner'
import type { IssueTransaction, Member, Book, PaginatedResponse } from '../../types'
import { formatDate, formatCurrency, calculateOverdueDays } from '../../lib/utils'

const issueStatusColors = {
  issued: 'info',
  returned: 'success',
  overdue: 'destructive',
  lost: 'secondary',
} as const

export const IssuesPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const [transactions, setTransactions] = useState<IssueTransaction[]>([])
  const [members, setMembers] = useState<Member[]>([])
  const [books, setBooks] = useState<Book[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pageSize] = useState(20)
  const [search, setSearch] = useState(searchParams.get('search') || '')
  const [memberFilter, setMemberFilter] = useState(searchParams.get('member_id') || '')
  const [bookFilter, setBookFilter] = useState(searchParams.get('book_id') || '')
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '')
  const [issueDialogOpen, setIssueDialogOpen] = useState(false)
  const [returnDialogOpen, setReturnDialogOpen] = useState(false)
  const [selectedTransaction, setSelectedTransaction] = useState<IssueTransaction | null>(null)
  const [issuing, setIssuing] = useState(false)
  const [returning, setReturning] = useState(false)
  const [issueForm, setIssueForm] = useState({ member_id: '', book_id: '', due_date: '', notes: '' })
  const [returnForm, setReturnForm] = useState({ transaction_id: '', notes: '' })

  const fetchTransactions = async () => {
    try {
      setLoading(true)
      const params: any = {
        skip: (page - 1) * pageSize,
        limit: pageSize,
        search: search || undefined,
        member_id: memberFilter ? parseInt(memberFilter) : undefined,
        book_id: bookFilter ? parseInt(bookFilter) : undefined,
        status: statusFilter || undefined,
      }
      const response = await issuesApi.list(params)
      setTransactions(response.data)
      setTotal(Number(response.headers['x-total-count']) || response.data.length)
    } catch (error) {
      toast.error('Failed to load transactions')
    } finally {
      setLoading(false)
    }
  }

  const fetchMembersAndBooks = async () => {
    try {
      const [membersRes, booksRes] = await Promise.all([
        membersApi.list({ limit: 500, status: 'active' }),
        booksApi.list({ limit: 500, available_only: true }),
      ])
      setMembers(membersRes.data)
      setBooks(booksRes.data)
    } catch (error) {
      toast.error('Failed to load members/books')
    }
  }

  useEffect(() => {
    fetchTransactions()
    fetchMembersAndBooks()
  }, [page, search, memberFilter, bookFilter, statusFilter])

  const handleIssue = async (e: React.FormEvent) => {
    e.preventDefault()
    setIssuing(true)
    try {
      await issuesApi.issue({
        member_id: parseInt(issueForm.member_id),
        book_id: parseInt(issueForm.book_id),
        due_date: issueForm.due_date || undefined,
        notes: issueForm.notes || undefined,
      })
      toast.success('Book issued successfully')
      setIssueDialogOpen(false)
      setIssueForm({ member_id: '', book_id: '', due_date: '', notes: '' })
      fetchTransactions()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to issue book')
    } finally {
      setIssuing(false)
    }
  }

  const handleReturn = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedTransaction) return
    setReturning(true)
    try {
      await issuesApi.return({
        transaction_id: selectedTransaction.transaction_id,
        notes: returnForm.notes || undefined,
      })
      toast.success('Book returned successfully')
      setReturnDialogOpen(false)
      setSelectedTransaction(null)
      setReturnForm({ transaction_id: '', notes: '' })
      fetchTransactions()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to return book')
    } finally {
      setReturning(false)
    }
  }

  const handleRenew = async (transactionId: string) => {
    try {
      await issuesApi.renew(transactionId)
      toast.success('Book renewed successfully')
      fetchTransactions()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to renew book')
    }
  }

  const getOverdueInfo = (txn: IssueTransaction) => {
    if (txn.status === 'returned') return { overdue: false, days: 0 }
    const today = new Date()
    const due = new Date(txn.due_date)
    const diffTime = today.getTime() - due.getTime()
    const days = Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)))
    return { overdue: days > 0, days }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Issue / Return</h1>
          <p className="text-muted-foreground">Manage book circulation</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => {
            setSelectedTransaction(null)
            setReturnForm({ transaction_id: '', notes: '' })
            setReturnDialogOpen(true)
          }}>
            <RotateCcw className="mr-2 h-4 w-4" />
            Return Book
          </Button>
          <Button onClick={() => {
            setIssueForm({ member_id: '', book_id: '', due_date: '', notes: '' })
            setIssueDialogOpen(true)
          }}>
            <Plus className="mr-2 h-4 w-4" />
            Issue Book
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <div className="relative sm:col-span-2 lg:col-span-3">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by transaction ID, member, book..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select
              value={memberFilter}
              onValueChange={setMemberFilter}
              options={[{ value: '', label: 'All Members' }, ...members.map(m => ({ value: String(m.id), label: `${m.first_name} ${m.last_name} (${m.member_id})` }))]}
              placeholder="Member"
            />
            <Select
              value={bookFilter}
              onValueChange={setBookFilter}
              options={[{ value: '', label: 'All Books' }, ...books.map(b => ({ value: String(b.id), label: b.title }))]}
              placeholder="Book"
            />
            <Select
              value={statusFilter}
              onValueChange={setStatusFilter}
              options={[
                { value: '', label: 'All Statuses' },
                { value: 'issued', label: 'Issued' },
                { value: 'returned', label: 'Returned' },
                { value: 'overdue', label: 'Overdue' },
                { value: 'lost', label: 'Lost' },
              ]}
              placeholder="Status"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Transaction ID</TableHead>
                <TableHead>Member</TableHead>
                <TableHead>Book</TableHead>
                <TableHead>Issue Date</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Return Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Fine</TableHead>
                <TableHead className="w-60 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
                    <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
                    <TableCell><Skeleton className="h-8 w-20" /></TableCell>
                  </TableRow>
                  ))
              ) : transactions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                    No transactions found
                  </TableCell>
                </TableRow>
              ) : (
                transactions.map((txn) => {
                  const { overdue, days } = getOverdueInfo(txn)
                  return (
                    <TableRow key={txn.id} className={overdue && txn.status === 'issued' ? 'bg-destructive/5' : ''}>
                      <TableCell className="font-mono text-sm">{txn.transaction_id}</TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{txn.member?.first_name} {txn.member?.last_name}</p>
                          <p className="text-xs text-muted-foreground">{txn.member?.member_id}</p>
                        </div>
                      </TableCell>
                      <TableCell>{txn.book?.title || 'Unknown'}</TableCell>
                      <TableCell>{formatDate(txn.issue_date)}</TableCell>
                      <TableCell className={overdue && txn.status === 'issued' ? 'text-destructive font-medium' : ''}>
                        {formatDate(txn.due_date)}
                        {overdue && txn.status === 'issued' && (
                          <Badge variant="destructive" className="ml-2 text-xs">{days} days overdue</Badge>
                        )}
                      </TableCell>
                      <TableCell>{txn.return_date ? formatDate(txn.return_date) : '—'}</TableCell>
                      <TableCell>
                        <Badge variant={issueStatusColors[txn.status as keyof typeof issueStatusColors] || 'secondary'}>
                          {txn.status.charAt(0).toUpperCase() + txn.status.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {txn.fine_amount > 0 ? (
                          <span className={txn.fine_paid < txn.fine_amount ? 'text-destructive' : 'text-green-600'}>
                            {formatCurrency(txn.fine_amount)}
                            {txn.fine_paid > 0 && (
                              <span className="text-xs text-muted-foreground ml-1">(Paid: {formatCurrency(txn.fine_paid)})</span>
                            )}
                          </span>
                        ) : '—'}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <ChevronDown className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            {txn.status === 'issued' && (
                              <>
                                <DropdownMenuItem onClick={() => handleRenew(txn.transaction_id)}>
                                  <RotateCcw className="mr-2 h-4 w-4" />
                                  Renew
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => {
                                  setSelectedTransaction(txn)
                                  setReturnForm({ transaction_id: txn.transaction_id, notes: '' })
                                  setReturnDialogOpen(true)
                                }}>
                                  <BookOpen className="mr-2 h-4 w-4" />
                                  Return
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                              </>
                            )}
                            <DropdownMenuItem asChild>
                              <Link to={`/members/${txn.member?.id}`} onClick={() => navigate(`/members/${txn.member?.id}`)}>
                                <User className="mr-2 h-4 w-4" />
                                View Member
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem asChild>
                              <Link to={`/books/${txn.book?.id}`} onClick={() => navigate(`/books/${txn.book?.id}`)}>
                                <BookOpen className="mr-2 h-4 w-4" />
                                View Book
                              </Link>
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  )
                })
              )}
            </TableBody>
          </Table>

          {total > pageSize && (
            <div className="border-t pt-4">
              <Pagination
                page={page}
                totalPages={Math.ceil(total / pageSize)}
                onPageChange={setPage}
                total={total}
                showTotal
              />
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={issueDialogOpen} onOpenChange={setIssueDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Issue Book</DialogTitle>
            <DialogDescription>Select a member and book to issue</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleIssue} className="space-y-4 p-6">
            <Select
              value={issueForm.member_id}
              onValueChange={(v) => setIssueForm({ ...issueForm, member_id: v })}
              label="Member *"
              placeholder="Select member"
              options={members.map(m => ({ value: String(m.id), label: `${m.first_name} ${m.last_name} (${m.member_id})` }))}
              error={!issueForm.member_id ? 'Required' : undefined}
            />
            <Select
              value={issueForm.book_id}
              onValueChange={(v) => setIssueForm({ ...issueForm, book_id: v })}
              label="Book *"
              placeholder="Select book"
              options={books.map(b => ({ value: String(b.id), label: `${b.title} (Available: ${b.available_copies})` }))}
              error={!issueForm.book_id ? 'Required' : undefined}
            />
            <Input
              label="Due Date"
              type="date"
              value={issueForm.due_date}
              onChange={(e) => setIssueForm({ ...issueForm, due_date: e.target.value })}
            />
            <Input
              label="Notes"
              placeholder="Optional notes"
              value={issueForm.notes}
              onChange={(e) => setIssueForm({ ...issueForm, notes: e.target.value })}
            />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIssueDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={issuing}>
                Issue Book
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={returnDialogOpen} onOpenChange={setReturnDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Return Book</DialogTitle>
            <DialogDescription>
              {selectedTransaction
                ? `Returning: ${selectedTransaction.book?.title} by ${selectedTransaction.member?.first_name} ${selectedTransaction.member?.last_name}`
                : 'Enter transaction ID to return a book'
              }
            </DialogDescription>
          </DialogHeader>
<form onSubmit={handleReturn} className="space-y-4 p-6">
            {!selectedTransaction && (
              <Input
                label="Transaction ID *"
                placeholder="TXN1234567890"
                value={returnForm.transaction_id}
                onChange={(e) => setReturnForm({ ...returnForm, transaction_id: e.target.value })}
                error={!returnForm.transaction_id ? 'Required' : undefined}
              />
            )}
            <Input
              label="Notes"
              placeholder="Optional notes"
              value={returnForm.notes}
              onChange={(e) => setReturnForm({ ...returnForm, notes: e.target.value })}
            />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => {
                setReturnDialogOpen(false)
                setSelectedTransaction(null)
              }}>
                Cancel
              </Button>
              <Button type="submit" loading={returning}>
                Return Book
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
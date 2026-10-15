import React, { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Search, Filter, ChevronDown, Edit, Eye, DollarSign, Receipt, AlertTriangle } from 'lucide-react'
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
import { finesApi, membersApi } from '../../services/api'
import { toast } from 'sonner'
import { Link } from 'react-router-dom'
import type { Fine, FinePayment, Member, PaginatedResponse } from '../../types'
import { formatDate, formatCurrency } from '../../lib/utils'

const fineStatusColors = {
  pending: 'warning',
  partial: 'info',
  paid: 'success',
  waived: 'secondary',
} as const

export const FinesPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const [fines, setFines] = useState<Fine[]>([])
  const [members, setMembers] = useState<Member[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pageSize] = useState(20)
  const [search, setSearch] = useState(searchParams.get('search') || '')
  const [memberFilter, setMemberFilter] = useState(searchParams.get('member_id') || '')
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '')
  const [paymentDialogOpen, setPaymentDialogOpen] = useState(false)
  const [selectedFine, setSelectedFine] = useState<Fine | null>(null)
  const [paymentForm, setPaymentForm] = useState({ fine_id: 0, amount: '', payment_method: 'cash', notes: '' })
  const [processing, setProcessing] = useState(false)

  const fetchFines = async () => {
    try {
      setLoading(true)
      const params: any = {
        skip: (page - 1) * pageSize,
        limit: pageSize,
        search: search || undefined,
        member_id: memberFilter ? parseInt(memberFilter) : undefined,
        status: statusFilter || undefined,
      }
      const response = await finesApi.list(params)
      setFines(response.data)
      setTotal(Number(response.headers['x-total-count']) || response.data.length)
    } catch (error) {
      toast.error('Failed to load fines')
    } finally {
      setLoading(false)
    }
  }

  const fetchMembers = async () => {
    try {
      const response = await membersApi.list({ limit: 500 })
      setMembers(response.data)
    } catch (error) {
      toast.error('Failed to load members')
    }
  }

  useEffect(() => {
    fetchFines()
    fetchMembers()
  }, [page, search, memberFilter, statusFilter])

  const handlePayment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFine) return
    setProcessing(true)
    try {
      await finesApi.payments.record({
        fine_id: selectedFine.id,
        amount: parseFloat(paymentForm.amount),
        payment_method: paymentForm.payment_method,
        notes: paymentForm.notes || undefined,
      })
      toast.success('Payment recorded successfully')
      setPaymentDialogOpen(false)
      setSelectedFine(null)
      setPaymentForm({ fine_id: 0, amount: '', payment_method: 'cash', notes: '' })
      fetchFines()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to record payment')
    } finally {
      setProcessing(false)
    }
  }

  const openPaymentDialog = (fine: Fine) => {
    setSelectedFine(fine)
    setPaymentForm({
      fine_id: fine.id,
      amount: String(fine.final_amount - fine.paid_amount),
      payment_method: 'cash',
      notes: '',
    })
    setPaymentDialogOpen(true)
  }

  const getOutstanding = (fine: Fine) => fine.final_amount - fine.paid_amount

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Fines Management</h1>
          <p className="text-muted-foreground">Track and collect overdue fines</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="relative sm:col-span-2">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by fine ID, member, book..."
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
              value={statusFilter}
              onValueChange={setStatusFilter}
              options={[
                { value: '', label: 'All Statuses' },
                { value: 'pending', label: 'Pending' },
                { value: 'partial', label: 'Partial' },
                { value: 'paid', label: 'Paid' },
                { value: 'waived', label: 'Waived' },
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
                <TableHead>Fine ID</TableHead>
                <TableHead>Member</TableHead>
                <TableHead>Book</TableHead>
                <TableHead>Overdue Days</TableHead>
                <TableHead>Fine/Day</TableHead>
                <TableHead>Total Fine</TableHead>
                <TableHead>Paid</TableHead>
                <TableHead>Outstanding</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-48 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
                    <TableCell><Skeleton className="h-5 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-8 w-20" /></TableCell>
                  </TableRow>
                ))
              ) : fines.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} className="text-center py-8 text-muted-foreground">
                    No fines found
                  </TableCell>
                </TableRow>
              ) : (
                fines.map((fine) => (
                  <TableRow key={fine.id}>
                    <TableCell className="font-mono text-sm">{fine.fine_id}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{fine.member?.first_name} {fine.member?.last_name}</p>
                        <p className="text-xs text-muted-foreground">{fine.member?.member_id}</p>
                      </div>
                    </TableCell>
                    <TableCell>{fine.issue?.book?.title || 'Unknown'}</TableCell>
                    <TableCell>{fine.overdue_days}</TableCell>
                    <TableCell>{formatCurrency(fine.fine_per_day)}</TableCell>
                    <TableCell className="font-medium">{formatCurrency(fine.final_amount)}</TableCell>
                    <TableCell>{formatCurrency(fine.paid_amount)}</TableCell>
                    <TableCell className="font-medium text-destructive">{formatCurrency(getOutstanding(fine))}</TableCell>
                    <TableCell>
                      <Badge variant={fineStatusColors[fine.status as keyof typeof fineStatusColors] || 'secondary'}>
                        {fine.status.charAt(0).toUpperCase() + fine.status.slice(1)}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <ChevronDown className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link to={`/fines/${fine.id}`} onClick={() => navigate(`/fines/${fine.id}`)}>
                              <Eye className="mr-2 h-4 w-4" />
                              View Details
                            </Link>
                          </DropdownMenuItem>
                          {fine.status !== 'paid' && fine.status !== 'waived' && (
                            <>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem onClick={() => openPaymentDialog(fine)}>
                                <DollarSign className="mr-2 h-4 w-4" />
                                Record Payment
                              </DropdownMenuItem>
                            </>
                          )}
                          {fine.payments && fine.payments.length > 0 && (
                            <>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem asChild>
                                <Link to={`/fines/${fine.id}/receipt`} onClick={() => navigate(`/fines/${fine.id}/receipt`)}>
                                  <Receipt className="mr-2 h-4 w-4" />
                                  View Receipt
                                </Link>
                              </DropdownMenuItem>
                            </>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
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

      <Dialog open={paymentDialogOpen} onOpenChange={setPaymentDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Record Payment</DialogTitle>
            <DialogDescription>
              {selectedFine
                ? `Collecting from ${selectedFine.member?.first_name} ${selectedFine.member?.last_name} - Outstanding: ${formatCurrency(getOutstanding(selectedFine))}`
                : 'Enter payment details'
              }
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handlePayment} className="space-y-4 p-6">
            <Input
              label="Amount *"
              type="number"
              step="0.01"
              min="0.01"
              max={selectedFine ? getOutstanding(selectedFine) : undefined}
              value={paymentForm.amount}
              onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })}
              error={!paymentForm.amount || parseFloat(paymentForm.amount) <= 0 ? 'Required' : undefined}
            />
            <Select
              value={paymentForm.payment_method}
              onValueChange={(v) => setPaymentForm({ ...paymentForm, payment_method: v })}
              label="Payment Method *"
              placeholder="Select method"
              options={[
                { value: 'cash', label: 'Cash' },
                { value: 'card', label: 'Card' },
                { value: 'upi', label: 'UPI' },
                { value: 'bank_transfer', label: 'Bank Transfer' },
                { value: 'cheque', label: 'Cheque' },
              ]}
            />
            <Input
              label="Notes"
              placeholder="Optional notes"
              value={paymentForm.notes}
              onChange={(e) => setPaymentForm({ ...paymentForm, notes: e.target.value })}
            />
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => {
                setPaymentDialogOpen(false)
                setSelectedFine(null)
              }}>
                Cancel
              </Button>
              <Button type="submit" loading={processing}>
                Record Payment
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
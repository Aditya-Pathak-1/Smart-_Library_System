import React, { useEffect, useState } from 'react'
import { Calendar, Download, FileText, Users, BookOpen, DollarSign, TrendingUp, AlertTriangle } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/Table'
import { Badge } from '../../components/ui/Badge'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../components/ui/Tabs'
import { Skeleton } from '../../components/ui/Skeleton'
import { reportsApi } from '../../services/api'
import { toast } from 'sonner'
import type { 
  BookInventoryReportItem, 
  IssuedBooksReportItem, 
  OverdueBooksReportItem, 
  MemberActivityReportItem, 
  FineCollectionReportItem, 
  MostBorrowedBookItem 
} from '../../types'
import { formatDate, formatCurrency } from '../../lib/utils'

const reportTabs = [
  { id: 'inventory', label: 'Book Inventory', icon: BookOpen },
  { id: 'issued', label: 'Issued Books', icon: BookOpen },
  { id: 'overdue', label: 'Overdue Books', icon: AlertTriangle },
  { id: 'members', label: 'Member Activity', icon: Users },
  { id: 'fines', label: 'Fine Collection', icon: DollarSign },
  { id: 'most-borrowed', label: 'Most Borrowed', icon: TrendingUp },
] as const

export const ReportsPage = () => {
  const [activeTab, setActiveTab] = useState<'inventory' | 'issued' | 'overdue' | 'members' | 'fines' | 'most-borrowed'>('inventory')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [loading, setLoading] = useState(false)
  
  // Report data states
  const [inventoryData, setInventoryData] = useState<BookInventoryReportItem[]>([])
  const [issuedData, setIssuedData] = useState<IssuedBooksReportItem[]>([])
  const [overdueData, setOverdueData] = useState<OverdueBooksReportItem[]>([])
  const [membersData, setMembersData] = useState<MemberActivityReportItem[]>([])
  const [finesData, setFinesData] = useState<FineCollectionReportItem[]>([])
  const [mostBorrowedData, setMostBorrowedData] = useState<MostBorrowedBookItem[]>([])

  const fetchReport = async (tab: string) => {
    setLoading(true)
    try {
      const filters: any = {}
      if (startDate) filters.start_date = startDate
      if (endDate) filters.end_date = endDate
      if (categoryFilter) filters.category_id = parseInt(categoryFilter)

      switch (tab) {
        case 'inventory':
          const invRes = await reportsApi.inventory(filters)
          setInventoryData(invRes.data)
          break
        case 'issued':
          const issRes = await reportsApi.issuedBooks(filters)
          setIssuedData(issRes.data)
          break
        case 'overdue':
          const ovdRes = await reportsApi.overdueBooksReport(filters)
          setOverdueData(ovdRes.data)
          break
        case 'members':
          const memRes = await reportsApi.members(filters)
          setMembersData(memRes.data)
          break
        case 'fines':
          const fineRes = await reportsApi.fines(filters)
          setFinesData(fineRes.data)
          break
        case 'most-borrowed':
          const mbRes = await reportsApi.mostBorrowed(20)
          setMostBorrowedData(mbRes.data)
          break
      }
    } catch (error) {
      toast.error('Failed to load report')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReport(activeTab)
  }, [activeTab, startDate, endDate, categoryFilter])

  const exportReport = async (tab: string) => {
    try {
      const filters: any = {}
      if (startDate) filters.start_date = startDate
      if (endDate) filters.end_date = endDate
      if (categoryFilter) filters.category_id = parseInt(categoryFilter)

      let blob: Blob
      switch (tab) {
        case 'inventory':
          const invRes = await reportsApi.export.inventory(filters)
          blob = invRes.data
          break
        case 'issued':
          const issRes = await reportsApi.export.issued(filters)
          blob = issRes.data
          break
        case 'overdue':
          const ovdRes = await reportsApi.export.overdue(filters)
          blob = ovdRes.data
          break
        case 'fines':
          const fineRes = await reportsApi.export.fines(filters)
          blob = fineRes.data
          break
        default:
          toast.error('Export not available for this report')
          return
      }

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${tab}_report_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success('Report exported successfully')
    } catch (error) {
      toast.error('Failed to export report')
    }
  }

  const renderInventoryTable = () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Title</TableHead>
          <TableHead>ISBN</TableHead>
          <TableHead>Author</TableHead>
          <TableHead>Category</TableHead>
          <TableHead>Total</TableHead>
          <TableHead>Available</TableHead>
          <TableHead>Issued</TableHead>
          <TableHead>Location</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <TableRow key={i}>
              <TableCell><Skeleton className="h-4 w-3/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
            </TableRow>
          ))
        ) : inventoryData.length === 0 ? (
          <TableRow>
            <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">No data</TableCell>
          </TableRow>
        ) : (
          inventoryData.map((item) => (
            <TableRow key={item.book_id}>
              <TableCell>{item.title}</TableCell>
              <TableCell className="font-mono text-sm">{item.isbn}</TableCell>
              <TableCell>{item.author}</TableCell>
              <TableCell>{item.category}</TableCell>
              <TableCell>{item.total_copies}</TableCell>
              <TableCell className="text-green-600 font-medium">{item.available_copies}</TableCell>
              <TableCell className="text-blue-600 font-medium">{item.issued_copies}</TableCell>
              <TableCell>{item.shelf_location || '—'}</TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  )

  const renderIssuedTable = () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Transaction ID</TableHead>
          <TableHead>Book</TableHead>
          <TableHead>Member</TableHead>
          <TableHead>Issue Date</TableHead>
          <TableHead>Due Date</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Overdue</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <TableRow key={i}>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-3/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-5 w-20" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
            </TableRow>
          ))
        ) : issuedData.length === 0 ? (
          <TableRow>
            <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">No data</TableCell>
          </TableRow>
        ) : (
          issuedData.map((item) => (
            <TableRow key={item.transaction_id}>
              <TableCell className="font-mono text-sm">{item.transaction_id}</TableCell>
              <TableCell>{item.book_title}</TableCell>
              <TableCell>{item.member_name} ({item.member_id})</TableCell>
              <TableCell>{formatDate(item.issue_date)}</TableCell>
              <TableCell>{formatDate(item.due_date)}</TableCell>
              <TableCell>
                <Badge variant={item.status === 'overdue' ? 'destructive' : item.status === 'issued' ? 'info' : 'success'}>
                  {item.status}
                </Badge>
              </TableCell>
              <TableCell>{item.overdue_days > 0 ? `${item.overdue_days} days` : '—'}</TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  )

  const renderOverdueTable = () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Transaction ID</TableHead>
          <TableHead>Book</TableHead>
          <TableHead>Member</TableHead>
          <TableHead>Issue Date</TableHead>
          <TableHead>Due Date</TableHead>
          <TableHead>Overdue</TableHead>
          <TableHead>Est. Fine</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <TableRow key={i}>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-3/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
            </TableRow>
          ))
        ) : overdueData.length === 0 ? (
          <TableRow>
            <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">No overdue books</TableCell>
          </TableRow>
        ) : (
          overdueData.map((item) => (
            <TableRow key={item.transaction_id}>
              <TableCell className="font-mono text-sm">{item.transaction_id}</TableCell>
              <TableCell>{item.book_title}</TableCell>
              <TableCell>{item.member_name} ({item.member_id})</TableCell>
              <TableCell>{formatDate(item.issue_date)}</TableCell>
              <TableCell>{formatDate(item.due_date)}</TableCell>
              <TableCell className="text-destructive font-medium">{item.overdue_days} days</TableCell>
              <TableCell className="text-destructive font-medium">{formatCurrency(item.estimated_fine)}</TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  )

  const renderMembersTable = () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Member ID</TableHead>
          <TableHead>Name</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Total Borrowed</TableHead>
          <TableHead>Currently Issued</TableHead>
          <TableHead>Overdue</TableHead>
          <TableHead>Total Fines</TableHead>
          <TableHead>Paid</TableHead>
          <TableHead>Outstanding</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <TableRow key={i}>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-3/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
            </TableRow>
          ))
        ) : membersData.length === 0 ? (
          <TableRow>
            <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">No data</TableCell>
          </TableRow>
        ) : (
          membersData.map((item) => (
            <TableRow key={item.member_id}>
              <TableCell className="font-mono text-sm">{item.member_id}</TableCell>
              <TableCell>{item.member_name}</TableCell>
              <TableCell>{item.email}</TableCell>
              <TableCell>{item.total_borrowed}</TableCell>
              <TableCell>{item.currently_issued}</TableCell>
              <TableCell className={item.overdue_count > 0 ? 'text-destructive' : ''}>{item.overdue_count}</TableCell>
              <TableCell>{formatCurrency(item.total_fines)}</TableCell>
              <TableCell>{formatCurrency(item.fines_paid)}</TableCell>
              <TableCell className={item.outstanding_fines > 0 ? 'text-destructive font-medium' : ''}>{formatCurrency(item.outstanding_fines)}</TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  )

  const renderFinesTable = () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Receipt</TableHead>
          <TableHead>Member</TableHead>
          <TableHead>Book</TableHead>
          <TableHead>Amount</TableHead>
          <TableHead>Method</TableHead>
          <TableHead>Date</TableHead>
          <TableHead>Received By</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <TableRow key={i}>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-3/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
            </TableRow>
          ))
        ) : finesData.length === 0 ? (
          <TableRow>
            <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">No data</TableCell>
          </TableRow>
        ) : (
          finesData.map((item) => (
            <TableRow key={item.payment_id}>
              <TableCell className="font-mono text-sm">{item.receipt_number}</TableCell>
              <TableCell>{item.member_name} ({item.member_id})</TableCell>
              <TableCell>{item.book_title}</TableCell>
              <TableCell className="font-medium">{formatCurrency(item.amount)}</TableCell>
              <TableCell>{item.payment_method}</TableCell>
              <TableCell>{formatDate(item.payment_date)}</TableCell>
              <TableCell>{item.received_by}</TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  )

  const renderMostBorrowedTable = () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>#</TableHead>
          <TableHead>Title</TableHead>
          <TableHead>ISBN</TableHead>
          <TableHead>Author</TableHead>
          <TableHead>Category</TableHead>
          <TableHead>Borrow Count</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <TableRow key={i}>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-3/4" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
              <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
            </TableRow>
          ))
        ) : mostBorrowedData.length === 0 ? (
          <TableRow>
            <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">No data</TableCell>
          </TableRow>
        ) : (
          mostBorrowedData.map((item, index) => (
            <TableRow key={item.book_id}>
              <TableCell className="font-bold">{index + 1}</TableCell>
              <TableCell>{item.title}</TableCell>
              <TableCell className="font-mono text-sm">{item.isbn}</TableCell>
              <TableCell>{item.author}</TableCell>
              <TableCell>{item.category}</TableCell>
              <TableCell className="font-bold text-primary">{item.borrow_count}</TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'inventory':
        return renderInventoryTable()
      case 'issued':
        return renderIssuedTable()
      case 'overdue':
        return renderOverdueTable()
      case 'members':
        return renderMembersTable()
      case 'fines':
        return renderFinesTable()
      case 'most-borrowed':
        return renderMostBorrowedTable()
    }
  }

  const canExport = ['inventory', 'issued', 'overdue', 'fines'].includes(activeTab)

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
          <p className="text-muted-foreground">Generate and export library reports</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <Input
              label="Start Date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
            <Input
              label="End Date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
            <Select
              value={categoryFilter}
              onValueChange={setCategoryFilter}
              options={[
                { value: '', label: 'All Categories' },
                { value: '1', label: 'Fiction' },
                { value: '2', label: 'Non-Fiction' },
                { value: '3', label: 'Science & Technology' },
                { value: '4', label: 'Computer Science' },
              ]}
              placeholder="Category"
            />
            <div className="flex items-end">
              <Button onClick={() => fetchReport(activeTab)} loading={loading} className="w-full">
                Apply Filters
              </Button>
            </div>
            {canExport && (
              <div className="flex items-end">
                <Button variant="outline" onClick={() => exportReport(activeTab)} className="w-full">
                  <Download className="mr-2 h-4 w-4" />
                  Export CSV
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-3 md:grid-cols-6">
          {reportTabs.map((tab) => (
            <TabsTrigger key={tab.id} value={tab.id}>
              <tab.icon className="mr-2 h-4 w-4" />
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value="inventory">
          <Card>
            <CardContent className="pt-0">{renderInventoryTable()}</CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="issued">
          <Card>
            <CardContent className="pt-0">{renderIssuedTable()}</CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="overdue">
          <Card>
            <CardContent className="pt-0">{renderOverdueTable()}</CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="members">
          <Card>
            <CardContent className="pt-0">{renderMembersTable()}</CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="fines">
          <Card>
            <CardContent className="pt-0">{renderFinesTable()}</CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="most-borrowed">
          <Card>
            <CardContent className="pt-0">{renderMostBorrowedTable()}</CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
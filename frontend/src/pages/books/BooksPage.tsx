import React, { useEffect, useState } from 'react'
import { Plus, Search, Filter, ChevronDown, Edit, Trash2, Eye, BookOpen } from 'lucide-react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import { Badge } from '../../components/ui/Badge'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../../components/ui/Table'
import { Pagination } from '../../components/ui/Pagination'
import { Skeleton } from '../../components/ui/Skeleton'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from '../../components/ui/DropdownMenu'
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../../components/ui/Dialog'
import { booksApi, categoriesApi, authorsApi } from '../../services/api'
import { toast } from 'sonner'
import type { Book, Category, Author, PaginatedResponse } from '../../types'
import { formatDate } from '../../lib/utils'

export const availabilityColors = {
  Available: 'success',
  'Limited Copies': 'warning',
  Unavailable: 'destructive',
} as const

export const BooksPage = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const routeSearch = searchParams.get('search') || ''
  const [books, setBooks] = useState<Book[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [authors, setAuthors] = useState<Author[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pageSize] = useState(20)
  const [search, setSearch] = useState(routeSearch)
  const [categoryFilter, setCategoryFilter] = useState('')
  const [authorFilter, setAuthorFilter] = useState('')
  const [availableOnly, setAvailableOnly] = useState(false)
  const [sortBy, setSortBy] = useState('title')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [bookToDelete, setBookToDelete] = useState<Book | null>(null)

  const fetchBooks = async () => {
    try {
      setLoading(true)
      const response = await booksApi.list({
        skip: (page - 1) * pageSize,
        limit: pageSize,
        search: search || undefined,
        category_id: categoryFilter ? parseInt(categoryFilter) : undefined,
        author_id: authorFilter ? parseInt(authorFilter) : undefined,
        available_only: availableOnly,
        sort_by: sortBy,
        sort_order: sortOrder,
      })
      setBooks(response.data)
      setTotal(Number(response.headers['x-total-count']) || response.data.length)
    } catch (error) {
      toast.error('Failed to load books')
    } finally {
      setLoading(false)
    }
  }

  const fetchFilters = async () => {
    try {
      const [catsRes, authsRes] = await Promise.all([
        categoriesApi.list({ active_only: true }),
        authorsApi.list({ limit: 100 }),
      ])
      setCategories(catsRes.data)
      setAuthors(authsRes.data)
    } catch (error) {
      toast.error('Failed to load filters')
    }
  }

  useEffect(() => {
    fetchBooks()
    fetchFilters()
  }, [page, search, categoryFilter, authorFilter, availableOnly, sortBy, sortOrder])

  useEffect(() => {
    setSearch(routeSearch)
    setPage(1)
  }, [routeSearch])

  const handleDelete = async () => {
    if (!bookToDelete) return
    try {
      await booksApi.delete(bookToDelete.id)
      toast.success('Book deleted')
      setDeleteDialogOpen(false)
      fetchBooks()
    } catch (error) {
      toast.error('Failed to delete book')
    }
  }

  const getAvailabilityBadge = (book: Book) => {
    if (book.available_copies === 0) return 'Unavailable'
    if (book.available_copies < book.total_copies) return 'Limited Copies'
    return 'Available'
  }

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(column)
      setSortOrder('asc')
    }
  }

  const SortIcon = ({ column }: { column: string }) => {
    if (sortBy !== column) return <ChevronDown className="h-4 w-4 text-muted-foreground ml-1" />
    return <ChevronDown className={`h-4 w-4 ml-1 ${sortOrder === 'desc' ? 'rotate-180' : ''}`} />
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Books</h1>
          <p className="text-muted-foreground">Manage your library catalog</p>
        </div>
        <Dialog>
          <DialogTrigger asChild>
            <Button onClick={() => navigate('/books/new')}>
              <Plus className="mr-2 h-4 w-4" />
              Add Book
            </Button>
          </DialogTrigger>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <div className="relative col-span-2 lg:col-span-3">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by title, author, ISBN..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select
              value={categoryFilter}
              onValueChange={setCategoryFilter}
              options={[{ value: '', label: 'All Categories' }, ...categories.map(c => ({ value: String(c.id), label: c.name }))]}
              placeholder="Category"
            />
            <Select
              value={authorFilter}
              onValueChange={setAuthorFilter}
              options={[{ value: '', label: 'All Authors' }, ...authors.map(a => ({ value: String(a.id), label: a.name }))]}
              placeholder="Author"
            />
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="availableOnly"
                checked={availableOnly}
                onChange={(e) => setAvailableOnly(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <label htmlFor="availableOnly" className="text-sm">Available only</label>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead onClick={() => handleSort('title')} className="cursor-pointer select-none flex items-center gap-1">
                  Title <SortIcon column="title" />
                </TableHead>
                <TableHead onClick={() => handleSort('author')} className="cursor-pointer select-none flex items-center gap-1">
                  Author <SortIcon column="author" />
                </TableHead>
                <TableHead onClick={() => handleSort('category')} className="cursor-pointer select-none flex items-center gap-1">
                  Category <SortIcon column="category" />
                </TableHead>
                <TableHead onClick={() => handleSort('publication_year')} className="cursor-pointer select-none flex items-center gap-1">
                  Year <SortIcon column="publication_year" />
                </TableHead>
                <TableHead onClick={() => handleSort('available_copies')} className="cursor-pointer select-none flex items-center gap-1">
                  Available <SortIcon column="available_copies" />
                </TableHead>
                <TableHead className="w-48">Status</TableHead>
                <TableHead className="w-60 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-3/4" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/2" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-1/4" /></TableCell>
                    <TableCell><Skeleton className="h-5 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-8 w-20" /></TableCell>
                  </TableRow>
                ))
              ) : books.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                    No books found. Try adjusting your filters or add a new book.
                  </TableCell>
                </TableRow>
              ) : (
                books.map((book) => (
                  <TableRow key={book.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{book.title}</p>
                        <p className="text-xs text-muted-foreground">ISBN: {book.isbn}</p>
                      </div>
                    </TableCell>
                    <TableCell>{book.author?.name || 'Unknown'}</TableCell>
                    <TableCell>{book.category?.name || 'Unknown'}</TableCell>
                    <TableCell>{book.publication_year || '—'}</TableCell>
                    <TableCell className="font-medium">
                      {book.available_copies} / {book.total_copies}
                    </TableCell>
                    <TableCell>
                      <Badge variant={availabilityColors[getAvailabilityBadge(book)]}>
                        {getAvailabilityBadge(book)}
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
                            <Link to={`/books/${book.id}`} onClick={() => navigate(`/books/${book.id}`)}>
                              <Eye className="mr-2 h-4 w-4" />
                              View
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem asChild>
                            <Link to={`/books/${book.id}/edit`} onClick={() => navigate(`/books/${book.id}/edit`)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => {
                              setBookToDelete(book)
                              setDeleteDialogOpen(true)
                            }}
                            className="text-destructive focus:text-destructive"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
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

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Book</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{bookToDelete?.title}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// Need to import Link
import { Link } from 'react-router-dom'
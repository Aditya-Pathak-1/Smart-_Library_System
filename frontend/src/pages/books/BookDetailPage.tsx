import React, { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Edit, BookOpen, Calendar, Award, Tag, Package, Hash, Image } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card'
import { booksApi } from '../../services/api'
import { toast } from 'sonner'
import type { Book } from '../../types'
import { formatDate, formatCurrency } from '../../lib/utils'
import { availabilityColors } from './BooksPage'

export const BookDetailPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [book, setBook] = useState<Book | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchBook = async () => {
      try {
        const response = await booksApi.get(parseInt(id!))
        setBook(response.data)
      } catch (error) {
        toast.error('Failed to load book')
        navigate('/books')
      } finally {
        setLoading(false)
      }
    }
    fetchBook()
  }, [id, navigate])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => navigate('/books')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Loading...</h1>
          </div>
        </div>
        <Card><CardContent className="p-6 h-96"><div className="animate-pulse space-y-4"><div className="h-8 bg-muted rounded w-1/4"></div><div className="h-4 bg-muted rounded w-1/2"></div></div></CardContent></Card>
      </div>
    )
  }

  if (!book) return null

  const getAvailabilityBadge = (book: Book) => {
    if (book.available_copies === 0) return 'Unavailable'
    if (book.available_copies < book.total_copies) return 'Limited Copies'
    return 'Available'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate('/books')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">{book.title}</h1>
          <p className="text-muted-foreground">ISBN: {book.isbn}</p>
        </div>
        <Button asChild variant="outline">
          <Link to={`/books/${book.id}/edit`}>
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Link>
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Book Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">Author</p>
                  <p className="font-medium">{book.author?.name || 'Unknown'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Category</p>
                  <p className="font-medium">{book.category?.name || 'Unknown'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Publisher</p>
                  <p className="font-medium">{book.publisher || '—'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Publication Year</p>
                  <p className="font-medium">{book.publication_year || '—'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Shelf Location</p>
                  <p className="font-medium">{book.shelf_location || '—'}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Copies</p>
                  <p className="font-medium">{book.total_copies}</p>
                </div>
              </div>

              {book.description && (
                <div className="pt-4 border-t">
                  <p className="text-sm text-muted-foreground mb-2">Description</p>
                  <p className="whitespace-pre-wrap">{book.description}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Availability</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-3">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Available</p>
                  <p className="text-3xl font-bold text-green-600">{book.available_copies}</p>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Issued</p>
                  <p className="text-3xl font-bold text-blue-600">{book.total_copies - book.available_copies}</p>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Total</p>
                  <p className="text-3xl font-bold">{book.total_copies}</p>
                </div>
              </div>

              <Badge variant={availabilityColors[getAvailabilityBadge(book)]} className="text-lg px-4 py-2">
                {getAvailabilityBadge(book)}
              </Badge>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full justify-start" asChild>
                <Link to={`/books/${book.id}/edit`}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit Book
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link to={`/issues?book_id=${book.id}`}>
                  <BookOpen className="mr-2 h-4 w-4" />
                  Issue This Book
                </Link>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <Link to={`/books?search=${encodeURIComponent(book.isbn)}`}>
                  <Hash className="mr-2 h-4 w-4" />
                  View All Copies
                </Link>
              </Button>
            </CardContent>
          </Card>

          {book.cover_image_url && (
            <Card>
              <CardHeader>
                <CardTitle>Cover Image</CardTitle>
              </CardHeader>
              <CardContent>
                <img
                  src={book.cover_image_url}
                  alt={book.title}
                  className="w-full h-auto rounded-lg"
                />
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
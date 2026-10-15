import React, { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Plus, BookOpen } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import { Textarea } from '../../components/ui/Textarea'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../components/ui/Card'
import { booksApi, categoriesApi, authorsApi } from '../../services/api'
import { toast } from 'sonner'
import type { Category, Author } from '../../types'

const bookSchema = z.object({
  title: z.string().min(1, 'Title is required').max(500),
  isbn: z.string().min(10, 'ISBN must be at least 10 characters').max(13),
  author_id: z.coerce.number().min(1, 'Author is required'),
  category_id: z.coerce.number().min(1, 'Category is required'),
  publisher: z.string().max(255).optional().or(z.literal('')),
  publication_year: z.coerce.number().min(1000).max(2100).optional().nullable(),
  shelf_location: z.string().max(100).optional().or(z.literal('')),
  total_copies: z.coerce.number().min(1, 'At least 1 copy required').max(1000),
  cover_image_url: z.string().url('Invalid URL').optional().or(z.literal('')),
  description: z.string().max(2000).optional().or(z.literal('')),
})

type BookForm = z.infer<typeof bookSchema>

export const BookFormPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEditing = !!id
  const [categories, setCategories] = useState<Category[]>([])
  const [authors, setAuthors] = useState<Author[]>([])
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm<BookForm>({
    resolver: zodResolver(bookSchema),
    defaultValues: {
      total_copies: 1,
      publisher: '',
      shelf_location: '',
      cover_image_url: '',
      description: '',
    },
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [catsRes, authsRes] = await Promise.all([
          categoriesApi.list({ active_only: true }),
          authorsApi.list({ limit: 200 }),
        ])
        setCategories(catsRes.data)
        setAuthors(authsRes.data)

        if (isEditing) {
          const bookRes = await booksApi.get(parseInt(id!))
          const book = bookRes.data
          reset({
            title: book.title,
            isbn: book.isbn,
            author_id: book.author_id,
            category_id: book.category_id,
            publisher: book.publisher || '',
            publication_year: book.publication_year || undefined,
            shelf_location: book.shelf_location || '',
            total_copies: book.total_copies,
            cover_image_url: book.cover_image_url || '',
            description: book.description || '',
          })
        }
      } catch (error) {
        toast.error('Failed to load form data')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id, isEditing, reset])

  const onSubmit = async (data: BookForm) => {
    setSubmitting(true)
    try {
      const submitData = {
        ...data,
        publication_year: data.publication_year || null,
        cover_image_url: data.cover_image_url || null,
        description: data.description || null,
        publisher: data.publisher || null,
        shelf_location: data.shelf_location || null,
      }

      if (isEditing) {
        await booksApi.update(parseInt(id!), submitData)
        toast.success('Book updated successfully')
      } else {
        await booksApi.create(submitData)
        toast.success('Book created successfully')
      }
      navigate('/books')
    } catch (error) {
      toast.error(isEditing ? 'Failed to update book' : 'Failed to create book')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => navigate('/books')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{isEditing ? 'Edit Book' : 'Add New Book'}</h1>
          </div>
        </div>
        <Card><CardContent className="p-6 h-96"><div className="animate-pulse space-y-4"><div className="h-8 bg-muted rounded w-1/4"></div><div className="h-4 bg-muted rounded w-1/2"></div></div></CardContent></Card>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate('/books')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{isEditing ? 'Edit Book' : 'Add New Book'}</h1>
          <p className="text-muted-foreground">{isEditing ? 'Update book details' : 'Add a new book to the library catalog'}</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Book Details</CardTitle>
        </CardHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              {...register('title')}
              label="Title *"
              placeholder="Enter book title"
              error={errors.title?.message}
            />
            <Input
              {...register('isbn')}
              label="ISBN *"
              placeholder="9780123456789"
              error={errors.isbn?.message}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Select
              {...register('author_id')}
              label="Author *"
              placeholder="Select author"
              options={authors.map(a => ({ value: String(a.id), label: a.name }))}
              error={errors.author_id?.message}
            />
            <Select
              {...register('category_id')}
              label="Category *"
              placeholder="Select category"
              options={categories.map(c => ({ value: String(c.id), label: c.name }))}
              error={errors.category_id?.message}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              {...register('publisher')}
              label="Publisher"
              placeholder="Publisher name"
            />
            <Input
              {...register('publication_year')}
              label="Publication Year"
              type="number"
              placeholder="2024"
              error={errors.publication_year?.message}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              {...register('shelf_location')}
              label="Shelf Location"
              placeholder="A1-FIC-001"
            />
            <Input
              {...register('total_copies')}
              label="Total Copies *"
              type="number"
              min="1"
              max="1000"
              error={errors.total_copies?.message}
            />
          </div>

          <Input
            {...register('cover_image_url')}
            label="Cover Image URL"
            placeholder="https://example.com/cover.jpg"
            error={errors.cover_image_url?.message}
          />

          <Textarea
            {...register('description')}
            label="Description"
            placeholder="Book description..."
            rows={4}
          />

          <CardFooter className="flex justify-end gap-3">
            <Button type="button" variant="outline" onClick={() => navigate('/books')}>
              Cancel
            </Button>
            <Button type="submit" loading={submitting}>
              {isEditing ? 'Update Book' : 'Create Book'}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
import React, { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import { Textarea } from '../../components/ui/Textarea'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../../components/ui/Card'
import { membersApi } from '../../services/api'
import { toast } from 'sonner'
import type { Member } from '../../types'

const memberSchema = z.object({
  first_name: z.string().min(1, 'First name is required').max(100),
  last_name: z.string().min(1, 'Last name is required').max(100),
  email: z.string().email('Invalid email address'),
  phone: z.string().max(20).optional().or(z.literal('')),
  address: z.string().max(500).optional().or(z.literal('')),
  date_of_birth: z.string().optional().nullable(),
  membership_type: z.string().min(1, 'Membership type is required'),
  registration_date: z.string().min(1, 'Registration date is required'),
  expiry_date: z.string().optional().nullable(),
  status: z.enum(['active', 'inactive', 'suspended', 'expired']),
  max_books_allowed: z.coerce.number().min(1, 'At least 1 book allowed').max(50),
})

type MemberForm = z.infer<typeof memberSchema>

const today = new Date().toISOString().split('T')[0]

export const MemberFormPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEditing = !!id
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    watch,
    formState: { errors },
  } = useForm<MemberForm>({
    resolver: zodResolver(memberSchema),
    defaultValues: {
      membership_type: 'standard',
      registration_date: today,
      status: 'active',
      max_books_allowed: 5,
      phone: '',
      address: '',
    },
  })

  useEffect(() => {
    if (isEditing) {
      const fetchMember = async () => {
        try {
          setLoading(true)
          const response = await membersApi.get(parseInt(id!))
          const member = response.data
          reset({
            first_name: member.first_name,
            last_name: member.last_name,
            email: member.email,
            phone: member.phone || '',
            address: member.address || '',
            date_of_birth: member.date_of_birth || '',
            membership_type: member.membership_type,
            registration_date: member.registration_date,
            expiry_date: member.expiry_date || '',
            status: member.status,
            max_books_allowed: member.max_books_allowed,
          })
        } catch (error) {
          toast.error('Failed to load member')
        } finally {
          setLoading(false)
        }
      }
      fetchMember()
    }
  }, [id, isEditing, reset])

  const onSubmit = async (data: MemberForm) => {
    setSubmitting(true)
    try {
      const submitData = {
        ...data,
        phone: data.phone || null,
        address: data.address || null,
        date_of_birth: data.date_of_birth || null,
        expiry_date: data.expiry_date || null,
      }

      if (isEditing) {
        await membersApi.update(parseInt(id!), submitData)
        toast.success('Member updated successfully')
      } else {
        await membersApi.create(submitData)
        toast.success('Member created successfully')
      }
      navigate('/members')
    } catch (error) {
      toast.error(isEditing ? 'Failed to update member' : 'Failed to create member')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => navigate('/members')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{isEditing ? 'Edit Member' : 'Add New Member'}</h1>
          </div>
        </div>
        <Card><CardContent className="p-6 h-96"><div className="animate-pulse space-y-4"><div className="h-8 bg-muted rounded w-1/4"></div><div className="h-4 bg-muted rounded w-1/2"></div></div></CardContent></Card>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate('/members')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{isEditing ? 'Edit Member' : 'Register New Member'}</h1>
          <p className="text-muted-foreground">{isEditing ? 'Update member details' : 'Register a new library member'}</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Member Details</CardTitle>
        </CardHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              {...register('first_name')}
              label="First Name *"
              placeholder="John"
              error={errors.first_name?.message}
            />
            <Input
              {...register('last_name')}
              label="Last Name *"
              placeholder="Doe"
              error={errors.last_name?.message}
            />
          </div>

          <Input
            {...register('email')}
            label="Email *"
            type="email"
            placeholder="john@example.com"
            error={errors.email?.message}
          />

          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              {...register('phone')}
              label="Phone"
              placeholder="+91-9876543210"
            />
            <Select
              {...register('membership_type')}
              label="Membership Type *"
              placeholder="Select type"
              options={[
                { value: 'standard', label: 'Standard' },
                { value: 'premium', label: 'Premium' },
                { value: 'student', label: 'Student' },
                { value: 'senior', label: 'Senior Citizen' },
              ]}
              error={errors.membership_type?.message}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              {...register('registration_date')}
              label="Registration Date *"
              type="date"
              error={errors.registration_date?.message}
            />
            <Input
              {...register('expiry_date')}
              label="Expiry Date"
              type="date"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              {...register('date_of_birth')}
              label="Date of Birth"
              type="date"
            />
            <Select
              {...register('status')}
              label="Status *"
              placeholder="Select status"
              options={[
                { value: 'active', label: 'Active' },
                { value: 'inactive', label: 'Inactive' },
                { value: 'suspended', label: 'Suspended' },
                { value: 'expired', label: 'Expired' },
              ]}
              error={errors.status?.message}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              {...register('max_books_allowed')}
              label="Max Books Allowed *"
              type="number"
              min="1"
              max="50"
              error={errors.max_books_allowed?.message}
            />
          </div>

          <Textarea
            {...register('address')}
            label="Address"
            placeholder="Full address..."
            rows={3}
          />

          <CardFooter className="flex justify-end gap-3">
            <Button type="button" variant="outline" onClick={() => navigate('/members')}>
              Cancel
            </Button>
            <Button type="submit" loading={submitting}>
              {isEditing ? 'Update Member' : 'Register Member'}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
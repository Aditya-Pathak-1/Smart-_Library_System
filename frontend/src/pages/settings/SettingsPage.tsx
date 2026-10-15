import React, { useEffect, useState } from 'react'
import { Save, RefreshCw, Shield, Bell, Palette, Database, Users, BookOpen } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Select } from '../../components/ui/Select'
import { Textarea } from '../../components/ui/Textarea'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../../components/ui/Card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../components/ui/Tabs'
import { Switch } from '../../components/ui/Switch'
import { settingsApi } from '../../services/api'
import { toast } from 'sonner'
import type { LibrarySettings } from '../../types'
import { useAuth } from '../../contexts/AuthContext'

const settingsSchema = z.object({
  library_name: z.string().min(1, 'Library name is required').max(255),
  library_address: z.string().max(500).optional().or(z.literal('')),
  library_phone: z.string().max(20).optional().or(z.literal('')),
  library_email: z.string().email('Invalid email').optional().or(z.literal('')),
  default_borrowing_days: z.coerce.number().min(1).max(365),
  default_fine_per_day: z.coerce.number().min(0).max(1000),
  max_books_per_member: z.coerce.number().min(1).max(50),
  max_renewal_count: z.coerce.number().min(0).max(10),
  grace_period_days: z.coerce.number().min(0).max(30),
  allow_online_registration: z.boolean(),
  require_email_verification: z.boolean(),
  send_due_reminders: z.boolean(),
  reminder_days_before: z.coerce.number().min(1).max(30),
  currency_symbol: z.string().max(5),
  date_format: z.string().max(20),
  timezone: z.string().max(50),
})

type SettingsForm = z.infer<typeof settingsSchema>

const defaultSettings: SettingsForm = {
  library_name: 'Smart Library',
  library_address: '',
  library_phone: '',
  library_email: '',
  default_borrowing_days: 14,
  default_fine_per_day: 5,
  max_books_per_member: 5,
  max_renewal_count: 2,
  grace_period_days: 0,
  allow_online_registration: true,
  require_email_verification: false,
  send_due_reminders: true,
  reminder_days_before: 3,
  currency_symbol: '₹',
  date_format: 'DD/MM/YYYY',
  timezone: 'Asia/Kolkata',
}

export const SettingsPage = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isDirty },
  } = useForm<SettingsForm>({
    resolver: zodResolver(settingsSchema),
    defaultValues: defaultSettings,
  })

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await settingsApi.get()
        const settings = response.data
        reset({
          library_name: settings.library_name,
          library_address: settings.library_address || '',
          library_phone: settings.library_phone || '',
          library_email: settings.library_email || '',
          default_borrowing_days: settings.default_borrowing_days,
          default_fine_per_day: Number(settings.default_fine_per_day),
          max_books_per_member: settings.max_books_per_member,
          max_renewal_count: settings.max_renewal_count,
          grace_period_days: settings.grace_period_days,
          allow_online_registration: settings.allow_online_registration,
          require_email_verification: settings.require_email_verification,
          send_due_reminders: settings.send_due_reminders,
          reminder_days_before: settings.reminder_days_before,
          currency_symbol: settings.currency_symbol,
          date_format: settings.date_format,
          timezone: settings.timezone,
        })
      } catch (error) {
        toast.error('Failed to load settings')
      } finally {
        setLoading(false)
      }
    }
    fetchSettings()
  }, [reset])

  const onSubmit = async (data: SettingsForm) => {
    setSaving(true)
    try {
      await settingsApi.update(data)
      toast.success('Settings saved successfully')
    } catch (error) {
      toast.error('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">Configure library settings</p>
        </div>
        <Card><CardContent className="p-6 h-96"><div className="animate-pulse space-y-4"><div className="h-8 bg-muted rounded w-1/4"></div><div className="h-4 bg-muted rounded w-1/2"></div></div></CardContent></Card>
      </div>
    )
  }

  if (user?.role !== 'admin') {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">Configure library settings</p>
        </div>
        <Card>
          <CardContent className="p-6 text-center">
            <Shield className="mx-auto h-12 w-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-medium">Access Denied</h3>
            <p className="mt-2 text-muted-foreground">Only administrators can access settings.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">Configure library settings and preferences</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => reset(defaultSettings)} disabled={!isDirty}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Reset
          </Button>
          <Button onClick={handleSubmit(onSubmit)} loading={saving} disabled={!isDirty}>
            <Save className="mr-2 h-4 w-4" />
            Save Changes
          </Button>
        </div>
      </div>

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList>
          <TabsTrigger value="general">
            <Database className="mr-2 h-4 w-4" />
            General
          </TabsTrigger>
          <TabsTrigger value="circulation">
            <BookOpen className="mr-2 h-4 w-4" />
            Circulation
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="mr-2 h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="appearance">
            <Palette className="mr-2 h-4 w-4" />
            Appearance
          </TabsTrigger>
        </TabsList>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <TabsContent value="general">
            <Card>
              <CardHeader>
                <CardTitle>Library Information</CardTitle>
                <CardDescription>Basic information about your library</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input {...register('library_name')} label="Library Name *" error={errors.library_name?.message} />
                <Textarea {...register('library_address')} label="Address" placeholder="Full address" rows={3} />
                <div className="grid gap-4 sm:grid-cols-2">
                  <Input {...register('library_phone')} label="Phone" placeholder="+91-22-12345678" />
                  <Input {...register('library_email')} label="Email" type="email" placeholder="info@library.com" error={errors.library_email?.message} />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="circulation">
            <Card>
              <CardHeader>
                <CardTitle>Circulation Rules</CardTitle>
                <CardDescription>Configure borrowing and fine policies</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <Input
                    {...register('default_borrowing_days')}
                    label="Default Borrowing Period (days) *"
                    type="number"
                    min="1"
                    max="365"
                    error={errors.default_borrowing_days?.message}
                  />
                  <Input
                    {...register('default_fine_per_day')}
                    label="Fine per Day (₹) *"
                    type="number"
                    step="0.01"
                    min="0"
                    max="1000"
                    error={errors.default_fine_per_day?.message}
                  />
                  <Input
                    {...register('max_books_per_member')}
                    label="Max Books per Member *"
                    type="number"
                    min="1"
                    max="50"
                    error={errors.max_books_per_member?.message}
                  />
                  <Input
                    {...register('max_renewal_count')}
                    label="Max Renewals Allowed *"
                    type="number"
                    min="0"
                    max="10"
                    error={errors.max_renewal_count?.message}
                  />
                  <Input
                    {...register('grace_period_days')}
                    label="Grace Period (days) *"
                    type="number"
                    min="0"
                    max="30"
                    error={errors.grace_period_days?.message}
                  />
                  <Input
                    {...register('reminder_days_before')}
                    label="Reminder Days Before Due *"
                    type="number"
                    min="1"
                    max="30"
                    error={errors.reminder_days_before?.message}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notifications">
            <Card>
              <CardHeader>
                <CardTitle>Notification Settings</CardTitle>
                <CardDescription>Configure automated notifications</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Allow Online Registration</p>
                    <p className="text-sm text-muted-foreground">Allow users to register themselves online</p>
                  </div>
                  <Switch
                    checked={watch('allow_online_registration')}
                    onCheckedChange={(checked) => setValue('allow_online_registration', checked)}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Require Email Verification</p>
                    <p className="text-sm text-muted-foreground">Require email verification for new registrations</p>
                  </div>
                  <Switch
                    checked={watch('require_email_verification')}
                    onCheckedChange={(checked) => setValue('require_email_verification', checked)}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Send Due Date Reminders</p>
                    <p className="text-sm text-muted-foreground">Automatically send reminders before due date</p>
                  </div>
                  <Switch
                    checked={watch('send_due_reminders')}
                    onCheckedChange={(checked) => setValue('send_due_reminders', checked)}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="appearance">
            <Card>
              <CardHeader>
                <CardTitle>Appearance & Localization</CardTitle>
                <CardDescription>Configure display and regional settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <Select
                    {...register('currency_symbol')}
                    label="Currency Symbol *"
                    options={[
                      { value: '₹', label: '₹ Indian Rupee' },
                      { value: '$', label: '$ US Dollar' },
                      { value: '€', label: '€ Euro' },
                      { value: '£', label: '£ British Pound' },
                    ]}
                    error={errors.currency_symbol?.message}
                  />
                  <Select
                    {...register('date_format')}
                    label="Date Format *"
                    options={[
                      { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY (31/12/2024)' },
                      { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY (12/31/2024)' },
                      { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (2024-12-31)' },
                    ]}
                    error={errors.date_format?.message}
                  />
                  <Select
                    {...register('timezone')}
                    label="Timezone *"
                    options={[
                      { value: 'Asia/Kolkata', label: 'Asia/Kolkata (IST)' },
                      { value: 'UTC', label: 'UTC' },
                      { value: 'America/New_York', label: 'America/New_York (EST)' },
                      { value: 'America/Los_Angeles', label: 'America/Los_Angeles (PST)' },
                      { value: 'Europe/London', label: 'Europe/London (GMT)' },
                    ]}
                    error={errors.timezone?.message}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </form>
      </Tabs>
    </div>
  )
}
export interface User {
  id: number
  email: string
  full_name: string
  role: 'admin' | 'librarian' | 'member'
  is_active: boolean
  is_superuser: boolean
  last_login: string | null
  created_at: string
  updated_at: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Category {
  id: number
  name: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  books_count: number
}

export interface Author {
  id: number
  name: string
  biography: string | null
  birth_date: string | null
  nationality: string | null
  created_at: string
  updated_at: string
  books_count: number
}

export interface Book {
  id: number
  title: string
  isbn: string
  author_id: number
  category_id: number
  publisher: string | null
  publication_year: number | null
  shelf_location: string | null
  total_copies: number
  available_copies: number
  cover_image_url: string | null
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  author?: Author
  category?: Category
}

export interface BookCopy {
  id: number
  book_id: number
  copy_number: number
  barcode: string | null
  is_available: boolean
  condition: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface Member {
  id: number
  member_id: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  address: string | null
  date_of_birth: string | null
  membership_type: string
  registration_date: string
  expiry_date: string | null
  status: 'active' | 'inactive' | 'suspended' | 'expired'
  max_books_allowed: number
  outstanding_fines: number
  created_at: string
  updated_at: string
  user_id: number | null
  currently_issued_books?: number
  total_books_borrowed?: number
  overdue_books?: number
}

export interface IssueTransaction {
  id: number
  transaction_id: string
  member_id: number
  book_id: number
  copy_id: number | null
  issue_date: string
  due_date: string
  return_date: string | null
  status: 'issued' | 'returned' | 'overdue' | 'lost'
  fine_amount: number
  fine_paid: number
  renewed_count: number
  notes: string | null
  issued_by: number
  returned_by: number | null
  created_at: string
  updated_at: string
  member?: Member
  book?: Book
  fine?: Fine
}

export interface Fine {
  id: number
  fine_id: string
  member_id: number
  issue_id: number
  overdue_days: number
  fine_per_day: number
  calculated_amount: number
  waived_amount: number
  final_amount: number
  paid_amount: number
  status: 'pending' | 'partial' | 'paid' | 'waived'
  calculated_at: string
  finalized_at: string | null
  created_at: string
  updated_at: string
  member?: Member
  issue?: IssueTransaction
  payments?: FinePayment[]
}

export interface FinePayment {
  id: number
  payment_id: string
  fine_id: number
  amount: number
  payment_method: string
  payment_date: string
  receipt_number: string
  received_by: number
  notes: string | null
  created_at: string
  updated_at: string
  fine?: Fine
}

export interface LibrarySettings {
  id: number
  library_name: string
  library_address: string | null
  library_phone: string | null
  library_email: string | null
  default_borrowing_days: number
  default_fine_per_day: number
  max_books_per_member: number
  max_renewal_count: number
  grace_period_days: number
  allow_online_registration: boolean
  require_email_verification: boolean
  send_due_reminders: boolean
  reminder_days_before: number
  currency_symbol: string
  date_format: string
  timezone: string
  created_at: string
  updated_at: string
}

export interface DashboardStats {
  total_books: number
  available_books: number
  issued_books: number
  total_members: number
  active_members: number
  overdue_books: number
  total_outstanding_fines: number
  total_fines_collected: number
}

export interface IssueReturnChartData {
  labels: string[]
  issues: number[]
  returns: number[]
}

export interface CategoryChartData {
  labels: string[]
  values: number[]
}

export interface RecentActivityItem {
  id: number
  type: string
  description: string
  date: string
  user_name: string | null
}

export interface OverdueBookItem {
  transaction_id: string
  member_name: string
  member_id: string
  book_title: string
  book_isbn: string
  due_date: string
  overdue_days: number
  estimated_fine: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ReportFilter {
  start_date?: string
  end_date?: string
  category_id?: number
  author_id?: number
  member_id?: number
  status?: string
}
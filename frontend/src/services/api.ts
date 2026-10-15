import { api } from '../lib/api'
import type {
  Book,
  Category,
  Author,
  BookCopy,
  Member,
  IssueTransaction,
  Fine,
  FinePayment,
  LibrarySettings,
  DashboardStats,
  IssueReturnChartData,
  CategoryChartData,
  RecentActivityItem,
  OverdueBookItem,
  BookInventoryReportItem,
  IssuedBooksReportItem,
  OverdueBooksReportItem,
  MemberActivityReportItem,
  FineCollectionReportItem,
  MostBorrowedBookItem,
  PaginatedResponse,
  ReportFilter,
  Token,
  User,
} from '../types'

// Books API
export const booksApi = {
  list: (params?: {
    skip?: number
    limit?: number
    search?: string
    category_id?: number
    author_id?: number
    available_only?: boolean
    year_from?: number
    year_to?: number
    sort_by?: string
    sort_order?: string
  }) => api.get<Book[]>('/books', { params }),

  get: (id: number) => api.get<Book>(`/books/${id}`),

  create: (data: Partial<Book>) => api.post<Book>('/books', data),

  update: (id: number, data: Partial<Book>) => api.patch<Book>(`/books/${id}`, data),

  delete: (id: number) => api.delete(`/books/${id}`),

  stats: () => api.get<{ total_titles: number; total_copies: number; available_copies: number; issued_copies: number }>('/books/stats'),

  copies: {
    list: (bookId: number) => api.get<BookCopy[]>(`/books/${bookId}/copies`),
    create: (bookId: number, data: Partial<BookCopy>) => api.post<BookCopy>(`/books/${bookId}/copies`, { ...data, book_id: bookId }),
    update: (copyId: number, data: Partial<BookCopy>) => api.patch<BookCopy>(`/copies/${copyId}`, data),
    delete: (copyId: number) => api.delete(`/copies/${copyId}`),
  },
}

// Categories API
export const categoriesApi = {
  list: (params?: { skip?: number; limit?: number; active_only?: boolean }) =>
    api.get<Category[]>('/books/categories', { params }),

  get: (id: number) => api.get<Category>(`/books/categories/${id}`),

  create: (data: Partial<Category>) => api.post<Category>('/books/categories', data),

  update: (id: number, data: Partial<Category>) => api.patch<Category>(`/books/categories/${id}`, data),

  delete: (id: number) => api.delete(`/books/categories/${id}`),
}

// Authors API
export const authorsApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    api.get<Author[]>('/books/authors', { params }),

  get: (id: number) => api.get<Author>(`/books/authors/${id}`),

  create: (data: Partial<Author>) => api.post<Author>('/books/authors', data),

  update: (id: number, data: Partial<Author>) => api.patch<Author>(`/books/authors/${id}`, data),

  delete: (id: number) => api.delete(`/books/authors/${id}`),
}

// Members API
export const membersApi = {
  list: (params?: { skip?: number; limit?: number; search?: string; status?: string }) =>
    api.get<Member[]>('/members', { params }),

  get: (id: number) => api.get<Member>(`/members/${id}`),

  getDetail: (id: number) => api.get<Member & { currently_issued_books: number; total_books_borrowed: number; overdue_books: number }>(`/members/${id}`),

  create: (data: Partial<Member>) => api.post<Member>('/members', data),

  update: (id: number, data: Partial<Member>) => api.patch<Member>(`/members/${id}`, data),

  delete: (id: number) => api.delete(`/members/${id}`),

  stats: () => api.get<{ total: number; active: number; inactive: number; suspended: number }>('/members/stats'),

  history: (id: number, params?: { skip?: number; limit?: number }) =>
    api.get<IssueTransaction[]>(`/members/${id}/history`, { params }),

  profile: () => api.get<Member & { currently_issued_books: number; total_books_borrowed: number; overdue_books: number }>('/members/profile'),

  myHistory: (params?: { skip?: number; limit?: number }) =>
    api.get<IssueTransaction[]>('/members/profile/history', { params }),
}

// Issues API
export const issuesApi = {
  list: (params?: { skip?: number; limit?: number; member_id?: number; book_id?: number; status?: string; search?: string }) =>
    api.get<IssueTransaction[]>('/issues/transactions', { params }),

  get: (transactionId: string) => api.get<IssueTransaction>(`/issues/transactions/${transactionId}`),

  issue: (data: { member_id: number; book_id: number; copy_id?: number; due_date?: string; notes?: string }) =>
    api.post<IssueTransaction>('/issues/issue', data),

  return: (data: { transaction_id: string; copy_id?: number; notes?: string }) =>
    api.post<IssueTransaction>('/issues/return', data),

  renew: (transactionId: string) => api.post<IssueTransaction>(`/issues/renew/${transactionId}`),

  stats: () => api.get<{ total: number; issued: number; returned: number; overdue: number }>('/issues/transactions/stats'),

  memberTransactions: (memberId: number, params?: { skip?: number; limit?: number }) =>
    api.get<IssueTransaction[]>(`/issues/member/${memberId}/transactions`, { params }),

  updateOverdueStatus: () => api.post<{ updated: number }>('/issues/update-overdue-status'),
}

// Fines API
export const finesApi = {
  list: (params?: { skip?: number; limit?: number; member_id?: number; status?: string; search?: string }) =>
    api.get<Fine[]>('/fines/fines', { params }),

  get: (id: number) => api.get<Fine & { payments: FinePayment[]; outstanding_balance: number; is_finalized: boolean }>(`/fines/fines/${id}`),

  update: (id: number, data: Partial<Fine>) => api.patch<Fine>(`/fines/fines/${id}`, data),

  stats: () => api.get<{ total_fines: number; pending: number; partial: number; paid: number; waived: number; total_amount: number; paid_amount: number; outstanding: number; collected: number }>('/fines/fines/stats'),

  overdue: () => api.get<Array<{ transaction_id: string; member_name: string; member_id: string; book_title: string; book_isbn: string; due_date: string; overdue_days: number; estimated_fine: number; status: string }>>('/fines/fines/overdue'),

  payments: {
    record: (data: { fine_id: number; amount: number; payment_method: string; notes?: string }) =>
      api.post<FinePayment>('/fines/fines/pay', data),

    get: (paymentId: number) => api.get<FinePayment>(`/fines/fines/payments/${paymentId}`),
  },

  memberSummary: (memberId: number) => api.get<{ total_fines: number; total_amount: number; paid_amount: number; outstanding: number }>(`/fines/members/${memberId}/fines/summary`),
}

// Reports API
export const reportsApi = {
  dashboardStats: () => api.get<DashboardStats>('/reports/dashboard/stats'),

  issueReturnChart: (days?: number) => api.get<IssueReturnChartData>('/reports/dashboard/charts/issue-return', { params: { days } }),

  categoryChart: () => api.get<CategoryChartData>('/reports/dashboard/charts/categories'),

  recentActivity: (limit?: number) => api.get<RecentActivityItem[]>('/reports/dashboard/recent-activity', { params: { limit } }),

  overdueBooks: (limit?: number) => api.get<OverdueBookItem[]>('/reports/dashboard/overdue', { params: { limit } }),

  inventory: (filters?: ReportFilter) => api.get<BookInventoryReportItem[]>('/reports/reports/inventory', { params: filters }),

  issuedBooks: (filters?: ReportFilter) => api.get<IssuedBooksReportItem[]>('/reports/reports/issued', { params: filters }),

  overdueBooksReport: (filters?: ReportFilter) => api.get<OverdueBooksReportItem[]>('/reports/reports/overdue', { params: filters }),

  members: (filters?: ReportFilter) => api.get<MemberActivityReportItem[]>('/reports/reports/members', { params: filters }),

  fines: (filters?: ReportFilter) => api.get<FineCollectionReportItem[]>('/reports/reports/fines', { params: filters }),

  mostBorrowed: (limit?: number) => api.get<MostBorrowedBookItem[]>('/reports/reports/most-borrowed', { params: { limit } }),

  export: {
    inventory: (filters?: ReportFilter) => api.get('/reports/reports/inventory/export', { params: filters, responseType: 'blob' }),
    issued: (filters?: ReportFilter) => api.get('/reports/reports/issued/export', { params: filters, responseType: 'blob' }),
    overdue: (filters?: ReportFilter) => api.get('/reports/reports/overdue/export', { params: filters, responseType: 'blob' }),
    fines: (filters?: ReportFilter) => api.get('/reports/reports/fines/export', { params: filters, responseType: 'blob' }),
  },
}

// Settings API
export const settingsApi = {
  get: () => api.get<LibrarySettings>('/settings/settings'),

  update: (data: Partial<LibrarySettings>) => api.patch<LibrarySettings>('/settings/settings', data),
}

// Auth API
export const authApi = {
  login: (email: string, password: string) => api.post<Token>('/auth/login', { email, password }),

  register: (data: { email: string; password: string; full_name: string; role?: string }) => api.post('/auth/register', data),

  refresh: (refresh_token: string) => api.post<Token>('/auth/refresh', { refresh_token }),

  me: () => api.get<User>('/auth/me'),

  impersonate: (userId: number) => api.post<Token>(`/auth/impersonate/${userId}`),

  users: {
    list: (params?: { skip?: number; limit?: number; role?: string }) => api.get<User[]>('/auth/users', { params }),

    get: (id: number) => api.get<User>(`/auth/users/${id}`),

    update: (id: number, data: any) => api.patch(`/auth/users/${id}`, data),

    delete: (id: number) => api.delete(`/auth/users/${id}`),
  },
}
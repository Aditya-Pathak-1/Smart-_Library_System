import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { MainLayout } from './components/layout/MainLayout'
import { LoginPage, RegisterPage, ProfilePage } from './pages/auth'
import { DashboardPage } from './pages/dashboard'
import { BooksPage, BookDetailPage, BookFormPage } from './pages/books'
import { MembersPage, MemberDetailPage, MemberFormPage } from './pages/members'
import { IssuesPage } from './pages/issues'
import { FinesPage } from './pages/fines'
import { ReportsPage } from './pages/reports'
import { SettingsPage } from './pages/settings'
import { useAuth } from './contexts/AuthContext'

const ProtectedRoute = ({ children, allowedRoles }: { children: React.ReactNode; allowedRoles?: string[] }) => {
  const { isAuthenticated, isLoading, user } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

const App = () => {
  return (
    <Routes>
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
      
      <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        
        <Route path="/books" element={<ProtectedRoute><BooksPage /></ProtectedRoute>} />
        <Route path="/books/new" element={<ProtectedRoute allowedRoles={['admin', 'librarian']}><BookFormPage /></ProtectedRoute>} />
        <Route path="/books/:id" element={<ProtectedRoute><BookDetailPage /></ProtectedRoute>} />
        <Route path="/books/:id/edit" element={<ProtectedRoute allowedRoles={['admin', 'librarian']}><BookFormPage /></ProtectedRoute>} />
        
        <Route path="/members" element={<ProtectedRoute allowedRoles={['admin', 'librarian']}><MembersPage /></ProtectedRoute>} />
        <Route path="/members/new" element={<ProtectedRoute allowedRoles={['admin', 'librarian']}><MemberFormPage /></ProtectedRoute>} />
        <Route path="/members/:id" element={<ProtectedRoute allowedRoles={['admin', 'librarian']}><MemberDetailPage /></ProtectedRoute>} />
        <Route path="/members/:id/edit" element={<ProtectedRoute allowedRoles={['admin', 'librarian']}><MemberFormPage /></ProtectedRoute>} />
        
        <Route path="/issues" element={<ProtectedRoute allowedRoles={['admin', 'librarian']}><IssuesPage /></ProtectedRoute>} />
        
        <Route path="/fines" element={<ProtectedRoute allowedRoles={['admin', 'librarian']}><FinesPage /></ProtectedRoute>} />
        
        <Route path="/reports" element={<ProtectedRoute allowedRoles={['admin', 'librarian']}><ReportsPage /></ProtectedRoute>} />
        
        <Route path="/settings" element={<ProtectedRoute allowedRoles={['admin']}><SettingsPage /></ProtectedRoute>} />
      </Route>

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
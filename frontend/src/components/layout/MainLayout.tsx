import React from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Navbar } from './Navbar'
import { cn } from '../../lib/utils'
import { useAuth } from '../../contexts/AuthContext'
import { handleApiError } from '../../lib/api'

export const MainLayout = () => {
  const { user, isImpersonating, returnToAdmin } = useAuth()
  const [returnError, setReturnError] = React.useState('')

  const handleReturnToAdmin = async () => {
    setReturnError('')
    try {
      await returnToAdmin()
    } catch (error) {
      setReturnError(handleApiError(error))
    }
  }

  const viewedRole = user?.role === 'librarian' ? 'Staff (Librarian)' : 'Member'

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div className={cn('transition-all duration-300', 'lg:pl-64')}>
        <Navbar />
        {isImpersonating && (
          <div className="mx-4 mt-4 flex flex-col gap-3 rounded-lg border border-amber-500/40 bg-amber-500/10 p-4 text-amber-950 dark:text-amber-100 sm:mx-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-medium">You are viewing the system as {user?.full_name} ({viewedRole}).</p>
              <p className="text-sm opacity-80">Administrator access is disabled until you return to your account.</p>
              {returnError && <p className="mt-1 text-sm font-medium" role="alert">{returnError}</p>}
            </div>
            <button
              type="button"
              className="shrink-0 rounded-md border border-current px-3 py-2 text-sm font-medium hover:bg-amber-500/10"
              onClick={handleReturnToAdmin}
            >
              Return to administrator
            </button>
          </div>
        )}
        <main className="p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
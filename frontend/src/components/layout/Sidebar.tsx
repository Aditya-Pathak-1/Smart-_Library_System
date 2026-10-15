import { useEffect, useState } from 'react'
import { Link, useLocation, NavLink, useNavigate } from 'react-router-dom'
import { cn } from '../../lib/utils'
import {
  LayoutDashboard,
  Book,
  Users,
  ArrowRightLeft,
  AlertTriangle,
  BarChart3,
  Settings,
  Menu,
  ChevronRight,
  ChevronDown,
  LogOut,
  User,
  UserRoundCog,
} from 'lucide-react'
import { Avatar } from '../ui/Avatar'
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from '../ui/DropdownMenu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../ui/Dialog'
import { Input } from '../ui/Input'
import { useAuth } from '../../contexts/AuthContext'
import { authApi } from '../../services/api'
import { handleApiError } from '../../lib/api'
import type { User as LibraryUser } from '../../types'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, roles: ['admin', 'librarian', 'member'] },
  { name: 'Books', href: '/books', icon: Book, roles: ['admin', 'librarian', 'member'] },
  { name: 'Members', href: '/members', icon: Users, roles: ['admin', 'librarian'] },
  { name: 'Issue/Return', href: '/issues', icon: ArrowRightLeft, roles: ['admin', 'librarian'] },
  { name: 'Fines', href: '/fines', icon: AlertTriangle, roles: ['admin', 'librarian'] },
  { name: 'Reports', href: '/reports', icon: BarChart3, roles: ['admin', 'librarian'] },
  { name: 'Settings', href: '/settings', icon: Settings, roles: ['admin'] },
]

const roleLabel = (role: LibraryUser['role']) =>
  role === 'admin' ? 'Administrator' : role === 'librarian' ? 'Staff (Librarian)' : 'Member'

export const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [switchDialogOpen, setSwitchDialogOpen] = useState(false)
  const [switchUsers, setSwitchUsers] = useState<LibraryUser[]>([])
  const [switchSearch, setSwitchSearch] = useState('')
  const [switchLoading, setSwitchLoading] = useState(false)
  const [switchingUserId, setSwitchingUserId] = useState<number | null>(null)
  const [switchError, setSwitchError] = useState('')
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout, impersonateUser } = useAuth()

  const filteredNavigation = navigation.filter((item) =>
    user ? item.roles.includes(user.role) : false
  )

  useEffect(() => {
    if (!switchDialogOpen || user?.role !== 'admin') return

    let cancelled = false
    const loadUsers = async () => {
      setSwitchLoading(true)
      setSwitchError('')
      try {
        const response = await authApi.users.list({ skip: 0, limit: 200 })
        if (!cancelled) {
          setSwitchUsers(response.data.filter((account) => account.is_active && account.role !== 'admin'))
        }
      } catch (error) {
        if (!cancelled) setSwitchError(handleApiError(error))
      } finally {
        if (!cancelled) setSwitchLoading(false)
      }
    }

    loadUsers()
    return () => {
      cancelled = true
    }
  }, [switchDialogOpen, user?.role])

  const visibleSwitchUsers = switchUsers.filter((account) => {
    const search = switchSearch.trim().toLowerCase()
    return !search
      || account.full_name.toLowerCase().includes(search)
      || account.email.toLowerCase().includes(search)
  })

  const handleImpersonate = async (account: LibraryUser) => {
    setSwitchingUserId(account.id)
    setSwitchError('')
    try {
      await impersonateUser(account.id)
      setSwitchDialogOpen(false)
      setMobileOpen(false)
      navigate('/dashboard', { replace: true })
    } catch (error) {
      setSwitchError(handleApiError(error))
    } finally {
      setSwitchingUserId(null)
    }
  }

  return (
    <>
      <button
        className="fixed top-4 left-4 z-50 lg:hidden btn-ghost btn-icon"
        onClick={() => setMobileOpen(true)}
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-screen border-r bg-card transition-all duration-300 ease-in-out flex flex-col',
          collapsed ? 'w-16' : 'w-64',
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        <div className="flex h-16 items-center justify-between px-4 border-b">
          {!collapsed && (
            <Link to="/dashboard" className="flex items-center gap-2 font-semibold text-lg text-primary">
              <Book className="h-6 w-6" />
              <span>Smart Library</span>
            </Link>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className={cn('btn-ghost btn-icon', collapsed && 'ml-auto')}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <ChevronRight className={cn('h-5 w-5 transition-transform', collapsed && 'rotate-180')} />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-4 space-y-1" aria-label="Main navigation">
          {filteredNavigation.map((item) => {
            const isActive = location.pathname === item.href || location.pathname.startsWith(item.href + '/')
            return (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
                  collapsed && 'justify-center'
                )}
                title={collapsed ? item.name : undefined}
                aria-current={isActive ? 'page' : undefined}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                {!collapsed && <span>{item.name}</span>}
              </NavLink>
            )
          })}
        </nav>

        <div className="border-t p-3">
          {user && (
            <DropdownMenu className="block w-full">
              <DropdownMenuTrigger asChild>
                <button
                  className="flex w-full min-w-0 items-center gap-3 rounded-lg px-2 py-2 text-left transition-colors hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  title={collapsed ? `${user.full_name} — ${roleLabel(user.role)}` : undefined}
                  aria-label={`Account: ${user.full_name}, ${roleLabel(user.role)}`}
                >
                  <Avatar src={null} fallback={user.full_name} size="md" />
                  {!collapsed && (
                    <>
                      <span className="min-w-0 flex-1">
                        <span className="block break-words text-sm font-medium leading-tight">{user.full_name}</span>
                        <span className="block break-words text-xs text-muted-foreground">{roleLabel(user.role)}</span>
                      </span>
                      <ChevronDown className="h-4 w-4 flex-shrink-0 text-muted-foreground" aria-hidden="true" />
                    </>
                  )}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="bottom-full left-0 right-auto top-auto mb-2 w-60">
                <DropdownMenuLabel className="font-normal">
                  <span className="block truncate text-sm font-medium">{user.full_name}</span>
                  <span className="block truncate text-xs text-muted-foreground">{roleLabel(user.role)}</span>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                {user.role === 'admin' && (
                  <DropdownMenuItem onClick={() => {
                    setSwitchSearch('')
                    setSwitchError('')
                    setSwitchDialogOpen(true)
                  }}>
                    <UserRoundCog className="mr-2 h-4 w-4" aria-hidden="true" />
                    Switch account
                  </DropdownMenuItem>
                )}
                <DropdownMenuItem asChild>
                  <Link to="/profile" className="w-full" onClick={() => setMobileOpen(false)}>
                    <User className="mr-2 h-4 w-4" aria-hidden="true" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout} className="text-destructive focus:text-destructive">
                  <LogOut className="mr-2 h-4 w-4" aria-hidden="true" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </aside>

      <Dialog open={switchDialogOpen} onOpenChange={setSwitchDialogOpen}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle>Switch account</DialogTitle>
            <DialogDescription>
              Temporarily view the system as an active member or staff account. You can return to your administrator account at any time.
            </DialogDescription>
          </DialogHeader>
          <Input
            value={switchSearch}
            onChange={(event) => setSwitchSearch(event.target.value)}
            placeholder="Find an account by name or email"
            aria-label="Find an account by name or email"
          />
          {switchError && (
            <p className="rounded-md border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive" role="alert">
              {switchError}
            </p>
          )}
          <div className="max-h-72 space-y-2 overflow-y-auto">
            {switchLoading ? (
              <p className="py-6 text-center text-sm text-muted-foreground">Loading accounts...</p>
            ) : visibleSwitchUsers.length === 0 ? (
              <p className="py-6 text-center text-sm text-muted-foreground">
                {switchUsers.length === 0 ? 'No active member or staff accounts found.' : 'No accounts match your search.'}
              </p>
            ) : (
              visibleSwitchUsers.map((account) => (
                <div key={account.id} className="flex items-center gap-3 rounded-md border p-3">
                  <Avatar src={null} fallback={account.full_name} size="sm" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{account.full_name}</p>
                    <p className="truncate text-xs text-muted-foreground">{account.email}</p>
                  </div>
                  <span className="shrink-0 text-xs text-muted-foreground">{roleLabel(account.role)}</span>
                  <button
                    type="button"
                    className="shrink-0 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
                    onClick={() => handleImpersonate(account)}
                    disabled={switchingUserId !== null}
                  >
                    {switchingUserId === account.id ? 'Switching…' : 'View as'}
                  </button>
                </div>
              ))
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

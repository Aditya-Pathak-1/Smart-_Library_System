import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, Sun, Moon } from 'lucide-react'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuLabel } from '../ui/DropdownMenu'
import { Avatar } from '../ui/Avatar'
import { useAuth } from '../../contexts/AuthContext'
import { useTheme } from '../../contexts/ThemeContext'

export const Navbar = () => {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const [search, setSearch] = useState('')

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const query = search.trim()
    navigate(query ? `/books?search=${encodeURIComponent(query)}` : '/books')
  }

  return (
    <header className="sticky top-0 z-40 h-16 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-full items-center gap-4 px-4 lg:px-6">
        <Link to="/dashboard" className="flex items-center gap-2 font-semibold text-lg text-primary">
          <span className="hidden sm:block">Smart Library</span>
        </Link>

        <div className="flex-1 max-w-xl hidden md:block">
          <form className="relative" onSubmit={submitSearch}>
            <button
              type="submit"
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              aria-label="Search books"
            >
              <Search className="h-4 w-4" aria-hidden="true" />
            </button>
            <Input
              placeholder="Search books by title, author, or ISBN..."
              className="pl-10 w-full"
              aria-label="Search books by title, author, or ISBN"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </form>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <Avatar
                  src={null}
                  fallback={user?.full_name || 'U'}
                  size="sm"
                />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="font-medium text-sm">{user?.full_name}</p>
                  <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link to="/profile" className="flex items-center w-full">
                  <span className="mr-2">Profile</span>
                </Link>
              </DropdownMenuItem>
              {user?.role === 'admin' && (
                <DropdownMenuItem asChild>
                  <Link to="/settings" className="flex items-center w-full">
                    <span className="mr-2">Settings</span>
                  </Link>
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout} className="text-destructive focus:text-destructive">
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
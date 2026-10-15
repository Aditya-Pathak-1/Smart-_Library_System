import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { api } from '../lib/api'
import { User, Token } from '../types'

interface AuthContextType {
  user: User | null
  token: string | null
  refreshToken: string | null
  isLoading: boolean
  isAuthenticated: boolean
  isImpersonating: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
  impersonateUser: (userId: number) => Promise<void>
  returnToAdmin: () => Promise<void>
}

interface RegisterData {
  email: string
  password: string
  full_name: string
  role?: 'admin' | 'librarian' | 'member'
}

let authToken: string | null = null

export const getAuthToken = () =>
  authToken ?? localStorage.getItem('access_token')

export const setAuthToken = (newToken: string, newRefreshToken?: string) => {
  authToken = newToken
  localStorage.setItem('access_token', newToken)
  if (newRefreshToken) {
    localStorage.setItem('refresh_token', newRefreshToken)
  }
}

export const clearAuth = () => {
  authToken = null
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('admin_access_token')
  localStorage.removeItem('admin_refresh_token')
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setTokenState] = useState<string | null>(null)
  const [refreshToken, setRefreshTokenState] = useState<string | null>(null)
  const [isImpersonating, setIsImpersonating] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  const clearAuthState = () => {
    setUser(null)
    setTokenState(null)
    setRefreshTokenState(null)
    setIsImpersonating(false)
    clearAuth()
  }

  const refreshUser = async () => {
    if (!token && !getAuthToken()) return
    try {
      const response = await api.get<User>('/auth/me')
      setUser(response.data)
    } catch (error) {
      clearAuthState()
      throw error
    }
  }

  const login = async (email: string, password: string) => {
    const response = await api.post<Token>('/auth/login', { email, password })
    const { access_token, refresh_token } = response.data
    setAuthToken(access_token, refresh_token)
    setTokenState(access_token)
    setRefreshTokenState(refresh_token)
    await refreshUser()
  }

  const register = async (data: RegisterData) => {
    const response = await api.post<User>('/auth/register', data)
    setUser(response.data)
  }

  const logout = () => {
    clearAuthState()
  }

  const impersonateUser = async (userId: number) => {
    if (user?.role !== 'admin' || isImpersonating) {
      throw new Error('Only administrators can start an impersonation session')
    }

    const response = await api.post<Token>(`/auth/impersonate/${userId}`)
    const adminAccessToken = getAuthToken()
    const adminRefreshToken = localStorage.getItem('refresh_token')
    if (!adminAccessToken || !adminRefreshToken) {
      throw new Error('The administrator session could not be preserved')
    }

    localStorage.setItem('admin_access_token', adminAccessToken)
    localStorage.setItem('admin_refresh_token', adminRefreshToken)
    setAuthToken(response.data.access_token, response.data.refresh_token)
    setTokenState(response.data.access_token)
    setRefreshTokenState(response.data.refresh_token)
    setIsImpersonating(true)
    await refreshUser()
  }

  const returnToAdmin = async () => {
    const adminAccessToken = localStorage.getItem('admin_access_token')
    const adminRefreshToken = localStorage.getItem('admin_refresh_token')
    if (!adminAccessToken || !adminRefreshToken) {
      clearAuthState()
      throw new Error('The administrator session is no longer available')
    }

    setAuthToken(adminAccessToken, adminRefreshToken)
    localStorage.removeItem('admin_access_token')
    localStorage.removeItem('admin_refresh_token')
    setTokenState(adminAccessToken)
    setRefreshTokenState(adminRefreshToken)
    setIsImpersonating(false)
    await refreshUser()
  }

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('access_token')
      const storedRefreshToken = localStorage.getItem('refresh_token')
      const storedAdminToken = localStorage.getItem('admin_access_token')
      const storedAdminRefreshToken = localStorage.getItem('admin_refresh_token')

      if (storedToken && storedRefreshToken) {
        setTokenState(storedToken)
        setRefreshTokenState(storedRefreshToken)
        setIsImpersonating(!!storedAdminToken && !!storedAdminRefreshToken)
        try {
          setAuthToken(storedToken, storedRefreshToken)
          await refreshUser()
        } catch {
          clearAuthState()
        }
      }
      setIsLoading(false)
    }

    initAuth()
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        refreshToken,
        isLoading,
        isAuthenticated: !!user && !!token,
        isImpersonating,
        login,
        register,
        logout,
        refreshUser,
        impersonateUser,
        returnToAdmin,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

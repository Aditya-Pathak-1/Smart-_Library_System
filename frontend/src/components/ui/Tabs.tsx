import React, { useState } from 'react'
import { cn } from '../../lib/utils'

interface TabsProps {
  defaultValue?: string
  value?: string
  onValueChange?: (value: string) => void
  children: React.ReactNode
  className?: string
}

const TabsContext = React.createContext<{
  value: string
  onValueChange?: (value: string) => void
} | null>(null)

const Tabs = ({ defaultValue, value: controlledValue, onValueChange, children, className }: TabsProps) => {
  const [uncontrolledValue, setUncontrolledValue] = useState(defaultValue ?? '')
  const value = controlledValue ?? uncontrolledValue

  const handleValueChange = (newValue: string) => {
    if (controlledValue === undefined) setUncontrolledValue(newValue)
    onValueChange?.(newValue)
  }

  return (
    <TabsContext.Provider value={{ value, onValueChange: handleValueChange }}>
      <div className={cn(className)}>{children}</div>
    </TabsContext.Provider>
  )
}

Tabs.displayName = 'Tabs'

interface TabsListProps {
  children: React.ReactNode
  className?: string
}

const TabsList = ({ children, className }: TabsListProps) => {
  return (
    <div
      className={cn(
        'inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground',
        className
      )}
      role="tablist"
    >
      {children}
    </div>
  )
}

TabsList.displayName = 'TabsList'

interface TabsTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value: string
}

const TabsTrigger = React.forwardRef<HTMLButtonElement, TabsTriggerProps>(
  ({ className, value, children, onClick, ...props }, ref) => {
    const context = React.useContext(TabsContext)
    if (!context) throw new Error('TabsTrigger must be used within Tabs')

    const { value: currentValue, onValueChange: contextOnValueChange } = context
    const isActive = currentValue === value

    return (
      <button
        ref={ref}
        role="tab"
        aria-selected={isActive}
        className={cn(
          'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm',
          isActive ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground',
          className
        )}
        onClick={(event) => {
          onClick?.(event)
          if (!event.defaultPrevented) contextOnValueChange?.(value)
        }}
        {...props}
      >
        {children}
      </button>
    )
  }
)

TabsTrigger.displayName = 'TabsTrigger'

interface TabsContentProps {
  value: string
  children: React.ReactNode
  className?: string
}

const TabsContent = ({ value, children, className }: TabsContentProps) => {
  const context = React.useContext(TabsContext)
  if (!context) throw new Error('TabsContent must be used within Tabs')

  const { value: currentValue } = context
  const isActive = currentValue === value

  if (!isActive) return null

  return (
    <div
      role="tabpanel"
      className={cn(
        'mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        className
      )}
    >
      {children}
    </div>
  )
}

TabsContent.displayName = 'TabsContent'

export { Tabs, TabsList, TabsTrigger, TabsContent }
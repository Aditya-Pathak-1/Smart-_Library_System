import React, { createContext, useContext, useEffect, useRef, useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from '../../lib/utils'

interface DropdownMenuContextValue {
  open: boolean
  setOpen: (open: boolean) => void
  rootRef: React.RefObject<HTMLDivElement>
}

interface DropdownMenuChildProps extends React.HTMLAttributes<HTMLElement> {
  className?: string
  onClick?: React.MouseEventHandler<HTMLElement>
}

const DropdownMenuContext = createContext<DropdownMenuContextValue | null>(null)

const useDropdownMenu = () => {
  const context = useContext(DropdownMenuContext)
  if (!context) {
    throw new Error('Dropdown menu components must be used inside DropdownMenu')
  }
  return context
}

interface DropdownMenuProps {
  children: React.ReactNode
  className?: string
}

const DropdownMenu = ({ children, className }: DropdownMenuProps) => {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return

    const closeOnOutsideClick = (event: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false)
    }

    document.addEventListener('mousedown', closeOnOutsideClick)
    document.addEventListener('keydown', closeOnEscape)
    return () => {
      document.removeEventListener('mousedown', closeOnOutsideClick)
      document.removeEventListener('keydown', closeOnEscape)
    }
  }, [open])

  return (
    <DropdownMenuContext.Provider value={{ open, setOpen, rootRef }}>
      <div ref={rootRef} className={cn('relative inline-block', className)}>
        {children}
      </div>
    </DropdownMenuContext.Provider>
  )
}

interface DropdownMenuTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactElement | React.ReactNode
  asChild?: boolean
}

const DropdownMenuTrigger = ({
  children,
  className,
  asChild,
  onClick,
  ...props
}: DropdownMenuTriggerProps) => {
  const { open, setOpen } = useDropdownMenu()
  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    onClick?.(event as React.MouseEvent<HTMLButtonElement>)
    if (!event.defaultPrevented) setOpen(!open)
  }

  if (asChild && React.isValidElement<DropdownMenuChildProps>(children)) {
    return React.cloneElement(children, {
      ...props,
      className: cn(children.props.className, className),
      onClick: (event: React.MouseEvent<HTMLElement>) => {
        children.props.onClick?.(event)
        handleClick(event)
      },
      'aria-haspopup': 'menu',
      'aria-expanded': open,
    })
  }

  return (
    <button
      type="button"
      className={cn(
        'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2',
        className
      )}
      onClick={handleClick}
      aria-haspopup="menu"
      aria-expanded={open}
      {...props}
    >
      {children}
      <ChevronDown className="ml-2 h-4 w-4" aria-hidden="true" />
    </button>
  )
}

DropdownMenuTrigger.displayName = 'DropdownMenuTrigger'

interface DropdownMenuContentProps {
  children: React.ReactNode
  className?: string
  align?: 'start' | 'center' | 'end'
}

const DropdownMenuContent = ({ children, className, align = 'end' }: DropdownMenuContentProps) => {
  const { open } = useDropdownMenu()
  if (!open) return null

  return (
    <div
      className={cn(
        'absolute top-full z-50 mt-2 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md focus:outline-none',
        align === 'start' && 'left-0',
        align === 'center' && 'left-1/2 -translate-x-1/2',
        align === 'end' && 'right-0',
        className
      )}
      role="menu"
    >
      {children}
    </div>
  )
}

DropdownMenuContent.displayName = 'DropdownMenuContent'

interface DropdownMenuItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  inset?: boolean
  disabled?: boolean
  asChild?: boolean
}

const DropdownMenuItem = React.forwardRef<HTMLButtonElement, DropdownMenuItemProps>(
  ({ className, inset, disabled, children, onClick, asChild, ...props }, ref) => {
    const { setOpen } = useDropdownMenu()
    const itemClassName = cn(
      'relative flex w-full cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground disabled:pointer-events-none disabled:opacity-50',
      inset && 'pl-8',
      className
    )

    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
      if (disabled) {
        event.preventDefault()
        return
      }
      onClick?.(event as React.MouseEvent<HTMLButtonElement>)
      if (!event.defaultPrevented) setOpen(false)
    }

    if (asChild && React.isValidElement<DropdownMenuChildProps>(children)) {
      return React.cloneElement(children, {
        ...props,
        className: cn(itemClassName, children.props.className),
        onClick: (event: React.MouseEvent<HTMLElement>) => {
          children.props.onClick?.(event)
          handleClick(event)
        },
        role: 'menuitem',
        'aria-disabled': disabled || undefined,
      })
    }

    return (
      <button
        ref={ref}
        type="button"
        className={itemClassName}
        onClick={handleClick}
        disabled={disabled}
        role="menuitem"
        {...props}
      >
        {children}
      </button>
    )
  }
)

DropdownMenuItem.displayName = 'DropdownMenuItem'

interface DropdownMenuSeparatorProps extends React.HTMLAttributes<HTMLDivElement> {}

const DropdownMenuSeparator = React.forwardRef<HTMLDivElement, DropdownMenuSeparatorProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('-mx-1 my-1 h-px bg-muted', className)}
      role="separator"
      {...props}
    />
  )
)

DropdownMenuSeparator.displayName = 'DropdownMenuSeparator'

interface DropdownMenuLabelProps extends React.HTMLAttributes<HTMLDivElement> {
  inset?: boolean
}

const DropdownMenuLabel = React.forwardRef<HTMLDivElement, DropdownMenuLabelProps>(
  ({ className, inset, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('px-2 py-1.5 text-sm font-semibold', inset && 'pl-8', className)}
      {...props}
    >
      {children}
    </div>
  )
)

DropdownMenuLabel.displayName = 'DropdownMenuLabel'

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
}

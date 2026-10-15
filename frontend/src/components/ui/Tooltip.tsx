import React, { useState, useRef, useEffect } from 'react'
import { cn } from '../../lib/utils'

interface TooltipProps {
  content: React.ReactNode
  children: React.ReactElement
  side?: 'top' | 'bottom' | 'left' | 'right'
  delayDuration?: number
}

const Tooltip = ({ content, children, side = 'top', delayDuration = 200 }: TooltipProps) => {
  const [open, setOpen] = useState(false)
  const timeoutRef = useRef<NodeJS.Timeout>()
  const childRef = useRef<HTMLElement>()

  const showTooltip = () => {
    timeoutRef.current = setTimeout(() => setOpen(true), delayDuration)
  }

  const hideTooltip = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    setOpen(false)
  }

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [])

  const sideClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  }

  const arrowClasses = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-background',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-background',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-background',
    right: 'right-full top-1/2 -translate-y-1/2 border-r-background',
  }

  return (
    <div className="relative inline-block" onMouseEnter={showTooltip} onMouseLeave={hideTooltip} onFocus={showTooltip} onBlur={hideTooltip}>
      {React.cloneElement(children, { ref: childRef })}
      {open && (
        <div
          className={cn(
            'absolute z-50 px-3 py-1.5 text-sm text-popover-foreground bg-popover rounded-md shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95',
            sideClasses[side]
          )}
          role="tooltip"
        >
          {content}
          <div
            className={cn(
              'absolute w-0 h-0 border-4 border-transparent',
              arrowClasses[side]
            )}
          />
        </div>
      )}
    </div>
  )
}

Tooltip.displayName = 'Tooltip'

export { Tooltip }
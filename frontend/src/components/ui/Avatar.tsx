import React from 'react'
import { cn } from '../../lib/utils'
import { getInitials } from '../../lib/utils'

interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string | null
  alt?: string
  fallback?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  ({ className, src, alt, fallback, size = 'md', ...props }, ref) => {
    const sizes = {
      sm: 'h-8 w-8 text-xs',
      md: 'h-10 w-10 text-sm',
      lg: 'h-12 w-12 text-base',
      xl: 'h-16 w-16 text-lg',
    }

    const [imageError, setImageError] = React.useState(false)

    if (src && !imageError) {
      return (
        <div
          ref={ref}
          className={cn('relative flex shrink-0 overflow-hidden rounded-full', sizes[size], className)}
          {...props}
        >
          <img
            src={src}
            alt={alt || fallback || 'Avatar'}
            className="aspect-square h-full w-full object-cover"
            onError={() => setImageError(true)}
          />
        </div>
      )
    }

    return (
      <div
        ref={ref}
        className={cn(
          'relative flex shrink-0 overflow-hidden rounded-full bg-muted flex items-center justify-center font-medium',
          sizes[size],
          className
        )}
        {...props}
      >
        {fallback ? getInitials(fallback) : '?'}
      </div>
    )
  }
)

Avatar.displayName = 'Avatar'

export { Avatar }
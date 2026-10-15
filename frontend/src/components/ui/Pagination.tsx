import React from 'react'
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react'
import { cn } from '../../lib/utils'
import { Button } from './Button'

interface PaginationProps {
  page: number
  totalPages: number
  onPageChange: (page: number) => void
  className?: string
  showTotal?: boolean
  total?: number
}

const Pagination = ({ page, totalPages, onPageChange, className, showTotal, total }: PaginationProps) => {
  if (totalPages <= 1) return null

  const pages = React.useMemo(() => {
    const result: (number | string)[] = []
    const showPages = 5
    const half = Math.floor(showPages / 2)

    let start = Math.max(1, page - half)
    let end = Math.min(totalPages, start + showPages - 1)

    if (end - start + 1 < showPages) {
      start = Math.max(1, end - showPages + 1)
    }

    if (start > 1) {
      result.push(1)
      if (start > 2) result.push('...')
    }

    for (let i = start; i <= end; i++) {
      result.push(i)
    }

    if (end < totalPages) {
      if (end < totalPages - 1) result.push('...')
      result.push(totalPages)
    }

    return result
  }, [page, totalPages])

  return (
    <nav className={cn('flex items-center justify-center gap-1', className)} aria-label="Pagination">
      {showTotal && total && (
        <span className="text-sm text-muted-foreground mr-2">
          Showing {((page - 1) * 20) + 1} to {Math.min(page * 20, total)} of {total} results
        </span>
      )}
      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(1)}
        disabled={page === 1}
        aria-label="First page"
      >
        <ChevronsLeft className="h-4 w-4" />
      </Button>
      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(page - 1)}
        disabled={page === 1}
        aria-label="Previous page"
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>
      <div className="flex items-center gap-1">
        {pages.map((p, i) =>
          p === '...' ? (
            <span key={`ellipsis-${i}`} className="px-2 text-muted-foreground">...</span>
          ) : (
            <Button
              key={p}
              variant={page === p ? 'primary' : 'outline'}
              size="icon"
              onClick={() => onPageChange(p as number)}
              aria-label={`Page ${p}`}
              aria-current={page === p ? 'page' : undefined}
            >
              {p}
            </Button>
          )
        )}
      </div>
      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(page + 1)}
        disabled={page === totalPages}
        aria-label="Next page"
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(totalPages)}
        disabled={page === totalPages}
        aria-label="Last page"
      >
        <ChevronsRight className="h-4 w-4" />
      </Button>
    </nav>
  )
}

Pagination.displayName = 'Pagination'

export { Pagination }
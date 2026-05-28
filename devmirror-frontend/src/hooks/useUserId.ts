import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getUserId, setUserId } from '../api/client'

/**
 * Returns the current user's numeric ID.
 * Priority: ?user_id= URL param (from OAuth callback) ? localStorage.
 * Persists any URL param value to localStorage for subsequent visits.
 */
export function useUserId(): number | null {
  const [userId, setUserIdState] = useState<number | null>(getUserId)
  const [searchParams, setSearchParams] = useSearchParams()

  useEffect(() => {
    const fromUrl = searchParams.get('user_id')
    if (fromUrl) {
      const id = parseInt(fromUrl, 10)
      if (!isNaN(id)) {
        setUserId(id)
        setUserIdState(id)
        // Remove user_id from URL to keep it clean
        setSearchParams(prev => {
          const next = new URLSearchParams(prev)
          next.delete('user_id')
          return next
        }, { replace: true })
      }
    }
  }, [searchParams, setSearchParams])

  return userId
}

import { Suspense } from 'react'
import SystemStatusBarClient from './SystemStatusBarClient'

async function fetchStatus() {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/status`, {
      next: { revalidate: 30 },
      // Use a short timeout so cold-starts don't block the HTML render for too long
      signal: AbortSignal.timeout(2000)
    })
    if (!res.ok) return null
    return await res.json()
  } catch (error) {
    return null
  }
}

export default async function SystemStatusBar() {
  const initialStatus = await fetchStatus()
  
  return (
    <Suspense fallback={<SystemStatusBarClient initialData={null} />}>
      <SystemStatusBarClient initialData={initialStatus} />
    </Suspense>
  )
}

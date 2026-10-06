import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import SystemStatusBar from '@/components/layout/SystemStatusBar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ORCA | Live Marine Intelligence for Fishermen',
  description: 'Live, evidence-backed fishing zone and marine safety advisory using official ocean and weather APIs and a 10-agent AI pipeline.',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <SystemStatusBar />
          {children}
        </Providers>
      </body>
    </html>
  )
}

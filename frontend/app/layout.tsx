import './globals.css'
import type { Metadata } from 'next'
import { ThemeProvider } from '@/components/theme-provider'
import { Navbar } from '@/components/navbar'
import { ModeSwitcher } from '@/components/mode-switcher'
import { StoreInitializer } from '@/components/store-initializer'

export const metadata: Metadata = {
  title: 'Linker - Smart Matching Platform',
  description: 'Connect with the perfect partner through AI-powered matching',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <StoreInitializer />
        <ThemeProvider>
          <div className="min-h-screen bg-background">
            <Navbar />
            <main className="container mx-auto px-4 py-8">
              {children}
            </main>
            <ModeSwitcher />
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
} 
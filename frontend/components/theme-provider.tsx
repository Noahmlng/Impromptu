'use client'

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes/dist/types"
import { useAppStore } from "@/lib/store"

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  const { themeMode, isDarkMode } = useAppStore()
  
  React.useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove('theme-romantic', 'theme-team')
    root.classList.add(`theme-${themeMode}`)
  }, [themeMode])

  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="light"
      enableSystem
      {...props}
    >
      {children}
    </NextThemesProvider>
  )
} 
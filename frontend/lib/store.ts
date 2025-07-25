import { create } from 'zustand'
import { AppState, User, ThemeMode, Language } from './types'

export const useAppStore = create<AppState>((set) => ({
  themeMode: 'romantic',
  isDarkMode: false,
  language: 'en',
  user: null,
  setThemeMode: (mode) => set({ themeMode: mode }),
  setIsDarkMode: (isDark) => set({ isDarkMode: isDark }),
  setLanguage: (lang) => set({ language: lang }),
  setUser: (user) => set({ user }),
})) 
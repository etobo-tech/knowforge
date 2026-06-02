export const THEME_STORAGE_KEY = 'knowforge-theme'

export type Theme = 'light' | 'dark'
export type ThemePreference = Theme | 'system'

export function getSystemTheme(): Theme {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function getStoredPreference(): ThemePreference | null {
  if (typeof window === 'undefined') return null
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    if (stored === 'light' || stored === 'dark' || stored === 'system') {
      return stored
    }
    return null
  } catch {
    return null
  }
}

export function resolveTheme(preference: ThemePreference = 'system'): Theme {
  if (preference === 'system') return getSystemTheme()
  return preference
}

export function applyTheme(theme: Theme) {
  document.documentElement.classList.toggle('dark', theme === 'dark')
}

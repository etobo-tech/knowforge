'use client'

import { Moon, Sun } from 'lucide-react'

import { useTheme } from '@/components/ThemeProvider'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  const isDark = theme === 'dark'

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-sidebar-text transition-colors hover:bg-sidebar-active/50"
      aria-label={isDark ? 'Activar modo claro' : 'Activar modo oscuro'}
    >
      {isDark ? (
        <Sun size={14} className="opacity-60" aria-hidden />
      ) : (
        <Moon size={14} className="opacity-60" aria-hidden />
      )}
      {isDark ? 'Modo claro' : 'Modo oscuro'}
    </button>
  )
}

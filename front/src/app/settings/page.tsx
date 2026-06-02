'use client'

import { Monitor, Moon, Sun } from 'lucide-react'

import { useTheme } from '@/components/ThemeProvider'
import type { ThemePreference } from '@/lib/theme'

const options: {
  value: ThemePreference
  label: string
  description: string
  icon: typeof Sun
}[] = [
  {
    value: 'light',
    label: 'Claro',
    description: 'Fondo claro en todo el contenido principal.',
    icon: Sun,
  },
  {
    value: 'dark',
    label: 'Oscuro',
    description: 'Fondo oscuro en chat, archivos y subida.',
    icon: Moon,
  },
  {
    value: 'system',
    label: 'Sistema',
    description: 'Sigue la preferencia de tu sistema operativo.',
    icon: Monitor,
  },
]

export default function SettingsPage() {
  const { preference, setPreference } = useTheme()

  return (
    <div className="flex h-full flex-col">
      <header className="shrink-0 border-b border-card-border bg-card-bg px-8 py-5">
        <h1 className="text-2xl font-bold text-text-primary">Settings</h1>
        <p className="mt-0.5 text-sm text-text-secondary">
          Apariencia y preferencias de la interfaz
        </p>
      </header>

      <div className="flex-1 overflow-y-auto p-8">
        <section className="max-w-xl rounded-2xl border border-card-border bg-card-bg p-6">
          <h2 className="text-lg font-bold text-text-primary">Tema</h2>
          <p className="mt-1 text-sm text-text-secondary">
            Elige cómo se ve Knowforge en el área principal (el menú lateral
            siempre usa tonos oscuros).
          </p>

          <div className="mt-5 space-y-2" role="radiogroup" aria-label="Tema">
            {options.map((option) => {
              const Icon = option.icon
              const selected = preference === option.value
              return (
                <label
                  key={option.value}
                  className={`flex cursor-pointer items-start gap-3 rounded-xl border px-4 py-3 transition-colors ${
                    selected
                      ? 'border-primary bg-primary/10'
                      : 'border-card-border bg-content-bg hover:border-primary/30'
                  }`}
                >
                  <input
                    type="radio"
                    name="theme"
                    value={option.value}
                    checked={selected}
                    onChange={() => setPreference(option.value)}
                    className="mt-1 accent-primary"
                  />
                  <Icon
                    size={18}
                    className={`mt-0.5 shrink-0 ${selected ? 'text-primary' : 'text-text-secondary'}`}
                    aria-hidden
                  />
                  <span>
                    <span className="block text-sm font-semibold text-text-primary">
                      {option.label}
                    </span>
                    <span className="mt-0.5 block text-xs text-text-secondary">
                      {option.description}
                    </span>
                  </span>
                </label>
              )
            })}
          </div>
        </section>
      </div>
    </div>
  )
}

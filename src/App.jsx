import Timeline from './components/Timeline'
import Logo from './components/Logo'

export default function App() {
  return (
    <div className="min-h-screen bg-cream">
      <header className="py-10 px-4 text-center">
        <Logo className="h-7 sm:h-9 w-auto mx-auto" />
        <p className="mt-3 text-ink/60 text-sm">Klass, kamp och kompromiss — från 1846 till i dag</p>
      </header>
      <main className="max-w-4xl mx-auto px-4 py-12">
        <Timeline />
      </main>
    </div>
  )
}

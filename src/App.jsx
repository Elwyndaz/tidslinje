import Timeline from './components/Timeline'

export default function App() {
  return (
    <div className="min-h-screen bg-white">
      <header className="bg-accent text-white py-10 px-4 text-center">
        <h1 className="text-3xl font-bold tracking-tight">Arbetarrörelsens tidslinje</h1>
        <p className="mt-2 text-red-200 text-sm">Klass, kamp och kompromiss — från 1846 till i dag</p>
      </header>
      <main className="max-w-4xl mx-auto px-4 py-12">
        <Timeline />
      </main>
    </div>
  )
}

import { useState } from 'react'
import events from '../data/events.json'
import EpochGroup from './EpochGroup'
import Modal from './Modal'

// Epoker definierade här — lätt att uppdatera titlar och år
const EPOCHS = [
  {
    id: 'informera-och-agitera',
    title: 'Informera och agitera',
    years: '1846–1931',
  },
  {
    id: 'folkhemmet-och-valfardsstaten',
    title: 'Folkhemmet och välfärdsstaten',
    years: '1932–1983',
  },
  {
    id: 'forvaltande',
    title: 'Förvaltande',
    years: '1985–2026',
  },
]

export default function Timeline() {
  const [open, setOpen] = useState(null)
  const sorted = [...events].sort((a, b) => a.year - b.year)

  return (
    <>
      {EPOCHS.map((epoch) => (
        <EpochGroup
          key={epoch.id}
          epoch={epoch}
          events={sorted.filter((e) => e.epoch === epoch.id)}
          onOpen={setOpen}
        />
      ))}
      {open && <Modal event={open} onClose={() => setOpen(null)} />}
    </>
  )
}

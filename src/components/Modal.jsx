import { useEffect } from 'react'
import { WikiIcon } from './icons'

const ICONS = {
  podcast: '🎙️',
  video: '🎬',
  wiki: <WikiIcon className="w-[18px] h-[18px]" />,
}

const LINK_LABEL = { podcast: 'Podcast', video: 'Video', wiki: 'Läs mer' }

function imgSrc(path) {
  if (!path) return null
  if (path.startsWith('http')) return path
  return `${import.meta.env.BASE_URL}${path}`
}

export default function Modal({ event, onClose }) {
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onClose])

  const imgUrl = imgSrc(event.image)

  return (
    <div
      className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white max-w-xl w-full rounded-xl shadow-2xl max-h-[85vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Stor bild högst upp — visas bara om bild finns */}
        {imgUrl && (
          <img
            src={imgUrl}
            alt={event.title}
            className="w-full h-52 object-cover rounded-t-xl"
          />
        )}

        <div className="p-6">
          {/* Huvud: år + titel + stängknapp */}
          <div className="flex justify-between items-start mb-5">
            <div>
              <span className="text-accent font-bold text-sm tracking-wide">
                {event.year}
              </span>
              <h2 className="text-xl font-bold text-gray-900 mt-1 leading-tight">
                {event.title}
              </h2>
            </div>
            <button
              onClick={onClose}
              aria-label="Stäng"
              className="text-gray-400 hover:text-gray-700 text-xl leading-none ml-4 mt-0.5"
            >
              ✕
            </button>
          </div>

          {/* Lång beskrivning */}
          <p className="text-gray-700 leading-relaxed text-sm">{event.long}</p>

          {/* Länkikoner */}
          {event.links && event.links.length > 0 && (
            <div className="flex flex-wrap gap-4 mt-6 pt-4 border-t border-gray-100">
              {event.links.map((link, i) => (
                <a
                  key={i}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-accent transition-colors"
                >
                  <span className="text-lg">{ICONS[link.type] ?? '🔗'}</span>
                  <span>{LINK_LABEL[link.type] || link.type}</span>
                </a>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

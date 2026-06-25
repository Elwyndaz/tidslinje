// Emoji-ikoner för länktyper — byts ut mot SVG-ikoner senare om det behövs
const ICONS = { podcast: '🎙️', video: '🎬', wiki: '📖' }

// Tailwind-klasser per kortstorlek
const SIZE = {
  large: 'p-5 shadow-md border-l-4',
  medium: 'p-4 shadow-sm border-l-2',
  small: 'p-3 border-l',
}

const TITLE_SIZE = {
  large: 'text-base',
  medium: 'text-sm',
  small: 'text-sm',
}

// Löser sökväg för bilder i public/ med hänsyn till Vite:s base-URL
function imgSrc(path) {
  if (!path) return null
  if (path.startsWith('http')) return path
  return `${import.meta.env.BASE_URL}${path}`
}

export default function EventCard({ event, onOpen }) {
  const hasLinks = event.links && event.links.length > 0
  const thumb    = imgSrc(event.image)

  return (
    <button
      onClick={() => onOpen(event)}
      className={`
        text-left w-full bg-white rounded-lg border border-gray-100
        border-l-accent hover:shadow-lg transition-shadow cursor-pointer
        ${SIZE[event.size]}
      `}
    >
      {/* Rubrikrad: år + titel + eventuell thumbnail */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-accent font-bold text-xs mb-1 tracking-wide">
            {event.year}
          </p>
          <h3 className={`font-semibold text-gray-900 leading-snug ${TITLE_SIZE[event.size]}`}>
            {event.title}
          </h3>
        </div>

        {/* Thumbnail — visas på large och medium om bild finns */}
        {thumb && event.size !== 'small' && (
          <img
            src={thumb}
            alt=""
            className="w-16 h-16 object-cover rounded flex-none"
            loading="lazy"
          />
        )}
      </div>

      {/* Kort beskrivning — visas ej på small-kort */}
      {event.size !== 'small' && (
        <p className="text-gray-500 text-xs mt-1 line-clamp-2 leading-relaxed">
          {event.short}
        </p>
      )}

      {/* Länkikoner */}
      {hasLinks && (
        <div className="flex gap-2 mt-2">
          {event.links.map((link, i) => (
            <span key={i} title={link.type} className="text-sm leading-none">
              {ICONS[link.type] || '🔗'}
            </span>
          ))}
        </div>
      )}
    </button>
  )
}

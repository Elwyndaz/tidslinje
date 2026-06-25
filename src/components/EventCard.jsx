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

export default function EventCard({ event, onOpen }) {
  const hasLinks = event.links && event.links.length > 0

  return (
    <button
      onClick={() => onOpen(event)}
      className={`
        text-left w-full bg-white rounded-lg border border-gray-100
        border-l-accent hover:shadow-lg transition-shadow cursor-pointer
        ${SIZE[event.size]}
      `}
    >
      <p className="text-accent font-bold text-xs mb-1 tracking-wide">
        {event.year}
      </p>

      <h3 className={`font-semibold text-gray-900 leading-snug ${TITLE_SIZE[event.size]}`}>
        {event.title}
      </h3>

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

// Wikipedia-ikon — cirkel med serif-"W", ersätter boksymbolen som lätt
// förväxlades med en generisk läsningsikon.
export function WikiIcon({ className = 'w-4 h-4' }) {
  return (
    <svg viewBox="0 0 20 20" className={className} aria-hidden="true">
      <circle cx="10" cy="10" r="9" fill="none" stroke="currentColor" strokeWidth="1.3" />
      <text
        x="10"
        y="14.5"
        textAnchor="middle"
        fontSize="10.5"
        fontFamily="Georgia, 'Times New Roman', serif"
        fontWeight="bold"
        fill="currentColor"
      >
        W
      </text>
    </svg>
  )
}

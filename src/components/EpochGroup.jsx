import EventCard from './EventCard'

export default function EpochGroup({ epoch, events, onOpen }) {
  if (events.length === 0) return null

  return (
    <section className="mb-20">
      {/* Epokrubrik */}
      <div className="text-center mb-12">
        <h2 className="text-2xl font-bold text-accent">{epoch.title}</h2>
        <p className="text-gray-400 text-sm mt-1 tracking-widest uppercase">
          {epoch.years}
        </p>
        <div className="mx-auto mt-3 w-12 h-0.5 bg-accent opacity-40" />
      </div>

      {/* Tidslinje-container med vertikal linje */}
      <div className="relative">
        {/*
          Linje: till vänster på mobil, centrerad på desktop.
          left-[0.75rem] = halva bredden på dot-kolumnen (1.5rem) på mobil.
          md:left-1/2     = exakt mitten av containern på desktop.
        */}
        <div className="absolute left-[0.75rem] md:left-1/2 top-0 bottom-0 w-px bg-ink/25 -translate-x-1/2" />

        {events.map((event, i) => {
          const goLeft = i % 2 === 0

          return (
            <div
              key={event.id}
              /*
                Grid på mobil:  [1.5rem dot-kolumn | 1fr kort-kolumn]
                Grid på desktop:[1fr vänster | 2rem dot-kolumn | 1fr höger]
                display:none-element tar inte upp grid-plats → fungerar på mobil.
              */
              className="grid grid-cols-[1.5rem_1fr] md:grid-cols-[1fr_2rem_1fr] mb-8 items-start"
            >
              {/* Desktop: vänster kort (hidden på mobil → tar ej grid-plats) */}
              <div className="hidden md:flex md:justify-end md:pr-4">
                {goLeft && <EventCard event={event} onOpen={onOpen} />}
              </div>

              {/* Dot — alltid synlig, centrerad i sin kolumn */}
              <div className="flex flex-col items-center pt-4">
                <div className="w-3 h-3 rounded-full bg-accent border-2 border-white shadow relative z-10" />
              </div>

              {/* Mobil: alltid höger. Desktop: höger kort om !goLeft */}
              <div className="pl-3 md:pl-4">
                {/* Mobil: visa alltid */}
                <div className="md:hidden">
                  <EventCard event={event} onOpen={onOpen} />
                </div>
                {/* Desktop: visa bara om kortet ska till höger */}
                {!goLeft && (
                  <div className="hidden md:block">
                    <EventCard event={event} onOpen={onOpen} />
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}

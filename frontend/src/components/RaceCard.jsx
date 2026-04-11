/**
 * RaceCard — one row per race, expands to show runner odds grid.
 *
 * Collapsed: race time, name, class, distance, going, runner count.
 * Expanded:  runner table with one column per bookmaker (the layout
 *            Mark requested — bookmakers as columns, runners as rows).
 *
 * Layout note: this is the CORRECT orientation per Mark's specification.
 * Runners run vertically (rows), bookmakers run horizontally (columns).
 * Read across a row to compare all bookies for one horse.
 *
 * Odds come embedded in the /v1/racecards/standard response — each
 * runner has an `odds` array with all bookmaker prices.
 */
import React, { useMemo } from 'react'

function classColour(cls) {
  const n = parseInt(cls)
  if (n === 1 || cls === 'Group 1') return 'text-chimera-gold'
  if (n === 2 || cls === 'Group 2') return 'text-slate-300'
  if (n === 3 || cls === 'Group 3') return 'text-slate-400'
  return 'text-slate-500'
}

function OddsGrid({ runners: runnerList }) {
  const { bookmakers, runners, bestPrices } = useMemo(() => {
    if (!runnerList?.length) return { bookmakers: [], runners: [], bestPrices: {} }

    // Collect all bookmaker names from embedded odds
    const bookSet = new Set()
    runnerList.forEach(r => {
      (r.odds ?? []).forEach(o => bookSet.add(o.bookmaker))
    })
    const bookmakers = [...bookSet].filter(Boolean).sort()

    // Best price per runner (highest decimal odds)
    const bestPrices = {}
    runnerList.forEach(r => {
      const prices = (r.odds ?? []).map(o => parseFloat(o.decimal ?? 0)).filter(p => p > 0)
      bestPrices[r.horse_id ?? r.horse] = prices.length ? Math.max(...prices) : 0
    })

    return { bookmakers, runners: runnerList, bestPrices }
  }, [runnerList])

  if (!runners.length) return (
    <div className="px-4 py-6 text-xs text-slate-500 text-center">No runners available</div>
  )

  if (!bookmakers.length) return (
    <div className="px-4 py-6 text-xs text-slate-500 text-center">No bookmaker odds available yet</div>
  )

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-chimera-700 text-slate-500">
            {/* Runner column */}
            <th className="text-left px-4 py-2 font-medium sticky left-0 bg-chimera-800 min-w-40">
              Runner
            </th>
            <th className="text-center px-3 py-2 font-medium">#</th>
            {/* One column per bookmaker */}
            {bookmakers.map(b => (
              <th key={b} className="text-center px-3 py-2 font-medium whitespace-nowrap">
                {b}
              </th>
            ))}
            <th className="text-center px-3 py-2 font-medium">Best</th>
          </tr>
        </thead>
        <tbody>
          {runners
            .filter(r => !r.non_runner)
            .sort((a, b) => (parseInt(a.number) || 99) - (parseInt(b.number) || 99))
            .map((runner, ri) => {
              const runnerId = runner.horse_id ?? runner.horse
              const best = bestPrices[runnerId] ?? 0

              return (
                <tr
                  key={runnerId ?? ri}
                  className={`border-b border-chimera-700 last:border-0 ${
                    ri % 2 === 0 ? '' : 'bg-chimera-900/30'
                  }`}
                >
                  {/* Runner name + jockey */}
                  <td className="px-4 py-2 sticky left-0 bg-inherit">
                    <div className="font-medium text-white whitespace-nowrap">
                      {runner.horse ?? runner.runner_name ?? runner.name}
                    </div>
                    {runner.jockey && (
                      <div className="text-slate-500 text-xs mt-0.5">{runner.jockey}</div>
                    )}
                  </td>

                  {/* Draw / number */}
                  <td className="px-3 py-2 text-center text-slate-400">
                    {runner.draw ?? runner.number ?? '—'}
                  </td>

                  {/* Price per bookmaker */}
                  {bookmakers.map(bk => {
                    const oddsEntry = (runner.odds ?? []).find(
                      o => o.bookmaker === bk
                    )
                    const price = oddsEntry
                      ? parseFloat(oddsEntry.decimal ?? 0)
                      : null
                    const isBest = price && price === best

                    return (
                      <td key={bk} className="px-3 py-2 text-center">
                        {price ? (
                          <span
                            className={`inline-block px-1.5 py-0.5 rounded font-mono font-semibold ${
                              isBest
                                ? 'bg-green-900 text-chimera-green'
                                : 'text-slate-300'
                            }`}
                          >
                            {oddsEntry.fractional ?? price.toFixed(2)}
                          </span>
                        ) : (
                          <span className="text-slate-600">—</span>
                        )}
                      </td>
                    )
                  })}

                  {/* Best price */}
                  <td className="px-3 py-2 text-center">
                    {best > 0 ? (
                      <span className="font-mono font-bold text-chimera-green">
                        {best.toFixed(2)}
                      </span>
                    ) : (
                      <span className="text-slate-600">—</span>
                    )}
                  </td>
                </tr>
              )
            })}
        </tbody>
      </table>
    </div>
  )
}

export default function RaceCard({ race, isExpanded, onToggle }) {
  return (
    <div>
      {/* Race row — always visible */}
      <button
        onClick={onToggle}
        className="w-full text-left px-4 py-3 hover:bg-chimera-700/50 transition-colors"
      >
        <div className="flex items-center gap-4">
          {/* Time */}
          <span className="font-mono text-chimera-gold font-semibold text-sm w-12 shrink-0">
            {race.off_time ?? race.time ?? '—'}
          </span>

          {/* Race name */}
          <span className="text-white text-sm font-medium flex-1 truncate">
            {race.race_name ?? race.name ?? 'Race'}
          </span>

          {/* Metadata pills */}
          <div className="flex items-center gap-2 shrink-0">
            {race.distance && (
              <span className="text-xs text-slate-400">{race.distance}</span>
            )}
            {race.going && (
              <span className="text-xs bg-chimera-700 text-slate-300 px-2 py-0.5 rounded">
                {race.going}
              </span>
            )}
            {(race.race_class ?? race.class) && (
              <span className={`text-xs font-medium ${classColour(race.race_class ?? race.class)}`}>
                C{race.race_class ?? race.class}
              </span>
            )}
            {race.field_size && (
              <span className="text-xs text-slate-500">{race.field_size} rnrs</span>
            )}
            {race.prize && (
              <span className="text-xs text-chimera-gold">{race.prize}</span>
            )}
            {/* Expand indicator */}
            <span className={`text-slate-500 text-xs transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </div>
        </div>
      </button>

      {/* Expanded odds grid — reads odds from runner data, no separate API call */}
      {isExpanded && (
        <div className="border-t border-chimera-700 bg-chimera-900/50">
          <OddsGrid runners={race.runners} />
        </div>
      )}
    </div>
  )
}

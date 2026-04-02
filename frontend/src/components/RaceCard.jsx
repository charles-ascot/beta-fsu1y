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
 */
import React, { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getOdds } from '../services/api'

function classColour(cls) {
  const n = parseInt(cls)
  if (n === 1 || cls === 'Group 1') return 'text-chimera-gold'
  if (n === 2 || cls === 'Group 2') return 'text-slate-300'
  if (n === 3 || cls === 'Group 3') return 'text-slate-400'
  return 'text-slate-500'
}

function OddsGrid({ raceId }) {
  const { data, isLoading, error } = useQuery({
    queryKey:        ['odds', raceId],
    queryFn:         () => getOdds(raceId),
    refetchInterval: 60_000,
    staleTime:       30_000,
  })

  const { bookmakers, runners, bestPrices } = useMemo(() => {
    const raw = data?.data ?? data ?? null
    if (!raw) return { bookmakers: [], runners: [], bestPrices: {} }

    // The Racing API odds response structure:
    // { runners: [{ runner_name, odds: [{ bookmaker, price }] }] }
    const runnerList = raw.runners ?? raw.data?.runners ?? []
    if (!runnerList.length) return { bookmakers: [], runners: [], bestPrices: {} }

    // Collect all bookmaker names
    const bookSet = new Set()
    runnerList.forEach(r => {
      (r.odds ?? []).forEach(o => bookSet.add(o.bookmaker ?? o.name ?? o.exchange))
    })
    const bookmakers = [...bookSet].filter(Boolean).sort()

    // Best price per runner
    const bestPrices = {}
    runnerList.forEach(r => {
      const prices = (r.odds ?? []).map(o => parseFloat(o.decimal ?? o.price ?? 0)).filter(p => p > 0)
      bestPrices[r.runner_id ?? r.horse_id ?? r.runner_name] = prices.length ? Math.max(...prices) : 0
    })

    return { bookmakers, runners: runnerList, bestPrices }
  }, [data])

  if (isLoading) return (
    <div className="px-4 py-6 text-xs text-slate-500 text-center">Loading odds…</div>
  )

  if (error) return (
    <div className="px-4 py-4 text-xs text-chimera-amber text-center">
      {error.response?.status === 403
        ? 'Odds require Standard plan or above on The Racing API'
        : 'Failed to load odds'}
    </div>
  )

  if (!runners.length) return (
    <div className="px-4 py-6 text-xs text-slate-500 text-center">No odds available yet</div>
  )

  if (!bookmakers.length) return (
    <div className="px-4 py-6 text-xs text-slate-500 text-center">No bookmaker odds available</div>
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
            .sort((a, b) => (a.number ?? 99) - (b.number ?? 99))
            .map((runner, ri) => {
              const runnerId = runner.runner_id ?? runner.horse_id ?? runner.runner_name
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
                      {runner.runner_name ?? runner.name}
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
                      o => (o.bookmaker ?? o.name ?? o.exchange) === bk
                    )
                    const price = oddsEntry
                      ? parseFloat(oddsEntry.decimal ?? oddsEntry.price ?? 0)
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
                            {price.toFixed(2)}
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

      {/* Cache indicator */}
      {data?.cache && (
        <div className="px-4 py-1 text-right">
          <span className={`text-xs ${data.cache === 'HIT' ? 'text-chimera-green' : 'text-chimera-amber'}`}>
            odds cache {data.cache}
          </span>
        </div>
      )}
    </div>
  )
}

export default function RaceCard({ race, isExpanded, onToggle }) {
  const raceId = race.race_id ?? race.id

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

      {/* Expanded odds grid */}
      {isExpanded && (
        <div className="border-t border-chimera-700 bg-chimera-900/50">
          <OddsGrid raceId={raceId} />
        </div>
      )}
    </div>
  )
}

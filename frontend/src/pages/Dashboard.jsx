/**
 * Racing dashboard.
 * Shows today's / tomorrow's racecards grouped by meeting.
 * Click any race to expand the runner odds grid.
 */
import React, { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { getRacecards } from '../services/api'
import RaceCard from '../components/RaceCard'

// All regions The Racing API covers.
// ✅ = full daily cards + odds  ⚠️ = group/stakes level only
const REGIONS = [
  { key: '',    label: 'All' },
  { key: 'gb',  label: 'GB ✅' },
  { key: 'ire', label: 'IRE ✅' },
  { key: 'hk',  label: 'HK ✅' },
  { key: 'fr',  label: 'FR ⚠️' },
  { key: 'usa', label: 'USA ⚠️' },
  { key: 'aus', label: 'AUS ⚠️' },
  { key: 'zaf', label: 'ZAF ⚠️' },
  { key: 'uae', label: 'UAE ⚠️' },
  { key: 'jpn', label: 'JPN ⚠️' },
  { key: 'ger', label: 'GER ⚠️' },
  { key: 'can', label: 'CAN ⚠️' },
  { key: 'ita', label: 'ITA ⚠️' },
  { key: 'arg', label: 'ARG ⚠️' },
  { key: 'nzl', label: 'NZL ⚠️' },
  { key: 'bra', label: 'BRA ⚠️' },
  { key: 'qat', label: 'QAT ⚠️' },
  { key: 'sau', label: 'SAU ⚠️' },
]

const DAYS = [
  { key: 'today',    label: 'Today' },
  { key: 'tomorrow', label: 'Tomorrow' },
]

function groupByCourse(races) {
  const groups = {}
  races.forEach(r => {
    const key = r.course || r.meeting || 'Unknown'
    if (!groups[key]) groups[key] = []
    groups[key].push(r)
  })
  return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b))
}

export default function Dashboard() {
  const [day, setDay]       = useState('today')
  const [region, setRegion] = useState('')
  const [expanded, setExpanded] = useState(null)

  const { data, isLoading, isFetching, dataUpdatedAt } = useQuery({
    queryKey:        ['racecards', day, region],
    queryFn:         () => getRacecards({ day, region: region || undefined }),
    refetchInterval: 60_000,
  })

  const races   = useMemo(() => data?.data?.racecards ?? data?.data?.races ?? (Array.isArray(data?.data) ? data.data : []), [data])
  const grouped = useMemo(() => groupByCourse(races), [races])
  const cache   = data?.cache ?? null

  const toggle = (raceId) =>
    setExpanded(prev => prev === raceId ? null : raceId)

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="space-y-2">
        {/* Day toggle */}
        <div className="flex items-center gap-3">
          <div className="flex gap-1 bg-chimera-800 rounded-lg p-1">
            {DAYS.map(d => (
              <button
                key={d.key}
                onClick={() => setDay(d.key)}
                className={`px-4 py-1.5 rounded text-sm font-medium transition-colors ${
                  day === d.key
                    ? 'bg-chimera-gold text-chimera-900'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {d.label}
              </button>
            ))}
          </div>

          {/* Status */}
          <div className="flex items-center gap-2 text-xs text-slate-500 ml-auto">
            {isFetching && (
              <div className="w-1.5 h-1.5 rounded-full bg-chimera-amber animate-pulse" />
            )}
            {cache && (
              <span className={cache === 'HIT' ? 'text-chimera-green' : 'text-chimera-amber'}>
                cache {cache}
              </span>
            )}
            <span>{races.length} races</span>
            {dataUpdatedAt > 0 && (
              <span>· {new Date(dataUpdatedAt).toLocaleTimeString()}</span>
            )}
          </div>
        </div>

        {/* Region filter — scrollable row */}
        <div className="flex gap-1 bg-chimera-800 rounded-lg p-1 overflow-x-auto">
          {REGIONS.map(r => (
            <button
              key={r.key}
              onClick={() => setRegion(r.key)}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors whitespace-nowrap ${
                region === r.key
                  ? 'bg-chimera-accent text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>

        {/* Coverage note for non-UK/IRE regions */}
        {region && !['', 'gb', 'ire', 'hk'].includes(region) && (
          <p className="text-xs text-chimera-amber px-1">
            ⚠️ {region.toUpperCase()} coverage is group/stakes level only — full daily cards
            and multi-bookmaker odds are UK/IRE/HK only on this plan.
          </p>
        )}
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center h-64 text-slate-500 text-sm">
          Loading racecards…
        </div>
      )}

      {/* No races */}
      {!isLoading && races.length === 0 && (
        <div className="flex items-center justify-center h-64 text-slate-500 text-sm">
          No races found for {day}{region ? ` (${region.toUpperCase()})` : ''}
        </div>
      )}

      {/* Grouped by course */}
      {grouped.map(([course, courseRaces]) => (
        <div key={course} className="bg-chimera-800 rounded-xl overflow-hidden">
          <div className="px-4 py-2.5 bg-chimera-700 flex items-center justify-between">
            <span className="font-semibold text-white text-sm">{course}</span>
            <span className="text-xs text-slate-400">{courseRaces.length} races</span>
          </div>
          <div className="divide-y divide-chimera-700">
            {courseRaces
              .sort((a, b) => (a.off_time || a.time || '').localeCompare(b.off_time || b.time || ''))
              .map(race => (
                <RaceCard
                  key={race.race_id || race.id}
                  race={race}
                  isExpanded={expanded === (race.race_id || race.id)}
                  onToggle={() => toggle(race.race_id || race.id)}
                />
              ))}
          </div>
        </div>
      ))}
    </div>
  )
}

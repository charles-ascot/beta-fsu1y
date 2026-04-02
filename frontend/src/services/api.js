/**
 * Axios instance for FSU-1Y backend.
 */
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  headers: {
    'X-API-Key': import.meta.env.VITE_FSU_API_KEY || '',
    'Content-Type': 'application/json',
  },
  timeout: 20000,
})

// ── API methods ───────────────────────────────────────────────────────────────

export const getHealth = () =>
  client.get('/health').then(r => r.data)

// Racecards
export const getRacecards = (params = {}) =>
  client.get('/v1/racecards', { params }).then(r => r.data)

export const getRacecardPro = (raceId) =>
  client.get(`/v1/racecards/pro/${raceId}`).then(r => r.data)

// Races
export const getRaces = (params = {}) =>
  client.get('/v1/races', { params }).then(r => r.data)

// Runners
export const getRunners = (raceId) =>
  client.get(`/v1/runners/${raceId}`).then(r => r.data)

// Odds
export const getOdds = (raceId, params = {}) =>
  client.get(`/v1/odds/${raceId}`, { params }).then(r => r.data)

// Results
export const getResults = (params = {}) =>
  client.get('/v1/results', { params }).then(r => r.data)

export const getResult = (raceId) =>
  client.get(`/v1/results/${raceId}`).then(r => r.data)

// Form
export const getHorseForm = (horseId, limit = 10) =>
  client.get(`/v1/form/${horseId}`, { params: { limit } }).then(r => r.data)

// ── Admin ─────────────────────────────────────────────────────────────────────

const adminClient = (adminKey) =>
  axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '',
    headers: { 'X-Admin-Key': adminKey, 'Content-Type': 'application/json' },
    timeout: 15000,
  })

export const listApiKeys = (adminKey) =>
  adminClient(adminKey).get('/v1/keys').then(r => r.data)

export const createApiKey = (adminKey, name) =>
  adminClient(adminKey).post('/v1/keys', { name }).then(r => r.data)

export const revokeApiKey = (adminKey, keyId) =>
  adminClient(adminKey).delete(`/v1/keys/${keyId}`).then(r => r.data)

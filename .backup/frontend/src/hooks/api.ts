const BASE = '/api'

async function getJson(path: string) {
  const r = await fetch(BASE + path)
  if (!r.ok) throw new Error('Request failed')
  return r.json()
}

export async function fetchMappingsSummary() { return getJson('/mappings/summary') }
export async function fetchNextUnmatched() { return getJson('/mappings/next') }
export async function fetchProblemSummaries(pattern?: string, difficulty?: string) {
  const params = new URLSearchParams()
  if (pattern) params.set('pattern', pattern)
  if (difficulty) params.set('difficulty', difficulty)
  return getJson('/problems/summary?' + params.toString())
}
export async function fetchProblemDetail(id: string) { return getJson('/problems/' + id) }

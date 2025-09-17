import { useEffect, useState } from 'react'
import { fetchMappingsSummary, fetchNextUnmatched } from '../hooks/api'
import { ProblemList } from '../components/ProblemList'
import { ProblemDetail } from '../components/ProblemDetail'

export function App() {
  const [summary, setSummary] = useState<any | null>(null)
  const [next, setNext] = useState<any | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  useEffect(() => { fetchMappingsSummary().then(setSummary); fetchNextUnmatched().then(setNext) }, [])

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'system-ui, sans-serif', fontSize: 14 }}>
      <div style={{ width: 260, borderRight: '1px solid #ddd', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 8, borderBottom: '1px solid #eee', background: '#fafafa' }}>
          <div style={{ fontWeight: 600 }}>Mapping</div>
          {summary && (
            <div style={{ fontSize: 11, marginTop: 4 }}>
              <div>Total: {summary.total}</div>
              <div>Matched: {summary.matched}</div>
              <div>Unmatched: {summary.unmatched}</div>
              <div>Coverage: {summary.coverage_percent}%</div>
            </div>
          )}
          {next && (
            <div style={{ fontSize: 11, marginTop: 6 }}>
              <div style={{ fontWeight: 600 }}>Next Unmatched</div>
              <div>{next.python?.title || next.cpp?.file || 'None'}</div>
            </div>
          )}
        </div>
        <div style={{ flex: 1, overflow: 'auto' }}>
          <ProblemList onSelect={setSelectedId} />
        </div>
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, overflow: 'auto' }}>
          <ProblemDetail id={selectedId} />
        </div>
      </div>
    </div>
  )
}

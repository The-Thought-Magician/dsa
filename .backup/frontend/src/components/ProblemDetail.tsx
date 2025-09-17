import { useEffect, useState } from 'react'
import { fetchProblemDetail } from '../hooks/api'

interface ProblemDetailProps { id: string | null }

export function ProblemDetail({ id }: ProblemDetailProps) {
  const [detail, setDetail] = useState<any | null>(null)

  useEffect(() => { if (id) fetchProblemDetail(id).then(setDetail) }, [id])
  if (!id) return <div style={{ padding: 8 }}>Select a problem</div>
  if (!detail) return <div style={{ padding: 8 }}>Loading...</div>
  return (
    <div style={{ padding: 8 }}>
      <h3 style={{ margin: '4px 0' }}>{detail.title}</h3>
      <div style={{ fontSize: 12, color: '#555', marginBottom: 8 }}>{detail.difficulty} · {detail.patterns.join(', ')}</div>
      <pre style={{ background: '#f7f7f7', padding: 8, fontSize: 12, overflowX: 'auto' }}>{detail.description || 'No description stored.'}</pre>
    </div>
  )
}

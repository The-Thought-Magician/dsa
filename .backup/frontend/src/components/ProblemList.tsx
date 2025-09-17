import { useEffect, useState } from 'react'
import { fetchProblemSummaries } from '../hooks/api'

interface ProblemListProps { onSelect: (id: string) => void }

export function ProblemList({ onSelect }: ProblemListProps) {
  const [items, setItems] = useState<any[]>([])
  const [pattern, setPattern] = useState('')
  const [difficulty, setDifficulty] = useState('')

  useEffect(() => { fetchProblemSummaries(pattern || undefined, difficulty || undefined).then(r => setItems(r.items)) }, [pattern, difficulty])

  return (
    <div>
      <div style={{ display: 'flex', gap: 4, marginBottom: 8 }}>
        <input placeholder='Pattern' value={pattern} onChange={e => setPattern(e.target.value)} style={{ flex: 1 }} />
        <input placeholder='Difficulty' value={difficulty} onChange={e => setDifficulty(e.target.value)} style={{ width: 110 }} />
      </div>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {items.map(p => (
          <li key={p.id} onClick={() => onSelect(p.id)} style={{ padding: '4px 6px', cursor: 'pointer', borderBottom: '1px solid #eee' }}>
            <strong>{p.title}</strong>
            <div style={{ fontSize: 10, color: '#666' }}>{p.difficulty} · {p.patterns.slice(0,3).join(', ')}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}

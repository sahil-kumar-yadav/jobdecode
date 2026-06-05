'use client';

import { useEffect, useState } from 'react';

type StatItem = { skill?: string; company?: string; count: number };

type StatsResponse = {
  top_skills: { skill: string; count: number }[];
  top_companies: { company: string; count: number }[];
  average_salary: number | null;
  count: number;
};

const API_BASE: string = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

export default function StatsPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [err, setErr] = useState<string | null>(null);
  const [running, setRunning] = useState<boolean>(false);
  const [lastVersion, setLastVersion] = useState<number | null>(null);

  async function refreshStats() {
    setLoading(true);
    setErr(null);
    try {
      const res = await fetch(`${API_BASE}/stats`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = (await res.json()) as StatsResponse;
      setStats(json);
    } catch (e: any) {
      setErr(e?.message ?? 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  }

  async function runEtl() {
    setRunning(true);
    setErr(null);
    try {
      const res = await fetch(`${API_BASE}/run-etl`, { method: 'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      if (typeof json?.stats_version === 'number') setLastVersion(json.stats_version);
      await refreshStats();
    } catch (e: any) {
      setErr(e?.message ?? 'ETL failed');
    } finally {
      setRunning(false);
    }
  }

  useEffect(() => {
    refreshStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <main style={{ padding: 24, fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif' }}>
      <h1 style={{ margin: 0, fontSize: 26 }}>Stats</h1>
      <p style={{ marginTop: 6, color: '#555' }}>
        Aggregates are computed from the SQLite data loaded by the ETL pipeline.
      </p>

      <div style={{ marginTop: 16, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <button
          onClick={runEtl}
          disabled={running}
          style={{ padding: '10px 14px', borderRadius: 10, border: '1px solid #ddd', background: '#fff' }}
        >
          {running ? 'Running ETL…' : 'Run ETL'}
        </button>
        <button
          onClick={refreshStats}
          disabled={loading || running}
          style={{ padding: '10px 14px', borderRadius: 10, border: '1px solid #ddd', background: '#fff' }}
        >
          Refresh
        </button>
        {lastVersion !== null && <span style={{ color: '#777', alignSelf: 'center' }}>stats_version: {lastVersion}</span>}
      </div>

      {err && <p style={{ color: 'crimson', marginTop: 12 }}>{err}</p>}
      {loading && <p style={{ marginTop: 12 }}>Loading…</p>}

      {stats && !loading && (
        <div style={{ marginTop: 16, display: 'grid', gap: 12 }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
            <div style={{ border: '1px solid #eaeaea', borderRadius: 12, padding: 14, background: '#fff' }}>
              <div style={{ color: '#777', fontSize: 13 }}>Jobs loaded</div>
              <div style={{ fontSize: 28, fontWeight: 800 }}>{stats.count}</div>
            </div>
            <div style={{ border: '1px solid #eaeaea', borderRadius: 12, padding: 14, background: '#fff' }}>
              <div style={{ color: '#777', fontSize: 13 }}>Average salary (LPA)</div>
              <div style={{ fontSize: 28, fontWeight: 800 }}>
                {stats.average_salary === null ? '—' : stats.average_salary.toFixed(2)}
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 12 }}>
            <div style={{ border: '1px solid #eaeaea', borderRadius: 12, padding: 14, background: '#fff' }}>
              <h2 style={{ fontSize: 16, margin: 0 }}>Top Skills</h2>
              <ul style={{ margin: '10px 0 0 18px', padding: 0 }}>
                {stats.top_skills.length === 0 && <li style={{ color: '#777' }}>No data yet. Click Run ETL.</li>}
                {stats.top_skills.map((x) => (
                  <li key={x.skill} style={{ margin: '6px 0' }}>
                    <b>{x.skill}</b> — {x.count}
                  </li>
                ))}
              </ul>
            </div>

            <div style={{ border: '1px solid #eaeaea', borderRadius: 12, padding: 14, background: '#fff' }}>
              <h2 style={{ fontSize: 16, margin: 0 }}>Top Companies</h2>
              <ul style={{ margin: '10px 0 0 18px', padding: 0 }}>
                {stats.top_companies.length === 0 && <li style={{ color: '#777' }}>No data yet. Click Run ETL.</li>}
                {stats.top_companies.map((x) => (
                  <li key={x.company} style={{ margin: '6px 0' }}>
                    <b>{x.company}</b> — {x.count}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}


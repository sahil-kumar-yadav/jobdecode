'use client';

import Link from 'next/link';

export default function Page() {
  return (
    <main style={{ padding: 24, fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif' }}>
      <h1 style={{ margin: 0, fontSize: 28 }}>Jobdecode</h1>
      <p style={{ marginTop: 8, color: '#555' }}>
        ETL + analytics for job postings (FastAPI backend, Next.js UI).
      </p>

      <div style={{ display: 'flex', gap: 12, marginTop: 18, flexWrap: 'wrap' }}>
        <Link
          href="/jobs"
          style={{
            padding: '10px 14px',
            border: '1px solid #ddd',
            borderRadius: 10,
            textDecoration: 'none',
            color: 'inherit',
          }}
        >
          Browse Jobs
        </Link>
        <Link
          href="/stats"
          style={{
            padding: '10px 14px',
            border: '1px solid #ddd',
            borderRadius: 10,
            textDecoration: 'none',
            color: 'inherit',
          }}
        >
          View Stats
        </Link>
      </div>

      <section style={{ marginTop: 28 }}>
        <h2 style={{ fontSize: 18, marginBottom: 10 }}>Run ETL</h2>
        <p style={{ color: '#555', margin: 0 }}>
          Use the “Run ETL” panel on the stats page to refresh data.
        </p>
      </section>

      <footer style={{ marginTop: 26, color: '#777', fontSize: 13 }}>
        API calls are made to the FastAPI server at <code>http://localhost:8000</code> by default.
      </footer>
    </main>
  );
}


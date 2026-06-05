'use client';

import { useEffect, useMemo, useState } from 'react';

type Job = {
  job_id: string;
  title: string;
  company: string;
  location: string | null;
  salary: string | null;
  skills: string[];
  posted_date: string | null;
  experience_level: string | null;
  description: string | null;
  min_lpa: number | null;
  max_lpa: number | null;
  avg_lpa: number | null;
};

type JobsResponse = {
  page: number;
  page_size: number;
  total: number;
  items: Job[];
};

const API_BASE: string = (globalThis as any)?.process?.env?.NEXT_PUBLIC_API_BASE ?? 'https://cautious-space-chainsaw-g9r76wxgx54fp7gv-8000.app.github.dev';


export default function JobsPage() {
  const [location, setLocation] = useState<string>('');
  const [skill, setSkill] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(20);
  const [sort, setSort] = useState<string>('posted_date');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');

  const [data, setData] = useState<JobsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [err, setErr] = useState<string | null>(null);

  const totalPages = useMemo(() => {
    if (!data) return 1;
    return Math.max(1, Math.ceil(data.total / data.page_size));
  }, [data]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setErr(null);
      try {
        const params = new URLSearchParams();
        if (location.trim()) params.set('location', location.trim());
        if (skill.trim()) params.set('skill', skill.trim());
        params.set('page', String(page));
        params.set('page_size', String(pageSize));
        params.set('sort', sort);
        params.set('order', order);

        const res = await fetch(`${API_BASE}/jobs?${params.toString()}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as JobsResponse;
        if (!cancelled) setData(json);
      } catch (e: any) {
        if (!cancelled) setErr(e?.message ?? 'Failed to load');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [location, skill, page, pageSize, sort, order]);

  return (
    <main style={{ padding: 24, fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif' }}>
      <h1 style={{ margin: 0, fontSize: 26 }}>Jobs</h1>
      <p style={{ marginTop: 6, color: '#555' }}>
        Filter by location/skill and browse results from the SQLite-backed API.
      </p>

      <div
        style={{
          marginTop: 16,
          padding: 14,
          border: '1px solid #eaeaea',
          borderRadius: 12,
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 12,
          background: '#fff',
        }}
      >
        <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          Location
          <input
            value={location}
            onChange={(e) => {
              setPage(1);
              setLocation(e.target.value);
            }}
            placeholder="e.g. Bengaluru"
          />
        </label>
        <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          Skill
          <input
            value={skill}
            onChange={(e) => {
              setPage(1);
              setSkill(e.target.value);
            }}
            placeholder="e.g. Python"
          />
        </label>
        <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          Page size
          <select
            value={pageSize}
            onChange={(e) => {
              setPage(1);
              setPageSize(Number(e.target.value));
            }}
          >
            {[10, 20, 50].map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          Sort
          <select value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="posted_date">posted_date</option>
            <option value="min_lpa">min_lpa</option>
            <option value="max_lpa">max_lpa</option>
            <option value="avg_lpa">avg_lpa</option>
          </select>
        </label>
        <label style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          Order
          <select value={order} onChange={(e) => setOrder(e.target.value as 'asc' | 'desc')}>
            <option value="desc">desc</option>
            <option value="asc">asc</option>
          </select>
        </label>
      </div>

      <section style={{ marginTop: 16 }}>
        {loading && <p>Loading…</p>}
        {err && <p style={{ color: 'crimson' }}>{err}</p>}

        {!loading && !err && data && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
              <p style={{ color: '#555', margin: 0 }}>
                Showing page <b>{data.page}</b> of <b>{totalPages}</b> • Total: <b>{data.total}</b>
              </p>
              <div style={{ display: 'flex', gap: 8 }}>
                <button disabled={data.page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>
                  Prev
                </button>
                <button disabled={data.page >= totalPages} onClick={() => setPage((p) => Math.min(totalPages, p + 1))}>
                  Next
                </button>
              </div>
            </div>

            <div style={{ marginTop: 12, display: 'grid', gap: 10 }}>
              {data.items.map((j) => (
                <article key={j.job_id} style={{ border: '1px solid #eaeaea', borderRadius: 12, padding: 14, background: '#fff' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap' }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 16 }}>{j.title}</div>
                      <div style={{ color: '#555', marginTop: 2 }}>
                        {j.company} • {j.location ?? '—'} • {j.experience_level ?? '—'}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 700 }}>{j.salary ?? '—'}</div>
                      <div style={{ color: '#777', fontSize: 13, marginTop: 2 }}>Posted: {j.posted_date ?? '—'}</div>
                    </div>
                  </div>

                  <div style={{ marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {j.skills.slice(0, 10).map((s: string) => (
                      <span
                        key={s}
                        style={{
                          border: '1px solid #eee',
                          background: '#fafafa',
                          padding: '4px 8px',
                          borderRadius: 999,
                          fontSize: 12,
                          color: '#333',
                        }}
                      >
                        {s}
                      </span>
                    ))}
                    {j.skills.length > 10 && <span style={{ color: '#777', fontSize: 12 }}>+{j.skills.length - 10}</span>}
                  </div>

                  {j.description && (
                    <details style={{ marginTop: 10 }}>
                      <summary style={{ cursor: 'pointer', color: '#333' }}>Description</summary>
                      <p style={{ color: '#555', marginTop: 8, whiteSpace: 'pre-wrap' }}>{j.description}</p>
                    </details>
                  )}
                </article>
              ))}
            </div>
          </>
        )}
      </section>
    </main>
  );
}


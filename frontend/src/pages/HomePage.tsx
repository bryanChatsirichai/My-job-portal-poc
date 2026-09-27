import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { fetchJobs } from '../api/jobs';
import { FilterPanel } from '../components/FilterPanel/FilterPanel';
import { useJobSources } from '../hooks/useJobSources';
import { getSourceDisplayName } from '../utils/format';
import { JobCard } from '../components/JobCard/JobCard';
import { SearchBar } from '../components/SearchBar/SearchBar';
import { Button } from '../components/ui/Button/Button';
import { Pill } from '../components/ui/Pill/Pill';
import type { JobListItem } from '../types/job';
import styles from './HomePage.module.scss';

type FilterKey = 'q' | 'salary_min' | 'salary_max' | 'location' | 'source';

const PAGE_SIZE = 20;

export function HomePage() {
  const jobSources = useJobSources();
  const searchInputRef = useRef<HTMLInputElement>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') ?? '');
  const [salaryMin, setSalaryMin] = useState(searchParams.get('salary_min') ?? '');
  const [salaryMax, setSalaryMax] = useState(searchParams.get('salary_max') ?? '');
  const [location, setLocation] = useState(searchParams.get('location') ?? '');
  const [source, setSource] = useState(searchParams.get('source') ?? '');
  const [jobs, setJobs] = useState<JobListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const page = Number(searchParams.get('page') ?? '1');
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const loadJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchJobs({
        q: searchParams.get('q') || undefined,
        salary_min: searchParams.get('salary_min') ? Number(searchParams.get('salary_min')) : undefined,
        salary_max: searchParams.get('salary_max') ? Number(searchParams.get('salary_max')) : undefined,
        location: searchParams.get('location') || undefined,
        source: searchParams.get('source') || undefined,
        page,
        limit: PAGE_SIZE,
      });
      setJobs(response.items);
      setTotal(response.total);
    } catch {
      setError('Unable to load jobs. Make sure the API is running.');
    } finally {
      setLoading(false);
    }
  }, [page, searchParams]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadJobs();
    }, 300);
    return () => window.clearTimeout(timer);
  }, [loadJobs]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== '/') return;
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.tagName === 'SELECT' ||
        target.isContentEditable
      ) {
        return;
      }
      event.preventDefault();
      searchInputRef.current?.focus();
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const applyFilters = () => {
    const next = new URLSearchParams();
    if (query) next.set('q', query);
    if (salaryMin) next.set('salary_min', salaryMin);
    if (salaryMax) next.set('salary_max', salaryMax);
    if (location) next.set('location', location);
    if (source) next.set('source', source);
    next.set('page', '1');
    setSearchParams(next);
  };

  const activeFilters = useMemo(() => {
    const chips: { key: FilterKey; label: string }[] = [];
    const q = searchParams.get('q');
    if (q) chips.push({ key: 'q', label: `"${q}"` });
    if (searchParams.get('salary_min')) {
      chips.push({ key: 'salary_min', label: `Min ${searchParams.get('salary_min')}` });
    }
    if (searchParams.get('salary_max')) {
      chips.push({ key: 'salary_max', label: `Max ${searchParams.get('salary_max')}` });
    }
    if (searchParams.get('location')) {
      chips.push({ key: 'location', label: searchParams.get('location')! });
    }
    if (searchParams.get('source')) {
      const sourceId = searchParams.get('source')!;
      chips.push({ key: 'source', label: getSourceDisplayName(sourceId) });
    }
    return chips;
  }, [searchParams]);

  const removeFilter = (key: FilterKey) => {
    const next = new URLSearchParams(searchParams);
    next.delete(key);
    next.set('page', '1');
    setSearchParams(next);

    if (key === 'q') setQuery('');
    if (key === 'salary_min') setSalaryMin('');
    if (key === 'salary_max') setSalaryMax('');
    if (key === 'location') setLocation('');
    if (key === 'source') setSource('');
  };

  const clearAllFilters = () => {
    setQuery('');
    setSalaryMin('');
    setSalaryMax('');
    setLocation('');
    setSource('');
    setSearchParams(new URLSearchParams({ page: '1' }));
  };

  const setPage = (nextPage: number) => {
    const next = new URLSearchParams(searchParams);
    next.set('page', String(nextPage));
    setSearchParams(next);
  };

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <h1 className={styles.headline}>Find your next role in Singapore</h1>
        <p className={styles.subcopy}>
          Search aggregated listings and track your applications in one place.
        </p>
        <SearchBar
          value={query}
          onChange={setQuery}
          onSubmit={applyFilters}
          inputRef={searchInputRef}
        />
      </section>

      <div className={styles.layout}>
        <FilterPanel
          salaryMin={salaryMin}
          salaryMax={salaryMax}
          location={location}
          source={source}
          sourceOptions={jobSources}
          onSalaryMinChange={setSalaryMin}
          onSalaryMaxChange={setSalaryMax}
          onLocationChange={setLocation}
          onSourceChange={setSource}
          onApply={applyFilters}
        />

        <section className={styles.results}>
          <div className={styles.summary}>
            <strong className={styles.summaryText}>
              {loading ? 'Searching...' : `Showing ${jobs.length} of ${total} jobs`}
            </strong>
            {activeFilters.length > 0 && (
              <div className={styles.chips}>
                {activeFilters.map((chip) => (
                  <Pill key={chip.key} onRemove={() => removeFilter(chip.key)}>
                    {chip.label}
                  </Pill>
                ))}
                <Button type="button" variant="ghost" className={styles.clearAll} onClick={clearAllFilters}>
                  Clear all
                </Button>
              </div>
            )}
          </div>

          {error && <p className={styles.error} role="alert">{error}</p>}

          {loading ? (
            <div className={styles.skeletons}>
              {Array.from({ length: 6 }).map((_, index) => (
                <div key={index} className={styles.skeleton} />
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <div className={styles.empty}>
              <h2>No jobs found</h2>
              <p>Try broadening your search or adjusting your filters.</p>
              {activeFilters.length > 0 && (
                <Button type="button" variant="secondary" onClick={clearAllFilters}>
                  Clear filters
                </Button>
              )}
            </div>
          ) : (
            <>
              <div className={styles.list}>
                {jobs.map((job) => <JobCard key={job.id} job={job} />)}
              </div>

              {totalPages > 1 && (
                <nav className={styles.pagination} aria-label="Job results pages">
                  <Button
                    type="button"
                    variant="secondary"
                    disabled={page <= 1}
                    onClick={() => setPage(page - 1)}
                  >
                    Previous
                  </Button>
                  <span className={styles.pageInfo}>
                    Page {page} of {totalPages}
                  </span>
                  <Button
                    type="button"
                    variant="secondary"
                    disabled={page >= totalPages}
                    onClick={() => setPage(page + 1)}
                  >
                    Next
                  </Button>
                </nav>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}

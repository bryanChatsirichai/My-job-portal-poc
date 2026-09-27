import { Link } from 'react-router-dom';
import { useEffect, useMemo, useState } from 'react';

import { DashboardAnalytics } from '../components/DashboardAnalytics/DashboardAnalytics';
import { DashboardJobCard } from '../components/DashboardJobCard/DashboardJobCard';
import { Button } from '../components/ui/Button/Button';
import { Input } from '../components/ui/Input/Input';
import { Pill } from '../components/ui/Pill/Pill';
import { SourceFilterSelect } from '../components/SourceFilterSelect/SourceFilterSelect';
import { Select } from '../components/ui/Select/Select';
import { useJobSources } from '../hooks/useJobSources';
import { useTrackedApplications } from '../hooks/useTrackedApplications';
import { getSourceDisplayName } from '../utils/format';
import type { ApplicationStatus } from '../types/job';
import { salaryOverlapsRange, STATUS_LABELS } from '../utils/applicationAnalytics';
import styles from './DashboardPage.module.scss';

const STATS_STORAGE_KEY = 'jobPortal_dashboardShowStats';

const KPI_STATUSES: Array<ApplicationStatus | 'all'> = [
  'all',
  'saved',
  'applied',
  'interview',
  'rejected',
  'accepted',
  'withdrawn',
];

const KPI_LABELS: Record<ApplicationStatus | 'all', string> = {
  all: 'All',
  ...STATUS_LABELS,
};

type ToolbarFilterKey = 'jobQuery' | 'source' | 'salaryMin' | 'salaryMax' | 'status';

function readShowStatsPreference(): boolean {
  try {
    return sessionStorage.getItem(STATS_STORAGE_KEY) === 'true';
  } catch {
    return false;
  }
}

export function DashboardPage() {
  const jobSources = useJobSources();
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | 'all'>('all');
  const [jobQuery, setJobQuery] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [salaryMin, setSalaryMin] = useState('');
  const [salaryMax, setSalaryMax] = useState('');
  const [showStats, setShowStats] = useState(readShowStatsPreference);
  const { items, stats, updateStatus, updateNotes, removeItem } = useTrackedApplications();

  useEffect(() => {
    try {
      sessionStorage.setItem(STATS_STORAGE_KEY, String(showStats));
    } catch {
      // Ignore storage failures in private browsing.
    }
  }, [showStats]);

  const filteredItems = useMemo(() => {
    const query = jobQuery.trim().toLowerCase();
    const min = salaryMin ? Number(salaryMin) : null;
    const max = salaryMax ? Number(salaryMax) : null;

    return items.filter((item) => {
      if (statusFilter !== 'all' && item.status !== statusFilter) return false;

      if (sourceFilter && item.jobSnapshot.source !== sourceFilter) return false;

      if (
        !salaryOverlapsRange(
          item.jobSnapshot.salaryMin,
          item.jobSnapshot.salaryMax,
          min,
          max,
        )
      ) {
        return false;
      }

      if (query) {
        const haystack = `${item.jobSnapshot.title} ${item.jobSnapshot.companyName}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }

      return true;
    });
  }, [items, jobQuery, salaryMax, salaryMin, sourceFilter, statusFilter]);

  const activeFilters = useMemo(() => {
    const chips: Array<{ key: ToolbarFilterKey; label: string }> = [];

    if (statusFilter !== 'all') {
      chips.push({ key: 'status', label: KPI_LABELS[statusFilter] });
    }
    if (jobQuery.trim()) {
      chips.push({ key: 'jobQuery', label: `"${jobQuery.trim()}"` });
    }
    if (sourceFilter) {
      chips.push({ key: 'source', label: getSourceDisplayName(sourceFilter) });
    }
    if (salaryMin) {
      chips.push({ key: 'salaryMin', label: `Min ${salaryMin}` });
    }
    if (salaryMax) {
      chips.push({ key: 'salaryMax', label: `Max ${salaryMax}` });
    }

    return chips;
  }, [jobQuery, salaryMax, salaryMin, sourceFilter, statusFilter]);

  const removeFilter = (key: ToolbarFilterKey) => {
    if (key === 'status') setStatusFilter('all');
    if (key === 'jobQuery') setJobQuery('');
    if (key === 'source') setSourceFilter('');
    if (key === 'salaryMin') setSalaryMin('');
    if (key === 'salaryMax') setSalaryMax('');
  };

  const clearAllFilters = () => {
    setStatusFilter('all');
    setJobQuery('');
    setSourceFilter('');
    setSalaryMin('');
    setSalaryMax('');
  };

  const hasToolbarFilters =
    statusFilter !== 'all' ||
    jobQuery.trim() !== '' ||
    sourceFilter !== '' ||
    salaryMin !== '' ||
    salaryMax !== '';

  const showEmptyState = items.length === 0;
  const showNoMatches = !showEmptyState && filteredItems.length === 0;

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerIntro}>
          <h1 className={styles.title}>My Applications</h1>
          <p className={styles.subtitle}>Saved in this browser</p>
        </div>
        <Button
          type="button"
          variant="secondary"
          className={styles.statsToggle}
          aria-expanded={showStats}
          aria-controls="dashboard-analytics"
          onClick={() => setShowStats((current) => !current)}
        >
          {showStats ? 'Hide statistics' : 'Show statistics'}
        </Button>
      </header>

      <div className={styles.kpiStrip} role="group" aria-label="Filter by application status">
        {KPI_STATUSES.map((status) => {
          const count = status === 'all' ? stats.total : stats[status];
          const isActive = statusFilter === status;

          return (
            <button
              key={status}
              type="button"
              className={[styles.kpiTile, isActive ? styles.kpiTileActive : ''].filter(Boolean).join(' ')}
              onClick={() => setStatusFilter(status)}
              aria-pressed={isActive}
            >
              <span className={styles.kpiValue}>{count}</span>
              <span className={styles.kpiLabel}>{KPI_LABELS[status]}</span>
            </button>
          );
        })}
      </div>

      {showStats && (
        <div id="dashboard-analytics" aria-hidden={false}>
          <DashboardAnalytics items={items} />
        </div>
      )}

      {!showEmptyState && (
        <section className={styles.toolbar} aria-label="Filter applications">
          <div className={styles.toolbarFields}>
            <label className={styles.field} htmlFor="dashboard-job-query">
              <span className={styles.fieldLabel}>Search job or company</span>
              <Input
                id="dashboard-job-query"
                value={jobQuery}
                onChange={(event) => setJobQuery(event.target.value)}
                placeholder="e.g. software engineer"
              />
            </label>

            <label className={styles.field} htmlFor="dashboard-source">
              <span className={styles.fieldLabel}>Source</span>
              <SourceFilterSelect
                id="dashboard-source"
                value={sourceFilter}
                sources={jobSources}
                onChange={setSourceFilter}
              />
            </label>

            <label className={styles.field} htmlFor="dashboard-salary-min">
              <span className={styles.fieldLabel}>Min salary (SGD)</span>
              <Input
                id="dashboard-salary-min"
                type="number"
                value={salaryMin}
                onChange={(event) => setSalaryMin(event.target.value)}
                placeholder="3000"
              />
            </label>

            <label className={styles.field} htmlFor="dashboard-salary-max">
              <span className={styles.fieldLabel}>Max salary (SGD)</span>
              <Input
                id="dashboard-salary-max"
                type="number"
                value={salaryMax}
                onChange={(event) => setSalaryMax(event.target.value)}
                placeholder="8000"
              />
            </label>
          </div>

          {activeFilters.length > 0 && (
            <div className={styles.activeFilters}>
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
        </section>
      )}

      {showEmptyState ? (
        <div className={styles.empty}>
          <h2>No tracked applications yet</h2>
          <p>Apply to a job and choose to track it to see it here.</p>
          <Link to="/" className={styles.searchJobs}>
            Search jobs
          </Link>
        </div>
      ) : showNoMatches ? (
        <div className={styles.empty}>
          <h2>No applications match these filters</h2>
          <p>Try removing a filter or searching with a broader term.</p>
          {hasToolbarFilters && (
            <Button type="button" variant="secondary" onClick={clearAllFilters}>
              Clear filters
            </Button>
          )}
        </div>
      ) : (
        <div className={styles.grid}>
          {filteredItems.map((item) => (
            <DashboardJobCard
              key={item.id}
              item={item}
              onStatusChange={updateStatus}
              onNotesChange={updateNotes}
              onRemove={removeItem}
            />
          ))}
        </div>
      )}
    </div>
  );
}

import { useEffect, useState } from 'react';

import type { JobSourceOption } from '../../types/job';
import { SourceFilterSelect } from '../SourceFilterSelect/SourceFilterSelect';
import { Button } from '../ui/Button/Button';
import { Input } from '../ui/Input/Input';
import styles from './FilterPanel.module.scss';

const SALARY_FLOOR = 0;
const SALARY_CEILING = 20000;
const SALARY_STEP = 500;
const FILTER_TOGGLE_ID = 'filter-mobile-toggle';

interface FilterPanelProps {
  salaryMin: string;
  salaryMax: string;
  location: string;
  source: string;
  sourceOptions: JobSourceOption[];
  onSalaryMinChange: (value: string) => void;
  onSalaryMaxChange: (value: string) => void;
  onLocationChange: (value: string) => void;
  onSourceChange: (value: string) => void;
  onApply: () => void;
}

function FilterFields({
  salaryMin,
  salaryMax,
  location,
  source,
  sourceOptions,
  onSalaryMinChange,
  onSalaryMaxChange,
  onLocationChange,
  onSourceChange,
  onApply,
}: FilterPanelProps) {
  const minRangeValue = salaryMin ? Number(salaryMin) : SALARY_FLOOR;
  const maxRangeValue = salaryMax ? Number(salaryMax) : SALARY_CEILING;

  return (
    <>
      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>Source</h3>
        <label className={styles.field} htmlFor="filter-source">
          <span className={styles.fieldLabel}>Job source</span>
          <SourceFilterSelect
            id="filter-source"
            value={source}
            sources={sourceOptions}
            onChange={onSourceChange}
          />
        </label>
      </section>

      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>Salary</h3>
        <div className={styles.fieldGroup}>
          <label className={styles.field} htmlFor="filter-salary-min">
            <span className={styles.fieldLabel}>Min (SGD)</span>
            <Input
              id="filter-salary-min"
              type="number"
              value={salaryMin}
              onChange={(event) => onSalaryMinChange(event.target.value)}
              placeholder="e.g. 3000"
            />
          </label>
          <label className={styles.field} htmlFor="filter-salary-max">
            <span className={styles.fieldLabel}>Max (SGD)</span>
            <Input
              id="filter-salary-max"
              type="number"
              value={salaryMax}
              onChange={(event) => onSalaryMaxChange(event.target.value)}
              placeholder="e.g. 8000"
            />
          </label>
        </div>
        <div className={styles.rangeGroup}>
          <label className={styles.rangeField} htmlFor="filter-salary-min-range">
            <span className={styles.fieldLabel}>Min range</span>
            <input
              id="filter-salary-min-range"
              type="range"
              className={styles.range}
              min={SALARY_FLOOR}
              max={SALARY_CEILING}
              step={SALARY_STEP}
              value={minRangeValue}
              onChange={(event) => {
                const value = event.target.value;
                onSalaryMinChange(value === String(SALARY_FLOOR) ? '' : value);
              }}
            />
          </label>
          <label className={styles.rangeField} htmlFor="filter-salary-max-range">
            <span className={styles.fieldLabel}>Max range</span>
            <input
              id="filter-salary-max-range"
              type="range"
              className={styles.range}
              min={SALARY_FLOOR}
              max={SALARY_CEILING}
              step={SALARY_STEP}
              value={maxRangeValue}
              onChange={(event) => {
                const value = event.target.value;
                onSalaryMaxChange(value === String(SALARY_CEILING) ? '' : value);
              }}
            />
          </label>
        </div>
      </section>

      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>Location</h3>
        <label className={styles.field} htmlFor="filter-location">
          <span className={styles.fieldLabel}>District or region</span>
          <Input
            id="filter-location"
            type="text"
            value={location}
            onChange={(event) => onLocationChange(event.target.value)}
            placeholder="e.g. Central, East"
          />
        </label>
      </section>

      <Button type="button" variant="primary" className={styles.applyButton} onClick={onApply}>
        Apply filters
      </Button>
    </>
  );
}

export function FilterPanel(props: FilterPanelProps) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  const closeDrawer = () => {
    setDrawerOpen(false);
    window.setTimeout(() => {
      document.getElementById(FILTER_TOGGLE_ID)?.focus();
    }, 0);
  };

  useEffect(() => {
    if (!drawerOpen) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') closeDrawer();
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [drawerOpen]);

  const handleApply = () => {
    props.onApply();
    closeDrawer();
  };

  return (
    <>
      <Button
        id={FILTER_TOGGLE_ID}
        type="button"
        variant="secondary"
        className={styles.mobileToggle}
        onClick={() => setDrawerOpen(true)}
        aria-expanded={drawerOpen}
        aria-controls="filter-drawer"
      >
        Filters
      </Button>

      <aside className={styles.panel}>
        <h2 className={styles.panelTitle}>Filters</h2>
        <FilterFields {...props} onApply={handleApply} />
      </aside>

      {drawerOpen && (
        <div className={styles.drawerBackdrop} onClick={closeDrawer} aria-hidden="true" />
      )}

      <aside
        id="filter-drawer"
        className={[styles.drawer, drawerOpen ? styles.drawerOpen : ''].filter(Boolean).join(' ')}
        aria-hidden={!drawerOpen}
        aria-label="Filters"
        role="dialog"
      >
        <div className={styles.drawerHeader}>
          <h2 className={styles.panelTitle}>Filters</h2>
          <Button
            type="button"
            variant="ghost"
            className={styles.drawerClose}
            onClick={closeDrawer}
            aria-label="Close filters"
          >
            Close
          </Button>
        </div>
        <FilterFields {...props} onApply={handleApply} />
      </aside>
    </>
  );
}

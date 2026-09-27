import { useEffect, useState } from 'react';

import { fetchJobSources } from '../api/jobs';
import type { JobSourceOption } from '../types/job';

const FALLBACK_SOURCES: JobSourceOption[] = [
  { id: 'mycareersfuture', label: 'MyCareersFuture' },
  { id: 'adzuna', label: 'Adzuna' },
  { id: 'jobicy', label: 'Jobicy' },
  { id: 'linkedin', label: 'LinkedIn' },
];

export function useJobSources(): JobSourceOption[] {
  const [sources, setSources] = useState<JobSourceOption[]>(FALLBACK_SOURCES);

  useEffect(() => {
    let cancelled = false;
    void fetchJobSources()
      .then((response) => {
        if (!cancelled && response.sources.length > 0) {
          setSources(response.sources);
        }
      })
      .catch(() => {
        /* keep fallback list */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return sources;
}

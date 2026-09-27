export const SOURCE_DISPLAY_NAMES: Record<string, string> = {
  mycareersfuture: 'MyCareersFuture',
  adzuna: 'Adzuna',
  jobicy: 'Jobicy',
  linkedin: 'LinkedIn',
  jobstreet: 'JobStreet',
  indeed: 'Indeed',
  // glassdoor: 'Glassdoor',
  // google: 'Google Jobs',
  // bayt: 'Bayt',
  // ziprecruiter: 'ZipRecruiter',
  // naukri: 'Naukri',
  // bdjobs: 'BDJobs',
  jobspy: 'JobSpy',
};
export function getSourceDisplayName(source: string): string {
  return SOURCE_DISPLAY_NAMES[source] ?? source;
}

export function formatSalary(
  min?: number | null,
  max?: number | null,
  currency = 'SGD',
  period?: string | null,
): string {
  if (min == null && max == null) return 'Salary not disclosed or check main job listing';
  const periodLabel = period ? ` / ${period}` : '';
  if (min != null && max != null) return `${currency} ${min.toLocaleString()} - ${max.toLocaleString()}${periodLabel}`;
  if (min != null) return `From ${currency} ${min.toLocaleString()}${periodLabel}`;
  return `Up to ${currency} ${max?.toLocaleString()}${periodLabel}`;
}

export function formatDate(value: string): string {
  return new Date(value).toLocaleDateString('en-SG', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

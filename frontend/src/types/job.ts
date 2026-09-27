export interface Location {
  address?: string | null;
  district?: string | null;
  region?: string | null;
  lat?: number | null;
  lng?: number | null;
}

export interface JobSourceOption {
  id: string;
  label: string;
}

export interface JobSourcesResponse {
  sources: JobSourceOption[];
}

export interface JobListItem {
  id: string;
  source: string;
  title: string;
  company_name: string;
  company_uen?: string | null;
  location: Location;
  salary_min?: number | null;
  salary_max?: number | null;
  salary_currency?: string | null;
  salary_period?: string | null;
  employment_type?: string | null;
  seniority_level?: string | null;
  skills: string[];
  posted_date: string;
  expiry_date?: string | null;
  apply_url: string;
  status: string;
}

export interface JobDetail extends JobListItem {
  description?: string | null;
}

export interface JobSearchResponse {
  items: JobListItem[];
  total: number;
  page: number;
  limit: number;
}

export type ApplicationStatus =
  | 'saved'
  | 'applied'
  | 'interview'
  | 'rejected'
  | 'accepted'
  | 'withdrawn';

export interface TrackedApplication {
  id: string;
  jobId: string;
  status: ApplicationStatus;
  notes?: string;
  appliedAt: string;
  updatedAt: string;
  jobSnapshot: {
    title: string;
    companyName: string;
    source: string;
    applyUrl: string;
    location?: { district?: string; region?: string };
    salaryMin?: number | null;
    salaryMax?: number | null;
  };
}

export interface JobSearchParams {
  q?: string;
  salary_min?: number;
  salary_max?: number;
  location?: string;
  source?: string;
  page?: number;
  limit?: number;
  sort?: string;
}

import type { JobDetail, JobSearchParams, JobSearchResponse, JobSourcesResponse } from '../types/job';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

function buildQuery(params: JobSearchParams): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchJobSources(): Promise<JobSourcesResponse> {
  return request<JobSourcesResponse>('/api/v1/job-sources');
}

export async function fetchJobs(params: JobSearchParams = {}): Promise<JobSearchResponse> {
  return request<JobSearchResponse>(`/api/v1/jobs${buildQuery(params)}`);
}

export async function fetchJobById(id: string): Promise<JobDetail> {
  return request<JobDetail>(`/api/v1/jobs/${id}`);
}

import { Select } from '../ui/Select/Select';
import type { JobSourceOption } from '../../types/job';

interface SourceFilterSelectProps {
  id: string;
  value: string;
  sources: JobSourceOption[];
  onChange: (value: string) => void;
}

export function SourceFilterSelect({ id, value, sources, onChange }: SourceFilterSelectProps) {
  return (
    <Select id={id} value={value} onChange={(event) => onChange(event.target.value)}>
      <option value="">All sources</option>
      {sources.map((option) => (
        <option key={option.id} value={option.id}>
          {option.label}
        </option>
      ))}
    </Select>
  );
}

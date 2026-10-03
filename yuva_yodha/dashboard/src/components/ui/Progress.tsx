export function Progress({ value, max = 100, color = "#3DCD58" }: { value: number; max?: number; color?: string }) {
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-navy-700" role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={max}>
      <div className="h-full rounded-full transition-all" style={{ width: `${Math.min(100, (100 * value) / max)}%`, background: color }} />
    </div>
  );
}

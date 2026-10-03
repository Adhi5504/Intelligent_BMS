import * as Slider from "@radix-ui/react-slider";

interface Props {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit?: string;
  format?: (v: number) => string;
  onChange: (v: number) => void;
}
export function SliderField({ label, value, min, max, step, unit, format, onChange }: Props) {
  return (
    <div className="space-y-2">
      <div className="flex items-baseline justify-between text-sm">
        <span className="text-slate-300">{label}</span>
        <span className="font-mono font-semibold text-brand">{format ? format(value) : value}{unit ? ` ${unit}` : ""}</span>
      </div>
      <Slider.Root className="relative flex h-5 w-full touch-none select-none items-center" value={[value]} min={min} max={max} step={step} onValueChange={(v) => onChange(v[0])} aria-label={label}>
        <Slider.Track className="relative h-1.5 grow rounded-full bg-navy-700">
          <Slider.Range className="absolute h-full rounded-full bg-brand" />
        </Slider.Track>
        <Slider.Thumb className="block h-4 w-4 rounded-full border-2 border-brand bg-navy-900 shadow focus:outline-none focus-visible:ring-2 focus-visible:ring-brand/60" />
      </Slider.Root>
      <div className="flex justify-between text-[10px] text-slate-500"><span>{format ? format(min) : min}</span><span>{format ? format(max) : max}</span></div>
    </div>
  );
}

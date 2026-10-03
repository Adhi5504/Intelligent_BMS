/** Indian digit grouping: 127178 -> 1,27,178 */
export function inr(n: number, withSymbol = true): string {
  if (!isFinite(n)) return "n/a";
  const neg = n < 0;
  const s = Math.round(Math.abs(n)).toString();
  let out: string;
  if (s.length <= 3) out = s;
  else {
    const last3 = s.slice(-3);
    const rest = s.slice(0, -3).replace(/\B(?=(\d{2})+(?!\d))/g, ",");
    out = rest + "," + last3;
  }
  return (neg ? "-" : "") + (withSymbol ? "₹" : "") + out;
}
export const num = (n: number, d = 1) => (isFinite(n) ? n.toFixed(d) : "n/a");
export const months = (m: number) => (isFinite(m) ? `${m.toFixed(1)} mo` : "no payback");

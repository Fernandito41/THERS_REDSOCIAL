import { MOODS } from "../data/mockData";

export default function MoodBadge({ mood, size = "text-xs", glow = false }) {
  if (!mood || !MOODS[mood]) return null;
  const { label, color } = MOODS[mood];

  return (
    <span
      className={`inline-flex items-center gap-1.5 ${size} font-medium px-2.5 py-1 rounded-full bg-surface dark:bg-surface-dark border border-line dark:border-line-dark`}
      style={{ color }}
    >
      <span
        aria-hidden="true"
        className={`w-1.5 h-1.5 rounded-full ${glow ? "animate-mood-glow" : ""}`}
        style={{ backgroundColor: color }}
      />
      {label}
    </span>
  );
}

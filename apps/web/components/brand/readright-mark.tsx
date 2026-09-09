type Props = {
  compact?: boolean;
};

export function ReadRightMark({ compact = false }: Props) {
  return (
    <div className="flex items-center gap-3" aria-label="ReadRight">
      <div className="relative grid h-10 w-10 place-items-center rounded-full border-2 border-[var(--rr-ink)] bg-white">
        <span className="absolute -right-1 -top-1 text-[15px] text-[var(--rr-orange)]">✦</span>
        <span className="h-4 w-4 rounded-bl-[70%] rounded-tr-[70%] bg-[linear-gradient(135deg,var(--rr-amber),var(--rr-orange))]" />
      </div>
      {!compact && (
        <div className="leading-none">
          <div className="text-xl font-bold tracking-[-0.04em]">
            Read<span className="text-[var(--rr-orange)]">Right</span>
          </div>
          <div className="mt-1 text-[10px] font-medium tracking-[0.08em] text-[var(--rr-muted)]">
            EVERY CHILD. EVERY LEARNER. EVERY FUTURE.
          </div>
        </div>
      )}
    </div>
  );
}

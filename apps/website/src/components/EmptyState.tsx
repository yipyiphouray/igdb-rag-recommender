export function EmptyState({
  title,
  message,
}: {
  title: string;
  message: string;
}) {
  return (
    <div className="cyber-panel rounded-2xl p-8 text-center">
      <h2 className="text-2xl font-bold text-white">{title}</h2>
      <p className="mt-3 text-slate-300">{message}</p>
    </div>
  );
}

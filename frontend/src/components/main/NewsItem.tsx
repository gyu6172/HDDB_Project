export type NewsItemProps = {
  title: string;
  source: string;
  time: string;
};

export default function NewsItem({ title, source, time }: NewsItemProps) {
  return (
    <article>
      <h3 className="text-xl font-bold text-zinc-900">{title}</h3>
      <p className="mt-2 text-lg font-medium text-zinc-500">
        {source} · {time}
      </p>
    </article>
  );
}

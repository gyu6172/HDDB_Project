import Link from "next/link";

export default function BackButton() {
  return (
    <Link
      href="/main"
      className="flex items-center gap-1 text-label text-muted hover:text-text transition-colors"
    >
      <span>←</span>
      <span>뒤로</span>
    </Link>
  );
}

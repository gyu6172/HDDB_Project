"use client";

import { useRouter } from "next/navigation";

export default function BackButton() {
  const router = useRouter();

  return (
    <button
      onClick={() => router.back()}
      className="flex items-center gap-1 text-label text-muted hover:text-text transition-colors"
    >
      <span>←</span>
      <span>뒤로</span>
    </button>
  );
}

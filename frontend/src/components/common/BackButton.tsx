"use client";

import { useRouter } from "next/navigation";

export default function BackButton() {
  const router = useRouter();

  return (
    <button
      onClick={() => router.back()}
      className="flex items-center gap-1 text-label text-black hover:text-black/70 transition-colors"
    >
      <span>←</span>
      <span>뒤로</span>
    </button>
  );
}

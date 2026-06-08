"use client";

import { useRouter } from "next/navigation";

interface Props {
  href?: string;
}

export default function BackButton({ href }: Props) {
  const router = useRouter();

  return (
    <button
      onClick={() => href ? router.push(href) : router.back()}
      className="flex items-center gap-1 text-label text-black hover:text-black/70 transition-colors"
    >
      <span>←</span>
      <span>뒤로</span>
    </button>
  );
}

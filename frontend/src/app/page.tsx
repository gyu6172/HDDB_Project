import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-bg px-5 py-8">
      <section className="flex min-h-[calc(100vh-4rem)] items-center justify-center rounded-[28px] bg-[linear-gradient(135deg,#b7dcf5_0%,#c7d9ac_55%,#6da7d2_100%)] px-6">
        <div className="flex flex-col items-center text-center">
          <div className="mb-20 flex h-[110px] w-[110px] items-center justify-center rounded-full bg-white/35 text-[56px] shadow-sm sm:h-[140px] sm:w-[140px] sm:text-[72px]">
            🦦
          </div>

          <h1 className="text-[32px] font-bold leading-tight text-white drop-shadow-sm sm:text-[44px]">
            하늘, 땅, 바다의 이야기를
          </h1>

          <p className="mt-5 text-[18px] font-semibold text-white/90 sm:text-[24px]">
            AI가 요약해 전해드릴게요!
          </p>

          <Link
            href="/main"
            className="mt-14 inline-flex h-16 min-w-[180px] items-center justify-center rounded-2xl bg-brand px-10 text-[22px] font-bold text-white shadow-sm transition hover:opacity-90 active:scale-[0.98]"
          >
            시작하기
          </Link>
        </div>
      </section>
    </main>
  );
}

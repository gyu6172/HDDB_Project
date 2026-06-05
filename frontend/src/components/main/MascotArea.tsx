import InteractiveMascot from "@/components/common/InteractiveMascot";

export default function MascotArea() {
  return (
    <div className="flex min-h-[360px] flex-col items-center justify-center gap-8">
      <InteractiveMascot />

      <div className="relative max-w-[260px] rounded-3xl bg-card px-7 py-4 text-center text-lg font-semibold leading-tight text-text shadow-sm before:absolute before:left-1/2 before:top-0 before:size-4 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-45 before:bg-card">
        궁금한 뉴스가
        <br />
        있나요?
      </div>
    </div>
  );
}

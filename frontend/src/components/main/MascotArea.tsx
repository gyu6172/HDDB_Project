export default function MascotArea() {
  return (
    <div className="flex min-h-[360px] flex-col items-center justify-center gap-14">
      <div className="rounded-3xl bg-card px-7 py-4 text-center text-lg font-semibold leading-tight text-text shadow-sm">
        궁금한 뉴스가
        <br />
        있나요?
      </div>

      <div
        aria-hidden="true"
        className="flex size-32 items-center justify-center text-7xl"
      >
        🦦
      </div>
    </div>
  );
}

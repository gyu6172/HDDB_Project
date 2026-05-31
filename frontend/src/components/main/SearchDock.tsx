import { SearchIcon, SendIcon } from "@/components/main/MainIcons";

export default function SearchDock() {
  return (
    <div className="flex h-16 w-full max-w-[440px] items-center gap-4 rounded-full bg-card px-7 shadow-sm">
      <SearchIcon className="size-7 text-muted" />

      <span className="flex-1 text-xl font-semibold text-muted">
        원하는 뉴스를 검색해보세요
      </span>

      <button
        type="button"
        aria-label="검색 전송"
        className="flex size-12 items-center justify-center rounded-full bg-brand text-white"
      >
        <SendIcon />
      </button>
    </div>
  );
}

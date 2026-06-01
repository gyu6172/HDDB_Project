import { MenuIcon, SearchIcon, UserIcon } from "@/components/main/MainIcons";

export default function MainHeader() {
  return (
    <header className="mb-8 flex items-center justify-between">
      <button
        type="button"
        aria-label="메뉴"
        className="flex size-11 items-center justify-center text-text"
      >
        <MenuIcon />
      </button>

      <div className="flex items-center gap-6">
        <button
          type="button"
          aria-label="검색"
          className="flex size-11 items-center justify-center text-text"
        >
          <SearchIcon />
        </button>

        <button
          type="button"
          aria-label="프로필"
          className="flex size-11 items-center justify-center text-text"
        >
          <UserIcon />
        </button>
      </div>
    </header>
  );
}

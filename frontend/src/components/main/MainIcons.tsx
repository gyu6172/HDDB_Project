type IconProps = {
  className?: string;
};

export function MenuIcon({ className = "size-8" }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M5 7h14" />
      <path d="M5 12h14" />
      <path d="M5 17h14" />
    </svg>
  );
}

export function SearchIcon({ className = "size-8" }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.3"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <circle cx="11" cy="11" r="6.5" />
      <path d="m16 16 4 4" />
    </svg>
  );
}

export function UserIcon({ className = "size-8" }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.3"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <circle cx="12" cy="7.5" r="3.2" />
      <path d="M6.5 20c0-3.4 2.2-5.5 5.5-5.5s5.5 2.1 5.5 5.5" />
    </svg>
  );
}

export function CloudIcon({ className = "size-8" }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M7.5 18h10.2a4.1 4.1 0 0 0 .4-8.2 5.8 5.8 0 0 0-11.1-1.6A4.9 4.9 0 0 0 7.5 18Z" />
    </svg>
  );
}

export function MountainIcon({ className = "size-8" }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M3 19 10.4 5.8a1.8 1.8 0 0 1 3.2 0L21 19H3Z" />
      <path d="m8.8 12.2 2 2 2.7-4.3 3.5 6.1" />
    </svg>
  );
}

export function WaveIcon({ className = "size-8" }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M3 13c2.2 0 2.2-6 4.4-6s2.2 10 4.4 10 2.2-8 4.4-8S18.4 13 21 13" />
    </svg>
  );
}

export function SendIcon({ className = "size-6" }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.3"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <path d="M21 3 10 14" />
      <path d="m21 3-7 18-4-7-7-4 18-7Z" />
    </svg>
  );
}

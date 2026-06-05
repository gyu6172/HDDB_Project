"use client";

import { useEffect, useRef, useState } from "react";

type MascotSize = "sm" | "lg";

type InteractiveMascotProps = {
  size?: MascotSize;
  className?: string;
};

type PupilOffset = {
  x: number;
  y: number;
};

type EyeOffsets = {
  left: PupilOffset;
  right: PupilOffset;
};

const CENTERED_EYES: EyeOffsets = {
  left: { x: 0, y: 0 },
  right: { x: 0, y: 0 },
};

const SIZE_CLASS: Record<MascotSize, string> = {
  sm: "h-36 w-32",
  lg: "h-52 w-44",
};

const PUPIL_CLASS: Record<MascotSize, string> = {
  sm: "size-3.5",
  lg: "size-5",
};

export default function InteractiveMascot({
  size = "sm",
  className = "",
}: InteractiveMascotProps) {
  const leftEyeRef = useRef<HTMLDivElement>(null);
  const rightEyeRef = useRef<HTMLDivElement>(null);
  const [eyeOffsets, setEyeOffsets] = useState<EyeOffsets>(CENTERED_EYES);

  useEffect(() => {
    function getEyeOffset(eye: HTMLDivElement | null, event: PointerEvent) {
      if (!eye) return { x: 0, y: 0 };

      const rect = eye.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const deltaX = event.clientX - centerX;
      const deltaY = event.clientY - centerY;
      const distance = Math.hypot(deltaX, deltaY) || 1;
      const maxOffset = 4;

      return {
        x: (deltaX / distance) * maxOffset,
        y: (deltaY / distance) * maxOffset,
      };
    }

    function handlePointerMove(event: PointerEvent) {
      setEyeOffsets({
        left: getEyeOffset(leftEyeRef.current, event),
        right: getEyeOffset(rightEyeRef.current, event),
      });
    }

    window.addEventListener("pointermove", handlePointerMove);

    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
    };
  }, []);

  return (
    <div
      className={`relative ${SIZE_CLASS[size]} ${className}`}
      aria-label="뉴스 탐험 마스코트"
      role="img"
    >
      <div className="absolute left-1/2 top-[1%] h-[8%] w-[38%] -translate-x-1/2 rounded-full bg-brand/80" />
      <div className="absolute left-1/2 top-[9%] h-[25%] w-[9%] -translate-x-1/2 rounded-full bg-brand/80" />
      <div className="absolute left-1/2 top-0 size-[14%] -translate-x-1/2 rounded-full border-[0.25rem] border-brand bg-card" />

      <div className="absolute left-1/2 top-[22%] h-[67%] w-[88%] -translate-x-1/2 rounded-[28%] border-[0.25rem] border-[#5b7fb8] bg-card shadow-sm">
        <div
          ref={leftEyeRef}
          className="absolute left-[14%] top-[29%] size-[29%] rounded-full border border-[#5b7fb8]/40 bg-white shadow-inner"
        >
          <div
            className="absolute left-1/2 top-1/2 transition-transform duration-75"
            style={{
              transform: `translate(${eyeOffsets.left.x}px, ${eyeOffsets.left.y}px)`,
            }}
          >
            <div
              className={`${PUPIL_CLASS[size]} -translate-x-1/2 -translate-y-1/2 rounded-full bg-text after:absolute after:left-[28%] after:top-[16%] after:size-[28%] after:rounded-full after:bg-white`}
            />
          </div>
        </div>

        <div
          ref={rightEyeRef}
          className="absolute right-[14%] top-[29%] size-[29%] rounded-full border border-[#5b7fb8]/40 bg-white shadow-inner"
        >
          <div
            className="absolute left-1/2 top-1/2 transition-transform duration-75"
            style={{
              transform: `translate(${eyeOffsets.right.x}px, ${eyeOffsets.right.y}px)`,
            }}
          >
            <div
              className={`${PUPIL_CLASS[size]} -translate-x-1/2 -translate-y-1/2 rounded-full bg-text after:absolute after:left-[28%] after:top-[16%] after:size-[28%] after:rounded-full after:bg-white`}
            />
          </div>
        </div>

        <div className="absolute left-[18%] top-[63%] h-[10%] w-[18%] rounded-full bg-[#f6a7a7]/55" />
        <div className="absolute right-[18%] top-[63%] h-[10%] w-[18%] rounded-full bg-[#f6a7a7]/55" />
        <div className="absolute left-1/2 top-[72%] h-[4%] w-[25%] -translate-x-1/2 rounded-full bg-[#5b7fb8]" />

        <div className="absolute -right-[10%] bottom-[20%] h-[32%] w-[25%] rotate-6 rounded-md border-2 border-line bg-white">
          <div className="mx-auto mt-[30%] h-0.5 w-[58%] rounded-full bg-muted/70" />
          <div className="mx-auto mt-[14%] h-0.5 w-[58%] rounded-full bg-muted/70" />
          <div className="mx-auto mt-[14%] h-0.5 w-[45%] rounded-full bg-muted/70" />
        </div>
      </div>

      <div className="absolute bottom-0 left-[19%] h-[17%] w-[25%] rounded-b-xl rounded-t-md bg-[#5b7fb8]" />
      <div className="absolute bottom-0 right-[19%] h-[17%] w-[25%] rounded-b-xl rounded-t-md bg-[#5b7fb8]" />
    </div>
  );
}

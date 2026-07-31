"use client";

import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
  lines?: number;
}

export function Skeleton({ className, lines = 1 }: SkeletonProps) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={cn(
            "h-4 bg-gray-700/60 rounded-lg animate-pulse",
            i === lines - 1 && lines > 1 && "w-3/4",
            className
          )}
        />
      ))}
    </div>
  );
}

import { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "error" | "info";
}

const variantClasses = {
  default: "bg-gray-700 text-gray-300",
  success: "bg-emerald-600/20 text-emerald-400 border border-emerald-700/50",
  warning: "bg-amber-600/20 text-amber-400 border border-amber-700/50",
  error: "bg-red-600/20 text-red-400 border border-red-700/50",
  info: "bg-violet-600/20 text-violet-400 border border-violet-700/50",
};

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}

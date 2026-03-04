import type { PropsWithChildren } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-display",
  {
    variants: {
      variant: {
        default: "bg-base-200 text-base-700",
        terracotta: "bg-terracotta-50 text-terracotta-600",
        teal: "bg-teal-50 text-teal-600",
        gold: "bg-gold-50 text-gold-600",
        muted: "bg-base-200/60 text-base-500",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

interface BadgeProps
  extends PropsWithChildren,
    VariantProps<typeof badgeVariants> {
  className?: string;
}

export function Badge({ children, className, variant }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant, className }))}>
      {children}
    </span>
  );
}

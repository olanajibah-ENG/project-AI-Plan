import type { PropsWithChildren } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";

const cardVariants = cva("rounded-2xl transition-all duration-200", {
  variants: {
    variant: {
      default: "bg-white border border-base-200 shadow-card p-6",
      outlined: "bg-white/60 border border-base-300 p-6",
      flat: "bg-base-200/40 p-6",
      highlighted:
        "bg-white border border-terracotta-100 shadow-card shadow-glow p-6",
    },
  },
  defaultVariants: {
    variant: "default",
  },
});

interface CardProps
  extends PropsWithChildren,
    VariantProps<typeof cardVariants> {
  className?: string;
}

export function Card({ children, className, variant }: CardProps) {
  return (
    <section className={cn(cardVariants({ variant, className }))}>
      {children}
    </section>
  );
}

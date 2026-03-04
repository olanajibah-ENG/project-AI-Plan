import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl font-display text-sm transition-all duration-200 outline-none disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]",
  {
    variants: {
      variant: {
        primary:
          "bg-base-900 text-base-100 hover:bg-base-800 shadow-subtle hover:shadow-card",
        secondary:
          "bg-terracotta text-white hover:bg-terracotta-500 shadow-subtle hover:shadow-card",
        teal: "bg-teal text-white hover:bg-teal-600 shadow-subtle hover:shadow-card",
        ghost:
          "bg-transparent text-base-700 hover:bg-base-200/60 hover:text-base-900",
        outline:
          "border border-base-300 bg-transparent text-base-700 hover:bg-base-200/40 hover:border-base-400",
        danger: "bg-red-50 text-red-600 hover:bg-red-100",
      },
      size: {
        sm: "h-9 px-3 text-xs",
        default: "h-11 px-5",
        lg: "h-12 px-7 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

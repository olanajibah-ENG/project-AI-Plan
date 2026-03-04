import * as React from "react";
import { cn } from "@/lib/utils/cn";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          "h-11 w-full rounded-xl border border-base-300 bg-white px-4 font-body text-sm text-base-900 shadow-inner-glow placeholder:text-base-400 outline-none transition-all duration-200 focus:border-terracotta-300 focus:ring-2 focus:ring-terracotta/10 hover:border-base-400",
          className,
        )}
        {...props}
      />
    );
  },
);
Input.displayName = "Input";

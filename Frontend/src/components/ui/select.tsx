import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils/cn";

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div className="relative">
        <select
          ref={ref}
          className={cn(
            "h-11 w-full appearance-none rounded-xl border border-base-300 bg-white pe-10 ps-4 font-body text-sm text-base-900 shadow-inner-glow outline-none transition-all duration-200 focus:border-terracotta-300 focus:ring-2 focus:ring-terracotta/10 hover:border-base-400",
            className,
          )}
          {...props}
        >
          {children}
        </select>
        <ChevronDown className="pointer-events-none absolute end-3 top-1/2 h-4 w-4 -translate-y-1/2 text-base-400" />
      </div>
    );
  },
);
Select.displayName = "Select";

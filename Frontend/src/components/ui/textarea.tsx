import * as React from "react";
import { cn } from "@/lib/utils/cn";

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        ref={ref}
        className={cn(
          "min-h-[6rem] w-full rounded-xl border border-base-300 bg-white px-4 py-3 font-body text-sm text-base-900 shadow-inner-glow placeholder:text-base-400 outline-none transition-all duration-200 focus:border-terracotta-300 focus:ring-2 focus:ring-terracotta/10 hover:border-base-400 resize-none",
          className,
        )}
        {...props}
      />
    );
  },
);
Textarea.displayName = "Textarea";

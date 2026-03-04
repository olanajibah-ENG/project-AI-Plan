import { cn } from "@/lib/utils/cn";

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  id?: string;
  label?: string;
  className?: string;
}

export function Toggle({
  checked,
  onChange,
  id,
  label,
  className,
}: ToggleProps) {
  return (
    <label
      className={cn("flex cursor-pointer items-center gap-3", className)}
      htmlFor={id}
    >
      <div className="relative">
        <input
          id={id}
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          className="peer sr-only"
        />
        <div
          className={cn(
            "h-6 w-11 rounded-full transition-colors duration-200",
            checked ? "bg-teal" : "bg-base-300",
          )}
        />
        <div
          className={cn(
            "absolute top-0.5 h-5 w-5 rounded-full bg-white shadow-subtle transition-all duration-200",
            checked ? "start-[1.375rem]" : "start-0.5",
          )}
        />
      </div>
      {label && (
        <span className="text-sm font-body text-base-700">{label}</span>
      )}
    </label>
  );
}

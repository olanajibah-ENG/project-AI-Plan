import type { PropsWithChildren } from "react";
import { Compass } from "lucide-react";

export function AuthLayout({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen bg-base-100 lg:grid lg:grid-cols-[1.1fr_1fr]">
      {/* Decorative panel */}
      <div className="relative hidden overflow-hidden lg:block">
        <div className="absolute inset-0 bg-gradient-to-br from-base-900 via-base-800 to-base-700" />

        {/* Ambient glow */}
        <div className="absolute -start-20 -top-20 h-80 w-80 rounded-full bg-terracotta/20 blur-[100px]" />
        <div className="absolute -bottom-10 -end-10 h-64 w-64 rounded-full bg-teal/15 blur-[80px]" />

        {/* Dot pattern */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              "radial-gradient(circle, #fff 1px, transparent 1px)",
            backgroundSize: "24px 24px",
          }}
        />

        {/* Content */}
        <div className="relative flex h-full flex-col items-center justify-center p-12 text-center">
          <div className="mb-8 flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 shadow-lg backdrop-blur-sm">
            <Compass className="h-8 w-8 text-terracotta-200" />
          </div>
          <h1 className="mb-4 font-display text-4xl text-white">
            رحلتك الذكية
          </h1>
          <p className="max-w-sm font-body text-lg leading-relaxed text-base-400">
            خطط لرحلتك المثالية بمساعدة الذكاء الاصطناعي. اختر وجهتك، حدد
            ميزانيتك، واترك الباقي علينا.
          </p>

          {/* Decorative dots grid */}
          <div className="absolute bottom-12 grid grid-cols-5 gap-2.5 opacity-15">
            {Array.from({ length: 15 }).map((_, i) => (
              <div key={i} className="h-1.5 w-1.5 rounded-full bg-white" />
            ))}
          </div>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex min-h-screen items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  );
}

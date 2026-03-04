import { Link } from "react-router-dom";
import { Compass } from "lucide-react";
import { Button } from "@/components/ui/button";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-pattern p-6 text-center">
      <div className="relative">
        <span className="font-display text-[10rem] leading-none text-base-200 select-none">
          404
        </span>
        <div className="absolute inset-0 flex items-center justify-center">
          <Compass className="h-14 w-14 text-terracotta/30 animate-float" />
        </div>
      </div>
      <div>
        <h1 className="font-display text-2xl text-base-900">
          الصفحة غير موجودة
        </h1>
        <p className="mt-2 text-base-500">
          يبدو أنك تاهت عن المسار. دعنا نعيدك.
        </p>
      </div>
      <Link to="/trip-planner">
        <Button variant="secondary">العودة للرئيسية</Button>
      </Link>
    </div>
  );
}

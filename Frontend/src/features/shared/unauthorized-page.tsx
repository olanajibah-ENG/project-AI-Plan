import { Link } from "react-router-dom";
import { ShieldX } from "lucide-react";
import { Button } from "@/components/ui/button";

export function UnauthorizedPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-pattern p-6 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-red-50">
        <ShieldX className="h-10 w-10 text-red-400" />
      </div>
      <div>
        <h1 className="font-display text-2xl text-base-900">
          غير مصرح لك بالوصول
        </h1>
        <p className="mt-2 max-w-sm text-base-500">
          هذه الصفحة متاحة فقط للأدوار المخولة. تواصل مع المسؤول إذا كنت تعتقد
          أن هذا خطأ.
        </p>
      </div>
      <Link to="/trip-planner">
        <Button variant="secondary">العودة</Button>
      </Link>
    </div>
  );
}

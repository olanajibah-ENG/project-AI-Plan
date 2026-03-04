import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { Compass, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { AuthLayout } from "@/components/layout/auth-layout";
import { loginSchema, type LoginFormValues } from "@/features/auth/schema";
import { login } from "@/features/auth/auth-api";
import { tokenStorage } from "@/lib/auth/tokenStorage";

export function LoginPage() {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string>("");
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: "", password: "" },
  });

  const mutation = useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      tokenStorage.setAuth(data.tokens.access, data.tokens.refresh, data.user);
      if (data.user.role === "admin") {
        navigate("/admin/destinations", { replace: true });
      } else {
        navigate("/trip-planner", { replace: true });
      }
    },
    onError: () => {
      setServerError("فشل تسجيل الدخول. تحقق من اسم المستخدم وكلمة المرور.");
    },
  });

  return (
    <AuthLayout>
      <div className="animate-fade-up">
        {/* Mobile logo */}
        <div className="mb-8 flex items-center gap-2.5 lg:hidden">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-terracotta to-terracotta-300">
            <Compass className="h-5 w-5 text-white" />
          </div>
          <span className="font-display text-xl text-base-900">رحلتك</span>
        </div>

        <div className="mb-8">
          <h1 className="font-display text-3xl text-base-900">مرحباً بعودتك</h1>
          <p className="mt-2 font-body text-base-500">
            سجل دخولك للمتابعة في التخطيط لرحلتك.
          </p>
        </div>

        <form
          className="space-y-5"
          onSubmit={form.handleSubmit((v) => mutation.mutate(v))}
        >
          <div className="space-y-2">
            <label className="block text-sm font-display text-base-700">
              اسم المستخدم
            </label>
            <Input placeholder="أدخل اسم المستخدم" {...form.register("username")} />
            {form.formState.errors.username && (
              <p className="text-xs text-red-500">
                {form.formState.errors.username.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-display text-base-700">
              كلمة المرور
            </label>
            <Input
              type="password"
              placeholder="أدخل كلمة المرور"
              {...form.register("password")}
            />
            {form.formState.errors.password && (
              <p className="text-xs text-red-500">
                {form.formState.errors.password.message}
              </p>
            )}
          </div>

          {serverError && (
            <div className="rounded-xl bg-red-50 border border-red-100 px-4 py-3 text-sm text-red-600">
              {serverError}
            </div>
          )}

          <Button
            className="w-full"
            size="lg"
            variant="secondary"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                جاري الدخول...
              </>
            ) : (
              "تسجيل الدخول"
            )}
          </Button>
        </form>

        <div className="mt-8 flex items-center gap-3">
          <div className="h-px flex-1 bg-base-200" />
          <span className="text-xs text-base-400 font-display">أو</span>
          <div className="h-px flex-1 bg-base-200" />
        </div>

        <p className="mt-6 text-center text-sm text-base-500">
          لا تمتلك حساباً؟{" "}
          <Link
            className="font-display text-terracotta transition hover:text-terracotta-500"
            to="/register"
          >
            إنشاء حساب جديد
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
}

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { Compass, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { AuthLayout } from "@/components/layout/auth-layout";
import {
  registerSchema,
  type RegisterFormValues,
} from "@/features/auth/schema";
import { register } from "@/features/auth/auth-api";

export function RegisterPage() {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string>("");
  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { username: "", email: "", password: "" },
  });

  const mutation = useMutation({
    mutationFn: register,
    onSuccess: () => navigate("/login", { replace: true }),
    onError: () =>
      setServerError("تعذر إنشاء الحساب. ربما اسم المستخدم مستخدم مسبقاً."),
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
          <h1 className="font-display text-3xl text-base-900">إنشاء حساب</h1>
          <p className="mt-2 font-body text-base-500">
            انضم إلينا وابدأ التخطيط لرحلتك المثالية.
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
            <Input
              placeholder="اختر اسم مستخدم"
              {...form.register("username")}
            />
            {form.formState.errors.username && (
              <p className="text-xs text-red-500">
                {form.formState.errors.username.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-display text-base-700">
              البريد الإلكتروني
            </label>
            <Input
              type="email"
              placeholder="example@email.com"
              {...form.register("email")}
            />
            {form.formState.errors.email && (
              <p className="text-xs text-red-500">
                {form.formState.errors.email.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-display text-base-700">
              كلمة المرور
            </label>
            <Input
              type="password"
              placeholder="8 أحرف على الأقل"
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
                جاري الإنشاء...
              </>
            ) : (
              "إنشاء الحساب"
            )}
          </Button>
        </form>

        <div className="mt-8 flex items-center gap-3">
          <div className="h-px flex-1 bg-base-200" />
          <span className="text-xs text-base-400 font-display">أو</span>
          <div className="h-px flex-1 bg-base-200" />
        </div>

        <p className="mt-6 text-center text-sm text-base-500">
          لديك حساب؟{" "}
          <Link
            className="font-display text-terracotta transition hover:text-terracotta-500"
            to="/login"
          >
            سجل الدخول
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
}

import { z } from "zod";

export const loginSchema = z.object({
  username: z.string().min(3, "اسم المستخدم مطلوب"),
  password: z.string().min(8, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"),
});

export const registerSchema = z.object({
  username: z.string().min(3, "اسم المستخدم مطلوب"),
  email: z.string().email("أدخل بريد إلكتروني صالح"),
  password: z.string().min(8, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"),
});

export type LoginFormValues = z.infer<typeof loginSchema>;
export type RegisterFormValues = z.infer<typeof registerSchema>;

import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Formato de correo no válido."),
  password: z.string().min(6, "La contraseña es obligatoria."),
});

export type LoginFormValues = z.infer<typeof loginSchema>;

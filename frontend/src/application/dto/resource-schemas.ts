import { z } from "zod";

export const registerLotSchema = z.object({
  code: z.string().trim().min(1, "El codigo es obligatorio."),
  mineral: z.string().trim().min(1, "El mineral es obligatorio."),
  quantity: z.coerce.number().positive("La cantidad debe ser mayor que 0."),
  unit: z.string().trim().min(1, "La unidad es obligatoria."),
  observation: z.string().optional(),
});

export const custodySchema = z.object({
  lot_id: z.string().trim().min(1, "El lote es obligatorio."),
  origin: z.string().trim().min(1, "El origen es obligatorio."),
  destination: z.string().trim().min(1, "El destino es obligatorio."),
  quantity: z.coerce.number().positive("La cantidad debe ser mayor que 0."),
  notes: z.string().optional(),
});

export const transportSchema = z.object({
  lot_id: z.string().trim().min(1, "El lote es obligatorio."),
  vehicle: z.string().trim().min(1, "El vehiculo es obligatorio."),
  plate: z.string().trim().min(1, "La placa es obligatoria."),
  driver: z.string().trim().min(1, "El conductor es obligatorio."),
  assigned_to: z.string().trim().min(1, "Debes seleccionar un transportista.").optional(),
  origin: z.string().optional(),
  destination: z.string().optional(),
});

export const transportEventSchema = z.object({
  description: z.string().trim().min(2, "La descripcion es obligatoria."),
  event_type: z.string().trim().min(1, "El tipo de evento es obligatorio."),
  is_incident: z.coerce.boolean().optional().default(false),
});

export const receptionSchema = z.object({
  lot_id: z.string().trim().min(1, "El lote es obligatorio."),
  declared_quantity: z.coerce.number().positive(),
  received_quantity: z.coerce.number().positive(),
  unit: z.string().trim().min(1),
  responsible: z.string().trim().min(1),
  notes: z.string().optional(),
});

export const weighingSchema = z.object({
  lot_id: z.string().trim().min(1, "El lote es obligatorio."),
  weight: z.coerce.number().positive(),
  unit: z.string().trim().min(1),
  instrument: z.string().trim().min(1),
  responsible: z.string().trim().min(1),
  notes: z.string().optional(),
});

export function parseForm<T>(
  schema: z.ZodType<T>,
  values: Record<string, unknown>,
): { ok: true; data: T } | { ok: false; errors: Record<string, string>; message: string } {
  const result = schema.safeParse(values);
  if (result.success) return { ok: true, data: result.data };
  const errors: Record<string, string> = {};
  for (const issue of result.error.issues) {
    const key = String(issue.path[0] ?? "_form");
    if (!errors[key]) errors[key] = issue.message;
  }
  return {
    ok: false,
    errors,
    message: Object.values(errors)[0] ?? "Revisa los datos del formulario.",
  };
}

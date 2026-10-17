export type UserRole =
  | "producer"
  | "carrier"
  | "receiver"
  | "transporter"
  | "plant_manager"
  | "control_center"
  | "supervisor"
  | "admin"
  | "auditor";

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  role_label: string;
  organization_id: string;
  status: string;
  invitation_status: string;
  permissions: string[];
}

export interface PageResult<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
}

export interface Lot {
  id: string;
  code: string;
  mineral: string;
  quantity: number;
  unit: string;
  status: string;
  created_at: string;
  qr_payload?: string | null;
  observation?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

export const roleLabels: Record<string, string> = {
  admin: "Administrador",
  auditor: "Auditor",
  producer: "Productor",
  carrier: "Transportista",
  transporter: "Transportista",
  receiver: "Receptor",
  plant_manager: "Receptor",
  supervisor: "Supervisor",
  control_center: "Supervisor",
};

export const statusLabels: Record<string, string> = {
  registered: "Registrado",
  inTransit: "En custodia",
  transferred: "Transferido",
  received: "Recibido",
  closed: "Cerrado",
  new: "Nueva",
  in_review: "En revisión",
  attended: "Atendida",
  pending: "Pendiente",
  active: "Activo",
  inactive: "Inactivo",
  expired: "Invitación expirada",
  assigned: "Asignado",
  in_progress: "En curso",
  arrived: "En destino",
  delivered: "Entregado",
  cancelled: "Cancelado",
  confirmed: "Confirmada",
  completed: "Completada",
  within_tolerance: "Dentro de tolerancia",
  review_required: "Revisión requerida",
  insufficient_data: "Sin información suficiente",
  low: "Baja",
  medium: "Media",
  high: "Alta",
  critical: "Crítica",
  review_signal: "Señal para revisión",
  none: "Sin señal",
};

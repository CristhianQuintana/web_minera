-- WEB_MINERA | DATASET SIMULADO DE PRUEBAS (220+ lotes)
-- Genera 220 lotes y registros relacionados para la organización Cooperativa piloto.
-- Ejecutar en Supabase > SQL Editor, sobre la BD correcta (p. ej. prod Render:
--   https://kwygymkrlwthddjijdyr.supabase.co  o el proyecto que uses).
-- Idempotente: puede ejecutarse varias veces sin duplicar por client_operation_id / code.
-- IMPORTANTE: datos ficticios. No representan operaciones mineras reales.
--
-- Estados de lote alineados al dominio:
--   registered | inTransit | transferred | received | closed
--
-- Prefijo: asegura columnas/tablas web si el proyecto solo tiene el esquema base.

begin;

-- Columnas de profiles añadidas en migración web (pueden faltar en proyectos antiguos).
alter table public.profiles
  add column if not exists email text,
  add column if not exists last_activity_at timestamptz,
  add column if not exists invitation_status text;

update public.profiles
set invitation_status = 'active'
where invitation_status is null;

do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'profiles_invitation_status_check'
  ) then
    alter table public.profiles
      add constraint profiles_invitation_status_check
      check (invitation_status in ('pending', 'active', 'inactive', 'expired'));
  end if;
end $$;

alter table public.custody_transfers
  add column if not exists created_by uuid references auth.users (id),
  add column if not exists status text,
  add column if not exists responsible text;

update public.custody_transfers set status = 'completed' where status is null;

alter table public.transports
  add column if not exists code text,
  add column if not exists origin text,
  add column if not exists destination text,
  add column if not exists assigned_to uuid references auth.users (id),
  add column if not exists declared_quantity numeric;

alter table public.audit_log
  add column if not exists context jsonb,
  add column if not exists organization_id uuid references public.organizations (id);

-- Tablas web usadas por el dataset (no-op si ya existen).
create table if not exists public.tolerance_rules (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations (id),
  rule_key text not null,
  name text not null,
  value numeric not null,
  unit text not null,
  version integer not null default 1,
  is_active boolean not null default true,
  effective_from timestamptz not null default now(),
  effective_to timestamptz,
  created_at timestamptz not null default now(),
  unique (organization_id, rule_key, version)
);

create table if not exists public.receptions (
  id uuid primary key default gen_random_uuid(),
  client_operation_id uuid not null unique,
  lot_id uuid not null references public.lots (id),
  declared_quantity numeric not null check (declared_quantity > 0),
  received_quantity numeric not null check (received_quantity > 0),
  unit text not null,
  occurred_at timestamptz not null,
  responsible text not null,
  status text not null default 'confirmed',
  notes text,
  latitude double precision,
  longitude double precision,
  location_accuracy double precision,
  location_captured_at timestamptz,
  created_by uuid references auth.users (id),
  created_at timestamptz not null default now()
);

create table if not exists public.weighings (
  id uuid primary key default gen_random_uuid(),
  client_operation_id uuid not null unique,
  lot_id uuid not null references public.lots (id),
  reception_id uuid references public.receptions (id),
  weight numeric not null check (weight > 0),
  unit text not null,
  occurred_at timestamptz not null,
  instrument text not null,
  responsible text not null,
  notes text,
  latitude double precision,
  longitude double precision,
  location_accuracy double precision,
  location_captured_at timestamptz,
  created_by uuid references auth.users (id),
  created_at timestamptz not null default now()
);

create table if not exists public.mass_balances (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations (id),
  lot_id uuid not null references public.lots (id),
  origin_quantity numeric not null,
  received_quantity numeric,
  difference numeric,
  difference_percent numeric,
  tolerance_value numeric,
  tolerance_unit text,
  tolerance_rule_id uuid references public.tolerance_rules (id),
  tolerance_version integer,
  status text not null default 'insufficient_data' check (
    status in ('within_tolerance', 'review_required', 'insufficient_data')
  ),
  calculated_at timestamptz not null default now(),
  unique (lot_id)
);

create table if not exists public.alerts (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations (id),
  lot_id uuid references public.lots (id),
  severity text not null check (severity in ('low', 'medium', 'high', 'critical')),
  alert_type text not null,
  title text not null,
  summary text,
  reason text,
  status text not null default 'new' check (
    status in ('new', 'in_review', 'attended', 'closed')
  ),
  assigned_to uuid references auth.users (id),
  rule_applied text,
  ml_inference_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  organization_id uuid references public.organizations (id),
  title text not null,
  body text,
  type text not null default 'operational',
  resource_type text,
  resource_id text,
  read_at timestamptz,
  created_at timestamptz not null default now()
);

DO $$
DECLARE
    v_user_id uuid;
    v_org_id uuid := 'e857fa80-1678-4b27-b80f-c38f471a8931';
    v_operation_id uuid;
    v_lot_count int := 220;
BEGIN
    -- Validar usuario real de Supabase Auth.
    SELECT id INTO v_user_id
    FROM auth.users
    WHERE lower(email) = lower('cristhian@gmail.com')
    LIMIT 1;

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'No existe el usuario cristhian@gmail.com en auth.users. Ajusta el correo en este script.';
    END IF;

    -- Asegurar organización piloto.
    INSERT INTO public.organizations (id, name)
    VALUES (v_org_id, 'Cooperativa piloto')
    ON CONFLICT (id) DO NOTHING;

    -- Asegurar operación minera de prueba.
    INSERT INTO public.mining_operations (organization_id, name, status)
    SELECT v_org_id, 'Operación El Alto - DATASET DEMO', 'active'
    WHERE NOT EXISTS (
        SELECT 1 FROM public.mining_operations
        WHERE organization_id = v_org_id
          AND name = 'Operación El Alto - DATASET DEMO'
    );

    SELECT id INTO v_operation_id
    FROM public.mining_operations
    WHERE organization_id = v_org_id
      AND name = 'Operación El Alto - DATASET DEMO'
    ORDER BY created_at
    LIMIT 1;

    -- Crear/actualizar el perfil del usuario como administrador de la organización.
    INSERT INTO public.profiles
        (id, full_name, role, organization_id, status, email, invitation_status)
    VALUES
        (v_user_id, 'Administrador WEB MINERA', 'admin', v_org_id, 'active',
         'cristhian@gmail.com', 'active')
    ON CONFLICT (id) DO UPDATE
       SET full_name = EXCLUDED.full_name,
           role = 'admin',
           organization_id = v_org_id,
           status = 'active',
           email = EXCLUDED.email,
           invitation_status = 'active',
           updated_at = now();

    -- Tolerancia por defecto (si no existe).
    INSERT INTO public.tolerance_rules (
        organization_id, rule_key, name, value, unit, version, is_active
    )
    SELECT v_org_id, 'mass_balance_percent', 'Tolerancia de balance de masas', 3, 'percent', 1, true
    WHERE NOT EXISTS (
        SELECT 1 FROM public.tolerance_rules
        WHERE organization_id = v_org_id
          AND rule_key = 'mass_balance_percent'
          AND version = 1
    );

    -- 220 LOTES SIMULADOS. Código estable para permitir reejecución.
    INSERT INTO public.lots (
        client_operation_id, organization_id, mining_operation_id,
        code, mineral, quantity, unit, status,
        latitude, longitude, location_accuracy, location_captured_at,
        qr_payload, observation, created_by, created_at, updated_at
    )
    SELECT
        md5('web-minera-demo-lot-' || g)::uuid,
        v_org_id,
        v_operation_id,
        'DEMO-LOTE-' || lpad(g::text, 3, '0'),
        (ARRAY['Oro', 'Plata', 'Cobre', 'Zinc', 'Plomo'])[((g - 1) % 5) + 1],
        round((120 + ((g * 137) % 4800) + (g % 7) * 0.35)::numeric, 2),
        'kg',
        (ARRAY['registered', 'inTransit', 'transferred', 'received', 'closed'])[((g - 1) % 5) + 1],
        -12.05 + ((g % 10) * 0.006),
        -75.20 + (((g * 7) % 10) * 0.006),
        5.0 + (g % 12),
        now() - (g || ' days')::interval,
        'WEBMINERA-DEMO:DEMO-LOTE-' || lpad(g::text, 3, '0'),
        'REGISTRO SIMULADO PARA PRUEBAS DE WEB_MINERA. No es una operación real.',
        v_user_id,
        now() - (g || ' days')::interval,
        now() - (g || ' days')::interval
    FROM generate_series(1, v_lot_count) AS g
    ON CONFLICT (organization_id, code) DO NOTHING;

    -- EVENTO DE REGISTRO PARA CADA LOTE.
    INSERT INTO public.lot_events (
        client_operation_id, lot_id, event_type, occurred_at,
        user_id, notes, latitude, longitude, location_accuracy, location_captured_at
    )
    SELECT
        md5('web-minera-demo-lot-event-' || l.id::text)::uuid,
        l.id,
        'lot_registered',
        l.created_at,
        v_user_id,
        'Evento inicial generado por dataset simulado.',
        l.latitude, l.longitude, l.location_accuracy, l.location_captured_at
    FROM public.lots l
    WHERE l.organization_id = v_org_id
      AND l.code LIKE 'DEMO-LOTE-%'
    ON CONFLICT (client_operation_id) DO NOTHING;

    -- TRANSFERENCIA DE CUSTODIA PARA CADA LOTE.
    INSERT INTO public.custody_transfers (
        client_operation_id, lot_id, origin, destination,
        quantity, occurred_at, notes, latitude, longitude,
        location_accuracy, location_captured_at, created_by, status, responsible
    )
    SELECT
        md5('web-minera-demo-transfer-' || l.id::text)::uuid,
        l.id,
        'Unidad minera El Alto',
        CASE WHEN (row_number() OVER (ORDER BY l.code))::int % 2 = 0
             THEN 'Centro de acopio Junín' ELSE 'Planta de procesamiento piloto' END,
        l.quantity,
        l.created_at + interval '2 hours',
        'Transferencia ficticia para validación de trazabilidad.',
        l.latitude, l.longitude, l.location_accuracy, l.location_captured_at,
        v_user_id, 'completed', 'Responsable de prueba'
    FROM public.lots l
    WHERE l.organization_id = v_org_id
      AND l.code LIKE 'DEMO-LOTE-%'
    ON CONFLICT (client_operation_id) DO NOTHING;

    -- TRANSPORTE PARA CADA LOTE.
    INSERT INTO public.transports (
        client_operation_id, lot_id, vehicle, plate, driver, status,
        started_at, ended_at, notes, latitude, longitude,
        location_accuracy, location_captured_at,
        code, origin, destination, assigned_to, declared_quantity
    )
    SELECT
        md5('web-minera-demo-transport-' || l.id::text)::uuid,
        l.id,
        (ARRAY['Volquete 10 m3', 'Camión plataforma', 'Camión baranda'])[((row_number() OVER (ORDER BY l.code))::int - 1) % 3 + 1],
        'D' || lpad(((row_number() OVER (ORDER BY l.code))::int)::text, 3, '0') || '-DEMO',
        (ARRAY['Carlos Rojas', 'Miguel Torres', 'Luis Quispe', 'Pedro Huamán'])[((row_number() OVER (ORDER BY l.code))::int - 1) % 4 + 1],
        CASE WHEN l.status = 'registered' THEN 'pending'
             WHEN l.status = 'inTransit' THEN 'in_progress'
             ELSE 'completed' END,
        l.created_at + interval '3 hours',
        CASE WHEN l.status IN ('received', 'closed', 'transferred')
             THEN l.created_at + interval '8 hours' ELSE NULL END,
        'Transporte ficticio del dataset de demostración.',
        l.latitude, l.longitude, l.location_accuracy, l.location_captured_at,
        'DEMO-TR-' || lpad(((row_number() OVER (ORDER BY l.code))::int)::text, 3, '0'),
        'Unidad minera El Alto', 'Centro de acopio Junín',
        v_user_id, l.quantity
    FROM public.lots l
    WHERE l.organization_id = v_org_id
      AND l.code LIKE 'DEMO-LOTE-%'
    ON CONFLICT (client_operation_id) DO NOTHING;

    -- EVENTO ASOCIADO A CADA TRANSPORTE.
    INSERT INTO public.transport_events (
        client_operation_id, transport_id, description, occurred_at,
        is_incident, latitude, longitude, location_accuracy, location_captured_at
    )
    SELECT
        md5('web-minera-demo-transport-event-' || t.id::text)::uuid,
        t.id,
        CASE WHEN t.status = 'in_progress'
             THEN 'Vehículo en ruta (evento simulado)'
             ELSE 'Salida registrada (evento simulado)' END,
        t.started_at,
        false, t.latitude, t.longitude, t.location_accuracy, t.location_captured_at
    FROM public.transports t
    JOIN public.lots l ON l.id = t.lot_id
    WHERE l.organization_id = v_org_id
      AND l.code LIKE 'DEMO-LOTE-%'
    ON CONFLICT (client_operation_id) DO NOTHING;

    -- RECEPCIÓN PARA LOTES RECIBIDOS O CERRADOS.
    INSERT INTO public.receptions (
        client_operation_id, lot_id, declared_quantity, received_quantity,
        unit, occurred_at, responsible, status, notes,
        latitude, longitude, location_accuracy, location_captured_at, created_by
    )
    SELECT
        md5('web-minera-demo-reception-' || l.id::text)::uuid,
        l.id,
        l.quantity,
        round((l.quantity * (1 - (((row_number() OVER (ORDER BY l.code))::int % 4) * 0.002)))::numeric, 2),
        l.unit,
        l.created_at + interval '8 hours',
        'Responsable de recepción DEMO',
        'confirmed',
        'Recepción ficticia para pruebas. Diferencia calculada de forma simulada.',
        l.latitude, l.longitude, l.location_accuracy, l.location_captured_at,
        v_user_id
    FROM public.lots l
    WHERE l.organization_id = v_org_id
      AND l.code LIKE 'DEMO-LOTE-%'
      AND l.status IN ('received', 'closed')
    ON CONFLICT (client_operation_id) DO NOTHING;

    -- PESAJES VINCULADOS A LAS RECEPCIONES CREADAS.
    INSERT INTO public.weighings (
        client_operation_id, lot_id, reception_id, weight, unit,
        occurred_at, instrument, responsible, notes,
        latitude, longitude, location_accuracy, location_captured_at, created_by
    )
    SELECT
        md5('web-minera-demo-weighing-' || r.id::text)::uuid,
        r.lot_id,
        r.id,
        r.received_quantity,
        r.unit,
        r.occurred_at + interval '10 minutes',
        'Balanza industrial DEMO',
        'Operador de balanza DEMO',
        'Pesaje ficticio asociado a recepción simulada.',
        r.latitude, r.longitude, r.location_accuracy, r.location_captured_at,
        v_user_id
    FROM public.receptions r
    JOIN public.lots l ON l.id = r.lot_id
    WHERE l.organization_id = v_org_id
      AND l.code LIKE 'DEMO-LOTE-%'
    ON CONFLICT (client_operation_id) DO NOTHING;

    -- BALANCE DE MASAS PARA TODOS LOS LOTES DEMO.
    INSERT INTO public.mass_balances (
        organization_id, lot_id, origin_quantity, received_quantity,
        difference, difference_percent, tolerance_value, tolerance_unit,
        tolerance_version, status, calculated_at
    )
    SELECT
        l.organization_id,
        l.id,
        l.quantity,
        r.received_quantity,
        CASE WHEN r.id IS NULL THEN NULL ELSE round(l.quantity - r.received_quantity, 2) END,
        CASE WHEN r.id IS NULL OR l.quantity = 0 THEN NULL
             ELSE round(((l.quantity - r.received_quantity) / l.quantity) * 100, 2) END,
        3, 'percent', 1,
        CASE WHEN r.id IS NULL THEN 'insufficient_data'
             WHEN abs(((l.quantity - r.received_quantity) / l.quantity) * 100) <= 3
             THEN 'within_tolerance' ELSE 'review_required' END,
        now()
    FROM public.lots l
    LEFT JOIN public.receptions r ON r.lot_id = l.id
    WHERE l.organization_id = v_org_id
      AND l.code LIKE 'DEMO-LOTE-%'
    ON CONFLICT (lot_id) DO UPDATE SET
        received_quantity = EXCLUDED.received_quantity,
        difference = EXCLUDED.difference,
        difference_percent = EXCLUDED.difference_percent,
        status = EXCLUDED.status,
        calculated_at = now();

    -- 40 ALERTAS FICTICIAS.
    INSERT INTO public.alerts (
        organization_id, lot_id, severity, alert_type, title,
        summary, reason, status, assigned_to, rule_applied
    )
    SELECT
        l.organization_id,
        l.id,
        CASE WHEN n % 5 = 0 THEN 'high'
             WHEN n % 3 = 0 THEN 'medium' ELSE 'low' END,
        CASE WHEN n % 2 = 0 THEN 'mass_balance' ELSE 'traceability' END,
        CASE WHEN n % 2 = 0 THEN 'Revisión de balance de masas (DEMO)'
             ELSE 'Validación de trazabilidad (DEMO)' END,
        'Alerta generada exclusivamente para probar el módulo de alertas.',
        'Dato simulado; requiere revisión del operador en entorno de pruebas.',
        CASE WHEN n % 4 = 0 THEN 'in_review'
             WHEN n % 4 = 1 THEN 'attended' ELSE 'new' END,
        v_user_id,
        'DEMO_DATASET_RULE'
    FROM (
        SELECT l.*, row_number() OVER (ORDER BY l.code)::int AS n
        FROM public.lots l
        WHERE l.organization_id = v_org_id
          AND l.code LIKE 'DEMO-LOTE-%'
    ) l
    WHERE l.n <= 40
      AND NOT EXISTS (
          SELECT 1 FROM public.alerts a
          WHERE a.lot_id = l.id
            AND a.rule_applied = 'DEMO_DATASET_RULE'
      );

    -- 30 NOTIFICACIONES PARA EL ADMIN.
    INSERT INTO public.notifications (
        user_id, organization_id, title, body, type, resource_type, resource_id, created_at
    )
    SELECT
        v_user_id,
        v_org_id,
        'Notificación DEMO #' || n,
        'Aviso simulado del dataset WEB_MINERA para pruebas de UI.',
        CASE WHEN n % 3 = 0 THEN 'alert' ELSE 'operational' END,
        'lot',
        (SELECT id::text FROM public.lots
         WHERE organization_id = v_org_id AND code = 'DEMO-LOTE-' || lpad(n::text, 3, '0')
         LIMIT 1),
        now() - (n || ' hours')::interval
    FROM generate_series(1, 30) AS n
    WHERE NOT EXISTS (
        SELECT 1 FROM public.notifications x
        WHERE x.user_id = v_user_id
          AND x.title = 'Notificación DEMO #' || n
    );

    -- AUDITORÍA (50 eventos) asociada a lotes DEMO.
    INSERT INTO public.audit_log (
        user_id, action, entity, entity_id, result, organization_id, context, created_at
    )
    SELECT
        v_user_id,
        CASE WHEN n % 2 = 0 THEN 'view_lot' ELSE 'list_lots' END,
        'lot',
        l.id::text,
        'success',
        v_org_id,
        jsonb_build_object('source', 'DEMO_DATASET', 'index', n),
        now() - (n || ' hours')::interval
    FROM (
        SELECT l.id, row_number() OVER (ORDER BY l.code)::int AS n
        FROM public.lots l
        WHERE l.organization_id = v_org_id
          AND l.code LIKE 'DEMO-LOTE-%'
    ) l
    WHERE l.n <= 50
      AND NOT EXISTS (
          SELECT 1 FROM public.audit_log a
          WHERE a.organization_id = v_org_id
            AND a.entity_id = l.id::text
            AND a.context->>'source' = 'DEMO_DATASET'
      );

END $$;

-- Resumen de registros generados.
SELECT 'lots' AS tabla, count(*) AS registros
FROM public.lots
WHERE code LIKE 'DEMO-LOTE-%'
UNION ALL
SELECT 'lot_events', count(*)
FROM public.lot_events e
JOIN public.lots l ON l.id = e.lot_id
WHERE l.code LIKE 'DEMO-LOTE-%'
UNION ALL
SELECT 'custody_transfers', count(*)
FROM public.custody_transfers c
JOIN public.lots l ON l.id = c.lot_id
WHERE l.code LIKE 'DEMO-LOTE-%'
UNION ALL
SELECT 'transports', count(*)
FROM public.transports t
JOIN public.lots l ON l.id = t.lot_id
WHERE l.code LIKE 'DEMO-LOTE-%'
UNION ALL
SELECT 'transport_events', count(*)
FROM public.transport_events e
JOIN public.transports t ON t.id = e.transport_id
JOIN public.lots l ON l.id = t.lot_id
WHERE l.code LIKE 'DEMO-LOTE-%'
UNION ALL
SELECT 'receptions', count(*)
FROM public.receptions r
JOIN public.lots l ON l.id = r.lot_id
WHERE l.code LIKE 'DEMO-LOTE-%'
UNION ALL
SELECT 'weighings', count(*)
FROM public.weighings w
JOIN public.lots l ON l.id = w.lot_id
WHERE l.code LIKE 'DEMO-LOTE-%'
UNION ALL
SELECT 'mass_balances', count(*)
FROM public.mass_balances m
JOIN public.lots l ON l.id = m.lot_id
WHERE l.code LIKE 'DEMO-LOTE-%'
UNION ALL
SELECT 'alerts', count(*)
FROM public.alerts
WHERE rule_applied = 'DEMO_DATASET_RULE'
UNION ALL
SELECT 'notifications', count(*)
FROM public.notifications
WHERE title LIKE 'Notificación DEMO #%'
UNION ALL
SELECT 'audit_log', count(*)
FROM public.audit_log
WHERE context->>'source' = 'DEMO_DATASET';

COMMIT;

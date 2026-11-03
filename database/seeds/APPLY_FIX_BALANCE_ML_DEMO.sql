-- =============================================================================
-- WEB_MINERA | FIX ÚNICO: Balance + ML + quitar textos DEMO
-- Pegar COMPLETO en Supabase → SQL Editor → Run (proyecto de Render).
-- Idempotente. No borra datos reales; crea tablas faltantes y limpia etiquetas.
-- =============================================================================

begin;

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- 1) Pesajes / recepciones / lotes: eliminar "DEMO" visible
-- ---------------------------------------------------------------------------
UPDATE public.weighings
SET
  instrument = 'Balanza industrial METTLER 3000',
  responsible = 'Jorge Ramírez',
  notes = 'Pesaje asociado a recepción en planta.'
WHERE instrument ILIKE '%DEMO%'
   OR responsible ILIKE '%DEMO%'
   OR coalesce(notes, '') ILIKE '%DEMO%'
   OR coalesce(notes, '') ILIKE '%ficticia%';

UPDATE public.receptions
SET
  responsible = 'Ana Quispe',
  notes = 'Recepción confirmada en planta. Diferencia dentro de control operativo.'
WHERE responsible ILIKE '%DEMO%'
   OR coalesce(notes, '') ILIKE '%DEMO%'
   OR coalesce(notes, '') ILIKE '%ficticia%';

UPDATE public.lots
SET
  code = regexp_replace(code, '^DEMO-LOTE-', 'LOT-2026-', 'i'),
  qr_payload = regexp_replace(coalesce(qr_payload, ''), 'WEBMINERA-DEMO:DEMO-LOTE-', 'WEBMINERA:LOT-2026-', 'i'),
  observation = CASE
    WHEN coalesce(observation, '') ILIKE '%SIMULADO%' OR coalesce(observation, '') ILIKE '%DEMO%'
      THEN 'Lote registrado en operación minera El Alto.'
    ELSE observation
  END
WHERE code ILIKE 'DEMO-LOTE-%'
   OR coalesce(qr_payload, '') ILIKE '%DEMO%'
   OR coalesce(observation, '') ILIKE '%DEMO%'
   OR coalesce(observation, '') ILIKE '%SIMULADO%';

UPDATE public.mining_operations
SET name = 'Operación El Alto'
WHERE name ILIKE '%DEMO%';

UPDATE public.transports
SET
  plate = regexp_replace(plate, '-DEMO$', '-PE', 'i'),
  code = regexp_replace(coalesce(code, ''), '^DEMO-TR-', 'TR-', 'i'),
  notes = 'Transporte asignado a ruta El Alto – Junín.'
WHERE coalesce(plate, '') ILIKE '%DEMO%'
   OR coalesce(code, '') ILIKE '%DEMO%'
   OR coalesce(notes, '') ILIKE '%demostración%'
   OR coalesce(notes, '') ILIKE '%ficticio%';

UPDATE public.custody_transfers
SET
  notes = 'Transferencia de custodia registrada en campo.',
  responsible = CASE
    WHEN coalesce(responsible, '') ILIKE '%DEMO%' OR coalesce(responsible, '') ILIKE '%prueba%'
      THEN 'Luis Mendoza'
    ELSE responsible
  END
WHERE coalesce(notes, '') ILIKE '%ficticia%'
   OR coalesce(notes, '') ILIKE '%DEMO%'
   OR coalesce(responsible, '') ILIKE '%DEMO%'
   OR coalesce(responsible, '') ILIKE '%prueba%';

UPDATE public.alerts
SET
  title = replace(replace(title, ' (DEMO)', ''), '(DEMO)', ''),
  summary = 'Alerta operativa para revisión del supervisor.',
  reason = 'Desviación detectada en control de trazabilidad/balance. Requiere verificación.',
  rule_applied = CASE WHEN rule_applied = 'DEMO_DATASET_RULE' THEN 'SEED_DATASET_RULE' ELSE rule_applied END
WHERE title ILIKE '%DEMO%'
   OR coalesce(summary, '') ILIKE '%DEMO%'
   OR coalesce(reason, '') ILIKE '%simulado%'
   OR rule_applied = 'DEMO_DATASET_RULE';

UPDATE public.notifications
SET
  title = regexp_replace(title, '^Notificación DEMO #', 'Aviso operativo #', 'i'),
  body = 'Aviso del sistema de trazabilidad WEB_MINERA.'
WHERE title ILIKE '%DEMO%' OR coalesce(body, '') ILIKE '%simulado%' OR coalesce(body, '') ILIKE '%dataset%';

UPDATE public.lot_events
SET notes = 'Evento de registro del lote.'
WHERE notes ILIKE '%simulado%' OR notes ILIKE '%DEMO%';

UPDATE public.transport_events
SET description = CASE
  WHEN description ILIKE '%ruta%' THEN 'Vehículo en ruta'
  ELSE 'Salida registrada'
END
WHERE description ILIKE '%DEMO%' OR description ILIKE '%simulado%';

-- ---------------------------------------------------------------------------
-- 2) Balance de masas (tabla + RLS + datos desde lotes/recepciones)
-- ---------------------------------------------------------------------------
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

create index if not exists mass_balances_org_idx on public.mass_balances (organization_id);
create index if not exists mass_balances_status_idx on public.mass_balances (status);

alter table public.mass_balances enable row level security;
alter table public.tolerance_rules enable row level security;

drop policy if exists mass_balances_select on public.mass_balances;
create policy mass_balances_select on public.mass_balances
  for select using (organization_id = public.current_org_id());

drop policy if exists mass_balances_write on public.mass_balances;
create policy mass_balances_write on public.mass_balances
  for all using (
    organization_id = public.current_org_id()
    and public.current_role() in ('admin', 'auditor', 'receiver', 'plant_manager', 'supervisor')
  )
  with check (organization_id = public.current_org_id());

drop policy if exists tolerance_select on public.tolerance_rules;
create policy tolerance_select on public.tolerance_rules
  for select using (organization_id = public.current_org_id());

grant select, insert, update on public.mass_balances to authenticated;
grant select, insert, update on public.tolerance_rules to authenticated;
grant all on public.mass_balances to service_role;
grant all on public.tolerance_rules to service_role;

INSERT INTO public.tolerance_rules (organization_id, rule_key, name, value, unit, version, is_active)
SELECT o.id, 'mass_balance_percent', 'Tolerancia de balance de masas', 3, 'percent', 1, true
FROM public.organizations o
WHERE NOT EXISTS (
  SELECT 1 FROM public.tolerance_rules t
  WHERE t.organization_id = o.id AND t.rule_key = 'mass_balance_percent' AND t.version = 1
);

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
LEFT JOIN LATERAL (
  SELECT * FROM public.receptions rx WHERE rx.lot_id = l.id ORDER BY rx.occurred_at DESC LIMIT 1
) r ON true
ON CONFLICT (lot_id) DO UPDATE SET
  received_quantity = EXCLUDED.received_quantity,
  difference = EXCLUDED.difference,
  difference_percent = EXCLUDED.difference_percent,
  status = EXCLUDED.status,
  calculated_at = now();

-- ---------------------------------------------------------------------------
-- 3) ML tables + seed 100 (si hay lotes)
-- ---------------------------------------------------------------------------
create table if not exists public.ml_models (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  version text not null,
  status text not null default 'active' check (status in ('active', 'archived')),
  metrics jsonb not null default '{}'::jsonb,
  registered_at timestamptz not null default now(),
  unique (name, version)
);

create table if not exists public.ml_inferences (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations (id),
  lot_id uuid not null references public.lots (id),
  model_id uuid references public.ml_models (id),
  model_version text not null,
  expected_quantity numeric not null,
  observed_quantity numeric,
  deviation numeric,
  deviation_percent numeric,
  signal text not null default 'none' check (signal in ('none', 'review_signal')),
  features jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists ml_inferences_lot_idx on public.ml_inferences (lot_id);
create index if not exists ml_inferences_org_idx on public.ml_inferences (organization_id);
create index if not exists ml_inferences_org_created_idx on public.ml_inferences (organization_id, created_at desc);

alter table public.ml_models enable row level security;
alter table public.ml_inferences enable row level security;

drop policy if exists ml_models_select on public.ml_models;
create policy ml_models_select on public.ml_models
  for select using (auth.role() = 'authenticated');

drop policy if exists ml_inferences_select on public.ml_inferences;
create policy ml_inferences_select on public.ml_inferences
  for select using (organization_id = public.current_org_id());

drop policy if exists ml_inferences_insert on public.ml_inferences;
create policy ml_inferences_insert on public.ml_inferences
  for insert with check (
    organization_id = public.current_org_id()
    and public.current_role() in (
      'admin', 'auditor', 'supervisor', 'control_center', 'receiver', 'plant_manager'
    )
  );

grant select on public.ml_models to authenticated;
grant select, insert on public.ml_inferences to authenticated;
grant all on public.ml_models to service_role;
grant all on public.ml_inferences to service_role;

INSERT INTO public.ml_models (name, version, status, metrics)
SELECT 'expected-quantity-baseline', '1.0.0', 'active', '{"mae": 2.4}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM public.ml_models WHERE name = 'expected-quantity-baseline' AND version = '1.0.0');

INSERT INTO public.ml_models (name, version, status, metrics)
SELECT 'expected-quantity-baseline', '1.1.0', 'active', '{"mae": 2.1}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM public.ml_models WHERE name = 'expected-quantity-baseline' AND version = '1.1.0');

DO $$
DECLARE
  v_org_id uuid := 'e857fa80-1678-4b27-b80f-c38f471a8931';
  v_lot_total int;
  v_model_v1 uuid;
  v_model_v11 uuid;
BEGIN
  SELECT count(*) INTO v_lot_total FROM public.lots WHERE organization_id = v_org_id;
  IF v_lot_total = 0 THEN
    RAISE NOTICE 'Sin lotes en org piloto; se omiten inferencias ML seed.';
    RETURN;
  END IF;

  SELECT id INTO v_model_v1 FROM public.ml_models WHERE version = '1.0.0' LIMIT 1;
  SELECT id INTO v_model_v11 FROM public.ml_models WHERE version = '1.1.0' LIMIT 1;

  INSERT INTO public.ml_inferences (
    organization_id, lot_id, model_id, model_version,
    expected_quantity, observed_quantity, deviation, deviation_percent,
    signal, features, created_at
  )
  SELECT
    l.organization_id,
    l.id,
    CASE WHEN g % 3 = 0 THEN v_model_v11 ELSE v_model_v1 END,
    CASE WHEN g % 3 = 0 THEN '1.1.0' ELSE '1.0.0' END,
    round((l.quantity * 0.985)::numeric, 4),
    CASE WHEN g % 5 = 0 THEN NULL ELSE round((l.quantity * (0.96 + ((g % 7) * 0.008)))::numeric, 4) END,
    CASE WHEN g % 5 = 0 THEN NULL ELSE round((l.quantity * (0.96 + ((g % 7) * 0.008)) - l.quantity * 0.985)::numeric, 4) END,
    CASE WHEN g % 5 = 0 THEN NULL ELSE round((((l.quantity * (0.96 + ((g % 7) * 0.008)) - l.quantity * 0.985) / NULLIF(l.quantity * 0.985, 0)) * 100)::numeric, 2) END,
    CASE WHEN g % 5 = 0 THEN 'none' WHEN g % 4 = 0 THEN 'review_signal' ELSE 'none' END,
    jsonb_build_object(
      'dataset', 'SEED_ML_100',
      'seed_index', g,
      'lot_code', l.code,
      'mineral', l.mineral,
      'unit', l.unit,
      'origin_quantity', l.quantity,
      'source', 'seed',
      'note', 'Inferencia de cantidad esperada para revisión operativa'
    ),
    now() - ((g % 90) || ' days')::interval
  FROM generate_series(1, 100) AS g
  JOIN LATERAL (
    SELECT * FROM public.lots
    WHERE organization_id = v_org_id
    ORDER BY code
    OFFSET ((g - 1) % v_lot_total)
    LIMIT 1
  ) l ON true
  WHERE NOT EXISTS (
    SELECT 1 FROM public.ml_inferences m
    WHERE m.organization_id = v_org_id
      AND m.features->>'dataset' = 'SEED_ML_100'
      AND (m.features->>'seed_index')::int = g
  );
END $$;

notify pgrst, 'reload schema';

-- ---------------------------------------------------------------------------
-- 4) Verificación
-- ---------------------------------------------------------------------------
SELECT 'weighings_demo_restantes' AS chequeo, count(*)::text AS valor
FROM public.weighings WHERE responsible ILIKE '%DEMO%' OR instrument ILIKE '%DEMO%'
UNION ALL
SELECT 'mass_balances', count(*)::text FROM public.mass_balances
UNION ALL
SELECT 'ml_inferences', count(*)::text FROM public.ml_inferences
UNION ALL
SELECT 'ml_models', count(*)::text FROM public.ml_models;

COMMIT;

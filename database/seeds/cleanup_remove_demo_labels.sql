-- WEB_MINERA | Eliminar etiquetas "DEMO" visibles en la UI
-- Ejecutar en Supabase > SQL Editor sobre la BD con datos del dataset.
-- No borra registros; solo renombra textos/códigos visibles.

begin;

-- Operación minera
UPDATE public.mining_operations
SET name = 'Operación El Alto'
WHERE name ILIKE '%DEMO%' OR name ILIKE '%DATASET DEMO%';

-- Lotes: códigos y observaciones
UPDATE public.lots
SET
  code = regexp_replace(code, '^DEMO-LOTE-', 'LOT-2026-', 'i'),
  qr_payload = regexp_replace(
    coalesce(qr_payload, ''),
    'WEBMINERA-DEMO:DEMO-LOTE-',
    'WEBMINERA:LOT-2026-',
    'i'
  ),
  observation = replace(
    coalesce(observation, ''),
    'REGISTRO SIMULADO PARA PRUEBAS DE WEB_MINERA. No es una operación real.',
    'Lote registrado en operación minera El Alto.'
  )
WHERE code ILIKE 'DEMO-LOTE-%'
   OR coalesce(qr_payload, '') ILIKE '%DEMO%'
   OR coalesce(observation, '') ILIKE '%DEMO%'
   OR coalesce(observation, '') ILIKE '%SIMULADO%';

-- Custodia
UPDATE public.custody_transfers ct
SET
  notes = 'Transferencia de custodia registrada en campo.',
  responsible = CASE
    WHEN coalesce(responsible, '') ILIKE '%DEMO%' OR coalesce(responsible, '') ILIKE '%prueba%'
      THEN 'Luis Mendoza'
    ELSE responsible
  END
WHERE EXISTS (
  SELECT 1 FROM public.lots l
  WHERE l.id = ct.lot_id
    AND (l.code LIKE 'LOT-2026-%' OR l.code LIKE 'DEMO-LOTE-%')
);

-- Transporte
UPDATE public.transports t
SET
  plate = regexp_replace(plate, '-DEMO$', '', 'i'),
  code = regexp_replace(coalesce(code, ''), '^DEMO-TR-', 'TR-', 'i'),
  notes = 'Transporte asignado a ruta El Alto – Junín.',
  driver = CASE
    WHEN coalesce(driver, '') = '' THEN 'Carlos Rojas'
    ELSE driver
  END
WHERE EXISTS (
  SELECT 1 FROM public.lots l
  WHERE l.id = t.lot_id
    AND (l.code LIKE 'LOT-2026-%' OR l.code LIKE 'DEMO-LOTE-%')
)
OR coalesce(plate, '') ILIKE '%DEMO%'
OR coalesce(code, '') ILIKE '%DEMO%';

-- Eventos de transporte
UPDATE public.transport_events e
SET description = CASE
  WHEN description ILIKE '%simulado%' AND description ILIKE '%ruta%' THEN 'Vehículo en ruta'
  WHEN description ILIKE '%simulado%' THEN 'Salida registrada'
  ELSE replace(replace(description, ' (evento simulado)', ''), ' (DEMO)', '')
END
WHERE description ILIKE '%DEMO%'
   OR description ILIKE '%simulado%';

-- Recepciones
UPDATE public.receptions
SET
  responsible = 'Ana Quispe',
  notes = 'Recepción confirmada en planta. Diferencia dentro de control operativo.'
WHERE responsible ILIKE '%DEMO%'
   OR coalesce(notes, '') ILIKE '%ficticia%'
   OR coalesce(notes, '') ILIKE '%DEMO%';

-- Pesajes
UPDATE public.weighings
SET
  instrument = 'Balanza industrial METTLER 3000',
  responsible = 'Jorge Ramírez',
  notes = 'Pesaje asociado a recepción en planta.'
WHERE instrument ILIKE '%DEMO%'
   OR responsible ILIKE '%DEMO%'
   OR coalesce(notes, '') ILIKE '%ficticia%'
   OR coalesce(notes, '') ILIKE '%DEMO%';

-- Alertas
UPDATE public.alerts
SET
  title = replace(replace(title, ' (DEMO)', ''), '(DEMO)', ''),
  summary = 'Alerta operativa para revisión del supervisor.',
  reason = 'Desviación detectada en control de trazabilidad/balance. Requiere verificación.',
  rule_applied = CASE
    WHEN rule_applied = 'DEMO_DATASET_RULE' THEN 'SEED_DATASET_RULE'
    ELSE rule_applied
  END
WHERE title ILIKE '%DEMO%'
   OR coalesce(summary, '') ILIKE '%DEMO%'
   OR coalesce(reason, '') ILIKE '%simulado%'
   OR rule_applied = 'DEMO_DATASET_RULE';

-- Notificaciones
UPDATE public.notifications
SET
  title = regexp_replace(title, '^Notificación DEMO #', 'Aviso operativo #', 'i'),
  body = 'Aviso del sistema de trazabilidad WEB_MINERA.'
WHERE title ILIKE '%DEMO%'
   OR coalesce(body, '') ILIKE '%simulado%'
   OR coalesce(body, '') ILIKE '%dataset%';

-- Inferencias ML (features visibles en detalle)
UPDATE public.ml_inferences
SET features = (
  coalesce(features, '{}'::jsonb)
  - 'note'
  || jsonb_build_object(
      'dataset', 'SEED_ML_100',
      'note', 'Inferencia de cantidad esperada para revisión operativa'
    )
)
WHERE features->>'dataset' = 'DEMO_ML_100'
   OR coalesce(features->>'note', '') ILIKE '%DEMO%'
   OR coalesce(features->>'note', '') ILIKE '%ficticia%';

-- Eventos de lote
UPDATE public.lot_events
SET notes = 'Evento de registro del lote.'
WHERE notes ILIKE '%simulado%' OR notes ILIKE '%DEMO%';

-- Verificación rápida
SELECT 'lots_con_demo' AS chequeo, count(*) AS n
FROM public.lots
WHERE code ILIKE '%DEMO%' OR coalesce(observation,'') ILIKE '%DEMO%'
UNION ALL
SELECT 'weighings_con_demo', count(*)
FROM public.weighings
WHERE responsible ILIKE '%DEMO%' OR instrument ILIKE '%DEMO%'
UNION ALL
SELECT 'receptions_con_demo', count(*)
FROM public.receptions
WHERE responsible ILIKE '%DEMO%'
UNION ALL
SELECT 'transports_con_demo', count(*)
FROM public.transports
WHERE coalesce(code,'') ILIKE '%DEMO%' OR coalesce(plate,'') ILIKE '%DEMO%'
UNION ALL
SELECT 'alerts_con_demo', count(*)
FROM public.alerts
WHERE title ILIKE '%DEMO%' OR rule_applied ILIKE '%DEMO%';

COMMIT;

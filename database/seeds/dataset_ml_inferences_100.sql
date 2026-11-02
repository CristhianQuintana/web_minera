-- WEB_MINERA | 100 inferencias ML simuladas (ficticias)
-- Prerrequisito: ejecutar database/migrations/0008_ensure_ml_inferences.sql
-- y disponer de lotes en la organización piloto (p. ej. dataset_demo_220.sql).
-- Idempotente: no duplica filas con features.dataset = 'DEMO_ML_100'.
-- IMPORTANTE: datos de demostración. No representan estimaciones reales.

begin;

DO $$
DECLARE
    v_org_id uuid := 'e857fa80-1678-4b27-b80f-c38f471a8931';
    v_lot_total int;
    v_model_v1 uuid;
    v_model_v11 uuid;
BEGIN
    SELECT count(*) INTO v_lot_total
    FROM public.lots
    WHERE organization_id = v_org_id;

    IF v_lot_total = 0 THEN
        RAISE EXCEPTION
          'No hay lotes en la organización piloto %. Ejecuta primero database/seeds/dataset_demo_220.sql',
          v_org_id;
    END IF;

    IF to_regclass('public.ml_inferences') IS NULL THEN
        RAISE EXCEPTION 'Falta public.ml_inferences. Ejecuta database/migrations/0008_ensure_ml_inferences.sql';
    END IF;

    SELECT id INTO v_model_v1
    FROM public.ml_models
    WHERE name = 'expected-quantity-baseline' AND version = '1.0.0'
    LIMIT 1;

    SELECT id INTO v_model_v11
    FROM public.ml_models
    WHERE name = 'expected-quantity-baseline' AND version = '1.1.0'
    LIMIT 1;

    IF v_model_v1 IS NULL THEN
        INSERT INTO public.ml_models (name, version, status, metrics)
        VALUES (
          'expected-quantity-baseline',
          '1.0.0',
          'active',
          '{"mae": 2.4, "mape": 3.1}'::jsonb
        )
        RETURNING id INTO v_model_v1;
    END IF;

    IF v_model_v11 IS NULL THEN
        INSERT INTO public.ml_models (name, version, status, metrics)
        VALUES (
          'expected-quantity-baseline',
          '1.1.0',
          'active',
          '{"mae": 2.1, "mape": 2.8}'::jsonb
        )
        RETURNING id INTO v_model_v11;
    END IF;

    INSERT INTO public.ml_inferences (
        organization_id,
        lot_id,
        model_id,
        model_version,
        expected_quantity,
        observed_quantity,
        deviation,
        deviation_percent,
        signal,
        features,
        created_at
    )
    SELECT
        l.organization_id,
        l.id,
        CASE WHEN g % 3 = 0 THEN v_model_v11 ELSE v_model_v1 END,
        CASE WHEN g % 3 = 0 THEN '1.1.0' ELSE '1.0.0' END,
        round((l.quantity * CASE
            WHEN lower(l.mineral) LIKE '%oro%' THEN 0.978
            WHEN lower(l.mineral) LIKE '%plata%' THEN 0.982
            WHEN lower(l.mineral) LIKE '%cobre%' THEN 0.985
            WHEN lower(l.mineral) LIKE '%zinc%' THEN 0.988
            ELSE 0.985
        END)::numeric, 4),
        CASE
            WHEN g % 5 = 0 THEN NULL
            ELSE round((l.quantity * (0.96 + ((g % 7) * 0.008)))::numeric, 4)
        END,
        CASE
            WHEN g % 5 = 0 THEN NULL
            ELSE round(
                (l.quantity * (0.96 + ((g % 7) * 0.008)))
                - (l.quantity * CASE
                    WHEN lower(l.mineral) LIKE '%oro%' THEN 0.978
                    WHEN lower(l.mineral) LIKE '%plata%' THEN 0.982
                    WHEN lower(l.mineral) LIKE '%cobre%' THEN 0.985
                    WHEN lower(l.mineral) LIKE '%zinc%' THEN 0.988
                    ELSE 0.985
                END)
            , 4)
        END,
        CASE
            WHEN g % 5 = 0 THEN NULL
            ELSE round((
                (
                  (l.quantity * (0.96 + ((g % 7) * 0.008)))
                  - (l.quantity * CASE
                      WHEN lower(l.mineral) LIKE '%oro%' THEN 0.978
                      WHEN lower(l.mineral) LIKE '%plata%' THEN 0.982
                      WHEN lower(l.mineral) LIKE '%cobre%' THEN 0.985
                      WHEN lower(l.mineral) LIKE '%zinc%' THEN 0.988
                      ELSE 0.985
                    END)
                ) / NULLIF(
                    l.quantity * CASE
                      WHEN lower(l.mineral) LIKE '%oro%' THEN 0.978
                      WHEN lower(l.mineral) LIKE '%plata%' THEN 0.982
                      WHEN lower(l.mineral) LIKE '%cobre%' THEN 0.985
                      WHEN lower(l.mineral) LIKE '%zinc%' THEN 0.988
                      ELSE 0.985
                    END
                , 0)
            ) * 100, 2)
        END,
        CASE
            WHEN g % 5 = 0 THEN 'none'
            WHEN abs((
                (
                  (l.quantity * (0.96 + ((g % 7) * 0.008)))
                  - (l.quantity * 0.985)
                ) / NULLIF(l.quantity * 0.985, 0)
            ) * 100) > 5 THEN 'review_signal'
            WHEN g % 4 = 0 THEN 'review_signal'
            ELSE 'none'
        END,
        jsonb_build_object(
            'dataset', 'DEMO_ML_100',
            'demo_index', g,
            'lot_code', l.code,
            'mineral', l.mineral,
            'unit', l.unit,
            'origin_quantity', l.quantity,
            'mining_operation_id', l.mining_operation_id,
            'source', 'simulated_seed',
            'note', 'Inferencia ficticia para pruebas del módulo Análisis ML'
        ),
        now() - ((g % 90) || ' days')::interval - ((g % 24) || ' hours')::interval
    FROM generate_series(1, 100) AS g
    JOIN LATERAL (
        SELECT l.*
        FROM public.lots l
        WHERE l.organization_id = v_org_id
        ORDER BY l.code
        OFFSET ((g - 1) % v_lot_total)
        LIMIT 1
    ) l ON true
    WHERE NOT EXISTS (
        SELECT 1
        FROM public.ml_inferences m
        WHERE m.organization_id = v_org_id
          AND m.features->>'dataset' = 'DEMO_ML_100'
          AND (m.features->>'demo_index')::int = g
    );

END $$;

SELECT
  count(*) AS total_demo_ml_inferences,
  count(*) FILTER (WHERE signal = 'review_signal') AS con_senal_revision,
  count(*) FILTER (WHERE signal = 'none') AS sin_senal,
  count(DISTINCT model_version) AS versiones_modelo,
  count(DISTINCT lot_id) AS lotes_distintos
FROM public.ml_inferences
WHERE features->>'dataset' = 'DEMO_ML_100';

COMMIT;

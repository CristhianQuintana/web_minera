# Informe ML — WEB_MINERA

Fecha: 2026-11-03

## Clasificacion
El servicio ML actual es un **estimador heuristic**o por mineral (factores oro/carbon/default) con fallback local en backend.
No existe dataset train/test versionado ni metricas MAE/RMSE/R2.

## Alcance PMV2
Capacidad **experimental / Incremento 3**. No bloquea cierre de requisitos I1-I2.
No debe presentarse como modelo predictivo validado ni detector de fraude/legalidad.

## Compose
`ml/Dockerfile` existe; `compose.yaml` no levanta el servicio. Despliegue separado o runbook pendiente (WEB-AUD-014).

INFORME TÉCNICO
Estructura y Arquitectura Estrictamente Hexagonal de `WEB_MINERA`
Proyecto: Plataforma Digital de Trazabilidad y Cadena de Custodia para Pequeña Minería Responsable  
Componente: Sistema Web  
Nombre: `WEB_MINERA`  
Versión: 1.0  
Estado: Base para construcción
---
1. Propósito
Este documento define la estructura física, lógica y arquitectónica que debe utilizarse para construir `WEB_MINERA` bajo una Arquitectura Hexagonal estricta (Ports and Adapters).
`WEB_MINERA` será independiente de `APP_MINERA`. El proyecto web será un workspace que contendrá frontend, backend y ML, además de contratos, base de datos, pruebas, documentación y despliegue.
La arquitectura debe impedir que el dominio y los casos de uso queden acoplados directamente a frameworks, bases de datos, proveedores externos o mecanismos concretos de infraestructura.
---
2. Contexto
La solución web pertenece a la plataforma de trazabilidad y cadena de custodia para pequeña minería responsable. Debe soportar progresivamente:
Registro digital de lotes.
Evidencias y ubicación.
Identificación mediante QR.
Transferencias de custodia.
Transporte.
Recepción.
Pesaje.
Balance de masas.
Auditoría.
Alertas.
Estimación de cantidad esperada mediante ML.
El proyecto móvil `APP_MINERA` permanece separado.
```text
PROYECTOS/
├── APP_MINERA/      # Flutter
└── WEB_MINERA/      # Solución web completa
```
La carpeta `APP_MINERA/web/` es el target web propio de Flutter y no debe utilizarse para Next.js.
---
3. Principio arquitectónico
`WEB_MINERA` es un workspace, no un único runtime. Por ello, `frontend`, `backend` y `ml` deben poseer su propia separación hexagonal.
La estructura conceptual es:
```text
ADAPTERS INBOUND
       |
PORTS INBOUND
       |
APPLICATION
       |
DOMAIN
       |
PORTS OUTBOUND
       |
ADAPTERS OUTBOUND
       |
INFRASTRUCTURE
```
La estructura física debe distinguir explícitamente:
`domain`
`application`
`ports/inbound`
`ports/outbound`
`adapters/inbound`
`adapters/outbound`
`infrastructure`
`composition`
---
4. Estructura raíz definitiva
```text
WEB_MINERA/
├── frontend/
├── backend/
├── ml/
├── database/
├── contracts/
├── infrastructure/
├── tests/
├── docs/
├── docker/
├── .github/
│   └── workflows/
├── .gitignore
├── README.md
├── LICENSE
└── docker-compose.yml
```
Carpeta	Responsabilidad
`frontend/`	Aplicación web Next.js
`backend/`	API y lógica de negocio principal
`ml/`	Servicio y ciclo de vida de Machine Learning
`database/`	Migraciones, seeds, políticas y objetos de BD
`contracts/`	Contratos compartidos
`infrastructure/`	Infraestructura de ejecución y despliegue a nivel solución
`tests/`	Pruebas transversales
`docs/`	Documentación técnica
`docker/`	Configuración Docker específica
`.github/`	CI/CD
---
5. Diferencia entre infraestructura raíz e infraestructura interna
No deben confundirse dos conceptos.
5.1 `WEB_MINERA/infrastructure/`
Corresponde a infraestructura de la solución completa:
Docker Compose.
Reverse proxy.
Configuración de despliegue.
Entornos.
Monitoring.
Scripts operativos.
5.2 `backend/app/infrastructure/`
Corresponde a infraestructura técnica interna del backend:
Base de datos.
Seguridad.
Configuración.
Logging.
Observabilidad.
Dependency Injection.
El mismo principio aplica a `frontend/src/infrastructure/` y `ml/infrastructure/`.
---
6. Backend
El backend utilizará Python + FastAPI.
6.1 Estructura
```text
backend/
├── app/
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── services/
│   │   ├── rules/
│   │   └── exceptions/
│   ├── application/
│   │   ├── use_cases/
│   │   ├── dto/
│   │   └── services/
│   ├── ports/
│   │   ├── inbound/
│   │   │   ├── use_cases/
│   │   │   └── services/
│   │   └── outbound/
│   │       ├── repositories/
│   │       ├── services/
│   │       ├── persistence/
│   │       ├── storage/
│   │       └── external/
│   ├── adapters/
│   │   ├── inbound/
│   │   │   ├── http/
│   │   │   ├── web/
│   │   │   └── api/
│   │   └── outbound/
│   │       ├── persistence/
│   │       ├── supabase/
│   │       ├── storage/
│   │       ├── external/
│   │       └── ml/
│   ├── infrastructure/
│   │   ├── database/
│   │   ├── security/
│   │   ├── configuration/
│   │   ├── logging/
│   │   ├── observability/
│   │   └── dependency-injection/
│   └── composition/
│       ├── dependency-container/
│       ├── application-factory/
│       └── bootstrap/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── e2e/
├── alembic/
│   └── versions/
├── scripts/
├── pyproject.toml
├── requirements/
├── .env.example
├── Dockerfile
└── README.md
```
6.2 `domain/`
Es el núcleo de negocio. No debe importar FastAPI, SQLAlchemy, Supabase SDK, Redis, HTTP clients, MLflow ni frameworks de infraestructura.
`entities/`
Entidades potenciales:
```text
Lot
CustodyTransfer
Transport
Reception
Weighing
Evidence
Alert
AuditRecord
MassBalance
```
`value_objects/`
Conceptos determinados por su valor:
```text
LotId
UserId
Quantity
Coordinates
QRCode
CustodyStatus
MeasurementUnit
Deviation
Tolerance
```
`services/`
Servicios de dominio para operaciones que involucren varias entidades o no pertenezcan naturalmente a una sola entidad.
Ejemplos:
```text
MassBalanceCalculator
CustodyIntegrityService
DeviationCalculator
```
`rules/`
Reglas deterministas y versionables:
```text
LotRegistrationRules
CustodyTransferRules
ReceptionRules
MassBalanceRules
AuditRules
```
`exceptions/`
Excepciones propias del dominio:
```text
InvalidLotState
InvalidCustodyTransfer
InvalidQuantity
InvalidMassBalance
InvalidEvidence
```
---
6.3 `application/`
Orquesta los casos de uso. Conoce el dominio y los puertos, pero no las implementaciones concretas.
`use_cases/`
Ejemplos:
```text
RegisterLot
AttachEvidence
StartCustodyTransfer
ConfirmCustodyTransfer
RegisterReception
RegisterWeighing
CalculateMassBalance
CreateAuditRecord
ReviewAlert
EstimateExpectedQuantity
```
Cada caso de uso debe recibir entrada, coordinar validaciones, utilizar dominio y puertos y producir una salida.
`dto/`
Objetos de transferencia de la aplicación. No deben confundirse automáticamente con entidades de dominio.
`services/`
Servicios de aplicación que coordinan múltiples operaciones.
---
6.4 `ports/inbound/`
Define cómo actores externos solicitan operaciones.
Ejemplos:
```text
RegisterLotUseCase
RegisterReceptionUseCase
RegisterWeighingUseCase
ReviewAlertUseCase
```
FastAPI no es el caso de uso. FastAPI adapta HTTP al puerto inbound.
---
6.5 `ports/outbound/`
Define lo que el núcleo necesita del exterior.
Ejemplos:
```text
LotRepository
EvidenceRepository
CustodyRepository
AuditRepository
StoragePort
AuthPort
MLInferencePort
NotificationPort
```
Estas interfaces no contienen implementaciones de PostgreSQL, Supabase o HTTP.
---
6.6 `adapters/inbound/`
Contiene los adaptadores de entrada. FastAPI pertenece aquí.
Flujo:
```text
HTTP Request
    |
FastAPI Router
    |
Controller
    |
Inbound Port
    |
Use Case
```
Los routers/controladores no deben contener lógica de negocio compleja.
---
6.7 `adapters/outbound/`
Contiene implementaciones concretas de puertos outbound.
```text
adapters/outbound/
├── persistence/
├── supabase/
├── storage/
├── external/
└── ml/
```
Ejemplos:
```text
PostgresLotRepository
PostgresCustodyRepository
PostgresReceptionRepository
```
El adaptador `ml/` será el cliente técnico que invoque al servicio ML.
---
6.8 `infrastructure/`
Contiene infraestructura técnica interna:
```text
database/
security/
configuration/
logging/
observability/
dependency-injection/
```
No debe utilizarse como carpeta genérica para código sin clasificación.
---
6.9 `composition/`
Es el punto donde se conectan puertos e implementaciones.
Ejemplo conceptual:
```text
LotRepository
      |
      +---- PostgresLotRepository
```
El caso de uso no debe ejecutar directamente:
```python
repository = PostgresLotRepository(...)
```
La composición debe realizar el wiring de dependencias.
---
7. Frontend
El frontend utilizará Next.js + TypeScript + Tailwind CSS.
7.1 Estructura
```text
frontend/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   ├── value-objects/
│   │   ├── services/
│   │   └── exceptions/
│   ├── application/
│   │   ├── use-cases/
│   │   ├── dto/
│   │   └── services/
│   ├── ports/
│   │   ├── inbound/
│   │   └── outbound/
│   ├── adapters/
│   │   ├── inbound/
│   │   │   └── nextjs/
│   │   │       ├── app/
│   │   │       ├── layouts/
│   │   │       └── routes/
│   │   └── outbound/
│   │       ├── api/
│   │       ├── supabase/
│   │       └── storage/
│   ├── infrastructure/
│   │   ├── configuration/
│   │   ├── auth/
│   │   ├── http/
│   │   └── dependency-injection/
│   ├── presentation/
│   │   ├── app/
│   │   ├── pages/
│   │   ├── layouts/
│   │   └── components/
│   ├── shared/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── schemas/
│   │   ├── types/
│   │   ├── utils/
│   │   └── constants/
│   └── config/
├── public/
├── tests/
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
├── .env.example
├── Dockerfile
└── README.md
```
7.2 Regla principal
Next.js no debe convertirse en el lugar donde se concentra la lógica de negocio.
Incorrecto:
```text
page.tsx
  ├── reglas de negocio
  ├── cálculo de balance
  ├── cambios de custodia
  ├── acceso a PostgreSQL
  └── decisiones de alertas
```
Correcto:
```text
UI
 |
Presentation
 |
Application
 |
Port
 |
Outbound Adapter
 |
Backend API
```
---
7.3 Estado
Server state: TanStack Query.
UI/client state: Zustand cuando sea necesario.
Zustand no debe utilizarse como sustituto general de TanStack Query.
7.4 Formularios
Utilizar:
```text
React Hook Form
+
Zod
```
La validación frontend mejora la experiencia, pero no sustituye la validación backend.
7.5 Herramientas previstas
React.
Next.js.
TypeScript.
Tailwind CSS.
shadcn/ui.
Lucide React.
React Hook Form.
Zod.
TanStack Query.
Zustand.
Recharts.
TanStack Table.
Vitest.
Testing Library.
Playwright.
ESLint.
Prettier.
---
8. Machine Learning
El componente ML será independiente.
```text
ml/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   └── rules/
├── application/
│   ├── use_cases/
│   ├── dto/
│   └── services/
├── ports/
│   ├── inbound/
│   └── outbound/
├── adapters/
│   ├── inbound/
│   └── outbound/
├── infrastructure/
│   ├── mlflow/
│   ├── persistence/
│   └── external/
├── presentation/
│   └── api/
├── training/
├── inference/
└── tests/
```
El servicio ML debe estimar cantidad esperada, calcular desviaciones y producir señales revisables. No debe declarar automáticamente fraude, legalidad o sanciones.
Flujo:
```text
Datos
  |
Preparación
  |
Feature Engineering
  |
Entrenamiento
  |
Evaluación
  |
MLflow
  |
Modelo versionado
  |
Inferencia
  |
Cantidad esperada
  |
Desviación
  |
Señal revisable
  |
Auditor
```
---
9. Base de datos
```text
database/
├── migrations/
├── seeds/
├── functions/
├── views/
├── policies/
├── indexes/
└── README.md
```
La persistencia será PostgreSQL/Supabase y se considerará PostGIS para información geográfica.
El frontend no debe ejecutar consultas de negocio directamente contra PostgreSQL.
Flujo principal:
```text
Frontend
  |
HTTP
  |
FastAPI
  |
Application
  |
Port
  |
Adapter
  |
PostgreSQL / Supabase
```
---
10. Contratos
```text
contracts/
├── api/
├── events/
├── schemas/
├── errors/
└── README.md
```
Los contratos reducen inconsistencias entre frontend, backend y ML. No deben contener lógica de negocio.
---
11. Infraestructura de solución
```text
infrastructure/
├── nginx/
├── docker/
├── environments/
├── monitoring/
├── scripts/
└── README.md
```
Su finalidad es despliegue y operación de la solución completa, no lógica de negocio.
---
12. Docker
```text
docker/
├── frontend/
├── backend/
├── ml/
└── README.md
```
`docker-compose.yml` podrá coordinar frontend, backend, ML y servicios auxiliares.
---
13. Variables de entorno
Cada componente debe disponer de `.env.example`. Nunca se deben subir secretos reales.
Backend, como referencia:
```text
DATABASE_URL=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
JWT_SECRET=
ML_SERVICE_URL=
```
Frontend:
```text
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```
ML:
```text
MLFLOW_TRACKING_URI=
MODEL_REGISTRY_URI=
```
---
14. Reglas de dependencia
Dependencias permitidas:
```text
Adapters -> Ports -> Application -> Domain
Application -> Ports -> Domain
Domain -> Domain
```
Dependencias prohibidas desde el dominio hacia:
```text
FastAPI
Next.js
React
SQLAlchemy
Supabase
PostgreSQL
Redis
MLflow
HTTP
Docker
```
La inversión de dependencias debe mantenerse mediante puertos.
---
15. Base de datos y balance de masas
Las tolerancias de balance no deben codificarse arbitrariamente. Deben ser configurables y versionadas.
El registro debe permitir conocer, según corresponda:
cantidad de origen;
movimientos;
cantidad recibida;
diferencia;
tolerancia aplicada;
versión de regla utilizada.
---
16. Evidencias
Las evidencias deben gestionarse mediante referencias de almacenamiento, no como blobs dentro del dominio.
Conceptualmente:
```text
Evidence
├── id
├── type
├── storage_reference
├── captured_at
└── metadata
```
El almacenamiento real corresponde a un adaptador outbound.
---
17. Auditoría
La auditoría debe permitir registrar, según corresponda:
actor;
acción;
fecha y hora;
entidad afectada;
identificador;
contexto;
resultado;
información relevante de trazabilidad.
La persistencia concreta queda fuera del dominio.
---
18. QR
El QR es un identificador operativo. No constituye por sí mismo autenticación, cifrado, prueba de legalidad ni autorización.
---
19. Offline-first e idempotencia
El offline-first pertenece principalmente a `APP_MINERA`, pero `WEB_MINERA` debe estar preparado para recibir operaciones sincronizadas.
El backend debe contemplar:
identificadores idempotentes;
control de duplicados;
timestamps;
estados de sincronización;
consistencia;
trazabilidad.
Una operación repetida por reintento no debe generar duplicados cuando la operación sea diseñada como idempotente.
---
20. API
Las rutas HTTP deben funcionar como adaptadores.
Ejemplos:
```text
/api/v1/lots
/api/v1/custody
/api/v1/transport
/api/v1/receptions
/api/v1/weighings
/api/v1/audits
/api/v1/alerts
/api/v1/ml
```
El dominio no debe conocer HTTP ni códigos de estado.
---
21. Health check
El backend debe exponer:
```text
GET /health
```
Debe devolver HTTP 200 cuando el servicio esté operativo.
---
22. Seguridad
Principios mínimos:
No versionar secretos.
Validar entradas.
Validar autorización en backend.
Aplicar mínimo privilegio.
Registrar eventos relevantes.
Controlar CORS.
Validar archivos.
Limitar tamaño de evidencias.
Proteger la API contra abuso.
Utilizar HTTPS en entornos desplegados.
Herramientas previstas:
```text
OWASP ZAP
SonarQube
GitHub Actions
```
---
23. Pruebas
Backend:
```text
backend/tests/
├── unit/
├── integration/
├── contract/
└── e2e/
```
Frontend:
```text
frontend/tests/
├── unit/
├── component/
└── e2e/
```
ML:
```text
ml/tests/
├── unit/
├── integration/
└── model/
```
Solución:
```text
tests/
├── e2e/
├── contract/
└── integration/
```
---
24. Git
Ramas recomendadas:
```text
main
develop
feature/*
fix/*
hotfix/*
```
Ejemplos:
```text
feature/backend-hexagonal-base
feature/frontend-base
feature/database-schema
feature/ml-service
fix/custody-validation
```
Commits sugeridos:
```text
feat(backend): initialize hexagonal structure
feat(frontend): initialize nextjs application
feat(database): add initial schema
feat(ml): initialize inference service
test(lot): add registration use case tests
docs(architecture): define web structure
```
---
25. CI/CD
```text
.github/
└── workflows/
    ├── backend-ci.yml
    ├── frontend-ci.yml
    ├── ml-ci.yml
    └── integration-ci.yml
```
Validaciones base:
```text
Install
  |
Lint
  |
Type Check
  |
Unit Tests
  |
Integration Tests
  |
Build
```
---
26. Documentación
```text
docs/
├── architecture/
├── api/
├── database/
├── deployment/
├── security/
├── testing/
└── ml/
```
Las decisiones arquitectónicas relevantes pueden registrarse como ADR en:
```text
docs/architecture/adr/
```
---
27. Estructura final consolidada
```text
WEB_MINERA/
├── frontend/
│   └── src/
│       ├── domain/
│       ├── application/
│       ├── ports/
│       │   ├── inbound/
│       │   └── outbound/
│       ├── adapters/
│       │   ├── inbound/
│       │   └── outbound/
│       ├── infrastructure/
│       ├── presentation/
│       ├── shared/
│       └── config/
│
├── backend/
│   └── app/
│       ├── domain/
│       ├── application/
│       ├── ports/
│       │   ├── inbound/
│       │   └── outbound/
│       ├── adapters/
│       │   ├── inbound/
│       │   └── outbound/
│       ├── infrastructure/
│       └── composition/
│
├── ml/
│   ├── domain/
│   ├── application/
│   ├── ports/
│   │   ├── inbound/
│   │   └── outbound/
│   ├── adapters/
│   │   ├── inbound/
│   │   └── outbound/
│   ├── infrastructure/
│   ├── presentation/
│   ├── training/
│   ├── inference/
│   └── tests/
│
├── database/
│   ├── migrations/
│   ├── seeds/
│   ├── functions/
│   ├── views/
│   ├── policies/
│   └── indexes/
├── contracts/
│   ├── api/
│   ├── events/
│   ├── schemas/
│   └── errors/
├── infrastructure/
│   ├── nginx/
│   ├── docker/
│   ├── environments/
│   ├── monitoring/
│   └── scripts/
├── tests/
│   ├── e2e/
│   ├── contract/
│   └── integration/
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── database/
│   ├── deployment/
│   ├── security/
│   ├── testing/
│   └── ml/
├── docker/
│   ├── frontend/
│   ├── backend/
│   └── ml/
├── .github/
│   └── workflows/
├── .gitignore
├── README.md
└── docker-compose.yml
```
---
28. Orden de implementación
El desarrollador debe crear primero la arquitectura y después las funcionalidades.
Fase 1. Workspace
Crear las carpetas raíz.
Fase 2. Backend
Crear `domain`, `application`, `ports`, `adapters`, `infrastructure` y `composition`.
Fase 3. Frontend
Crear `domain`, `application`, `ports`, `adapters`, `infrastructure`, `presentation` y `shared`.
Fase 4. ML
Crear `domain`, `application`, `ports`, `adapters`, `infrastructure`, `training` e `inference`.
Fase 5. Contratos
Definir contratos iniciales de API y comunicación.
Fase 6. Base de datos
Crear migraciones iniciales.
Fase 7. Composition Root
Configurar el wiring de dependencias.
Fase 8. Health checks
Comprobar que los servicios arranquen correctamente.
Fase 9. CI
Configurar lint, tests y build.
Fase 10. Primera funcionalidad
Implementar un caso de uso completo respetando toda la arquitectura.
---
29. Primera prueba arquitectónica
La primera funcionalidad recomendada es Registrar lote.
Flujo:
```text
Frontend
  |
Formulario
  |
Caso de uso frontend
  |
API Adapter
  |
FastAPI
  |
Inbound Port
  |
RegisterLotUseCase
  |
Domain
  |
LotRepository Port
  |
Postgres Adapter
  |
PostgreSQL
```
Esta funcionalidad debe demostrar que la arquitectura está funcionando antes de construir el resto del sistema.
---
30. Criterios de aceptación
Arquitectura
[ ] Separación explícita entre dominio, aplicación, puertos y adaptadores.
[ ] Existen `ports/inbound` y `ports/outbound`.
[ ] Existen `adapters/inbound` y `adapters/outbound`.
[ ] Existe `infrastructure`.
[ ] Existe `composition` donde corresponde.
[ ] El dominio no depende de frameworks.
[ ] Los casos de uso no instancian repositorios concretos.
Backend
[ ] FastAPI funciona como adaptador inbound.
[ ] PostgreSQL/Supabase está detrás de adaptadores outbound.
[ ] Los repositorios están definidos mediante puertos.
[ ] Existe composición de dependencias.
[ ] Existe `GET /health`.
[ ] Existen pruebas unitarias.
Frontend
[ ] Next.js está separado del dominio.
[ ] Los componentes UI no contienen reglas de negocio.
[ ] El acceso a API está detrás de adaptadores.
[ ] TanStack Query gestiona server state.
[ ] Zod valida formularios.
ML
[ ] ML posee estructura independiente.
[ ] Existe puerto de inferencia.
[ ] El backend no depende directamente de una librería concreta de ML.
[ ] Los modelos son versionables.
[ ] MLflow está aislado como infraestructura.
Infraestructura
[ ] Existen Dockerfiles.
[ ] Existe Docker Compose.
[ ] Existen `.env.example`.
[ ] No existen secretos versionados.
[ ] Existe CI básico.
[ ] Existe README de ejecución.
---
31. Reglas obligatorias para el desarrollador
No colocar lógica de negocio en controladores HTTP.
No colocar SQL directamente en casos de uso.
No importar Supabase desde el dominio.
No importar FastAPI desde el dominio.
No importar Next.js desde el dominio.
No conectar el frontend directamente a PostgreSQL para operaciones de negocio.
No instanciar implementaciones concretas dentro de casos de uso.
No usar `infrastructure/` como carpeta genérica.
No convertir `shared/` en un depósito de lógica de negocio.
No implementar decisiones de fraude o legalidad mediante ML.
No codificar tolerancias arbitrarias sin configuración/versionamiento.
No mezclar `APP_MINERA` con `WEB_MINERA`.
---
32. Definición de terminado
La actividad de creación de estructura queda terminada cuando:
`WEB_MINERA` existe como workspace independiente.
`frontend`, `backend` y `ml` existen como componentes separados.
Cada componente posee separación hexagonal coherente.
Backend posee `domain`, `application`, `ports`, `adapters`, `infrastructure` y `composition`.
Frontend posee separación entre dominio, aplicación, puertos, adaptadores, infraestructura y presentación.
ML posee separación entre dominio, aplicación, puertos, adaptadores e infraestructura.
Existen base de datos, contratos, documentación y despliegue.
Los archivos iniciales de configuración están creados.
Los servicios pueden arrancar sin errores estructurales.
Existe README para ejecutar la solución.
Existe una primera prueba automatizada por componente.
Existe CI básico.
El dominio no depende de frameworks externos.
Las implementaciones concretas están detrás de puertos.
El wiring de dependencias está centralizado en composición.
---
33. Resultado esperado
Al terminar esta etapa, `WEB_MINERA` tendrá una base sólida para implementar los cuatro incrementos definidos del proyecto:
```text
I1
Registro digital offline-first,
GPS, evidencias y QR

I2
Transferencia de custodia
y trazabilidad del transporte

I3
Recepción, pesaje, evidencias
y balance de masas

I4
Auditoría, alertas y estimación
de cantidad esperada mediante ML
```
Cada incremento debe implementarse como casos de uso y atravesar las capas correspondientes sin romper las reglas arquitectónicas.
---
34. Nota final
La finalidad de esta estructura no es aumentar artificialmente la cantidad de carpetas. Cada directorio responde a una responsabilidad arquitectónica concreta.
El principio rector es:
```text
EXTERIOR
   |
ADAPTERS INBOUND
   |
PORTS INBOUND
   |
APPLICATION
   |
DOMAIN
   |
PORTS OUTBOUND
   |
ADAPTERS OUTBOUND
   |
EXTERIOR
```
El dominio debe ser el elemento más estable del sistema. Frameworks, proveedores, bases de datos, almacenamiento, servicios externos y mecanismos de infraestructura deben poder cambiarse con el menor impacto posible sobre el núcleo de negocio.
`WEB_MINERA` debe construirse bajo este principio desde el primer commit, evitando crear primero una solución fuertemente acoplada y tratar de convertirla posteriormente en arquitectura hexagonal.

---
35. Estado de implementación (1.0)

La estructura hexagonal, los contratos, el backend FastAPI, el frontend Next.js, el servicio ML, las migraciones web, Docker y CI quedaron construidos en este workspace.

Criterios de la sección 30 cubiertos:
- Separación domain / application / ports / adapters / infrastructure / composition.
- FastAPI como adaptador inbound; Supabase como adaptador outbound.
- `GET /health` operativo.
- Next.js separado del dominio; TanStack Query y Zod en uso.
- ML independiente con puerto de inferencia.
- Dockerfiles, Compose, `.env.example`, CI y README de ejecución.
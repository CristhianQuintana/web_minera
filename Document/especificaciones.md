ESPECIFICACIÓN FUNCIONAL Y UX/UI DE `WEB_MINERA`
Plataforma Digital de Trazabilidad y Cadena de Custodia para Pequeña Minería Responsable
Documento: Especificación integral para desarrollo de la aplicación web  
Versión: 1.0  
Estado: Base para implementación  
Componente: `WEB_MINERA`  
Objetivo: Definir con precisión la estructura funcional, visual, interactiva y técnica de la aplicación web para que el desarrollador pueda construirla de extremo a extremo con código limpio, mantenible, seguro y consistente.
---
1. Objetivo del documento
Este documento especifica cómo debe comportarse la aplicación web `WEB_MINERA`.
No se limita a indicar qué pantallas deben existir. También define:
qué información debe mostrar cada pantalla;
quién puede acceder;
qué ocurre al presionar cada acción;
qué componentes deben utilizarse;
cuándo abrir un drawer;
cuándo utilizar modal;
cuándo navegar a una página;
qué animaciones utilizar;
qué ocurre durante la carga;
qué ocurre cuando no existen datos;
qué ocurre cuando falla una operación;
cómo deben funcionar los formularios;
cómo debe funcionar el login;
cómo se realiza la invitación mediante correo;
cómo se controlan sesiones y permisos;
cómo debe mantenerse la consistencia visual;
cómo debe implementarse el código;
qué reglas de Clean Code debe respetar el desarrollador.
El resultado esperado es una aplicación web completa, no un conjunto de mockups o páginas aisladas.
---
2. Contexto del sistema
`WEB_MINERA` es el componente web de la Plataforma Digital de Trazabilidad y Cadena de Custodia para Pequeña Minería Responsable.
La aplicación permitirá consultar, gestionar, supervisar y auditar:
lotes;
cadena de custodia;
transporte;
recepción;
pesajes;
balance de masas;
evidencias;
alertas;
auditoría;
análisis mediante ML;
usuarios;
configuración.
El proyecto móvil `APP_MINERA` permanece separado.
La aplicación web será desarrollada como un proyecto independiente:
```text
PROYECTOS/
├── APP_MINERA/
│   └── Flutter
│
└── WEB_MINERA/
    ├── frontend/
    ├── backend/
    ├── ml/
    ├── database/
    ├── contracts/
    ├── infrastructure/
    ├── tests/
    ├── docs/
    ├── docker/
    └── .github/
```
La carpeta `APP_MINERA/web/` no se utilizará para desarrollar el frontend Next.js.
---
3. Principio de acceso
3.1 No existe registro público
La aplicación NO debe permitir que una persona cree una cuenta libremente.
La pantalla de login no debe contener:
```text
Registrarse
Crear cuenta
Sign up
Crear usuario
```
El acceso se concede mediante cuentas creadas o invitadas por un administrador.
---
4. Invitación por correo electrónico
Sí se debe implementar un flujo mediante correo electrónico.
El objetivo es que un administrador pueda invitar a una persona a utilizar el sistema.
Flujo:
```text
Administrador
    |
Usuarios
    |
Invitar usuario
    |
Registrar correo y rol
    |
Backend
    |
Servicio de autenticación
    |
Servicio de correo
    |
Correo de invitación
    |
Usuario abre enlace
    |
Activación de cuenta
    |
Configuración de contraseña
    |
Login
    |
Dashboard correspondiente
```
No se deben enviar contraseñas permanentes por correo.
La invitación debe utilizar un enlace seguro con token de activación o mecanismo equivalente proporcionado por el sistema de autenticación.
El enlace debe tener expiración y control de uso.
---
5. Roles
La aplicación debe considerar como mínimo:
Rol	Función principal
Administrador	Administración general, usuarios, configuración y supervisión
Auditor	Revisión de trazabilidad, balances, alertas y expedientes
Productor	Gestión y consulta de sus lotes
Transportista	Gestión de transportes y transferencias asignadas
Receptor	Gestión de recepciones y pesajes
La interfaz debe ocultar las acciones no autorizadas.
La seguridad real debe validarse en backend.
Ocultar un botón no constituye autorización.
---
6. Stack visual y tecnológico esperado
Frontend:
Next.js.
React.
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
Backend:
FastAPI.
Python.
Arquitectura Hexagonal.
PostgreSQL/Supabase.
Supabase Auth.
Supabase Storage.
La aplicación web debe comunicarse con el backend mediante API.
El frontend no debe conectarse directamente a PostgreSQL para operaciones de negocio.
---
7. Principios de diseño UX
La aplicación debe priorizar:
claridad;
rapidez;
trazabilidad;
consistencia;
accesibilidad;
jerarquía visual;
feedback inmediato;
reducción de errores;
densidad de información controlada;
facilidad de auditoría.
No debe diseñarse como una landing page.
Debe percibirse como una plataforma profesional de operación y supervisión.
---
8. Sistema visual
8.1 Paleta
Uso	Color
Primary	`#0F766E`
Primary Dark	`#115E59`
Secondary	`#2563EB`
Background	`#F8FAFC`
Surface	`#FFFFFF`
Text	`#0F172A`
Secondary Text	`#64748B`
Success	`#16A34A`
Warning	`#D97706`
Error	`#DC2626`
Info	`#0284C7`
Los colores de estado deben utilizarse semánticamente.
No utilizar rojo únicamente como decoración.
---
9. Tipografía
Utilizar una tipografía sans-serif moderna y legible.
Debe existir una jerarquía clara:
```text
H1
H2
H3
H4
Body
Body secondary
Label
Caption
```
Los valores numéricos importantes deben ser visualmente fáciles de identificar.
---
10. Sistema de espaciado
Se debe utilizar un sistema consistente de spacing.
No introducir valores arbitrarios diferentes para componentes equivalentes.
Los tokens deben centralizarse.
Ejemplo conceptual:
```text
spacing-xs
spacing-sm
spacing-md
spacing-lg
spacing-xl
```
---
11. Bordes y sombras
La interfaz debe utilizar:
bordes suaves;
sombras discretas;
esquinas consistentes.
No utilizar sombras excesivamente fuertes.
---
12. Animaciones
Las animaciones deben comunicar:
entrada;
salida;
cambio de estado;
feedback;
relación entre elementos.
No deben utilizarse únicamente para decorar.
Duraciones recomendadas:
Interacción	Duración
Hover	100–150 ms
Microinteracción	150–200 ms
Modal	150–250 ms
Drawer	200–300 ms
Transición de vista	150–250 ms
Se debe respetar `prefers-reduced-motion`.
---
13. Login
Ruta:
```text
/login
```
La pantalla de login no utiliza el layout administrativo.
Debe ser visualmente independiente.
13.1 Estructura
```text
┌──────────────────────────────────────────────────────┐
│                                                      │
│              Identidad de WEB_MINERA                │
│                                                      │
│                  Iniciar sesión                     │
│                                                      │
│   Correo electrónico                                │
│   [________________________________]                │
│                                                      │
│   Contraseña                                        │
│   [________________________________]                │
│                                                      │
│   [ ] Mostrar contraseña                            │
│                                                      │
│   ¿Olvidaste tu contraseña?                         │
│                                                      │
│   [              Ingresar             ]             │
│                                                      │
│   Mensaje de estado                                 │
│                                                      │
└──────────────────────────────────────────────────────┘
```
---
14. Animación del login
Al cargar:
aparece el contenedor principal con `fade`;
puede utilizarse un pequeño desplazamiento vertical;
los campos aparecen de manera progresiva;
el botón permanece estable.
No utilizar:
partículas;
animaciones infinitas;
fondos excesivamente dinámicos;
efectos 3D;
videos pesados.
El sistema es una plataforma operativa.
---
15. Campo de correo
Debe:
tener label;
indicar formato esperado;
validar correo;
mostrar error debajo del campo;
conservar el valor introducido cuando sea seguro hacerlo.
Ejemplo:
```text
Correo electrónico
[usuario@dominio.com]

Formato de correo no válido.
```
---
16. Campo de contraseña
Debe:
ocultar caracteres por defecto;
permitir mostrar/ocultar;
mostrar focus visible;
indicar error cuando corresponda.
Botón:
```text
Mostrar contraseña
```
debe ser accesible.
---
17. Botón Ingresar
Estado normal:
```text
Ingresar
```
Al presionar:
```text
[spinner] Ingresando...
```
Debe:
deshabilitarse;
impedir doble envío;
conservar el layout.
Si el login es correcto:
```text
Autenticación
    |
Obtener usuario
    |
Obtener permisos
    |
Cargar sesión
    |
Dashboard
```
---
18. Errores del login
No mostrar errores técnicos.
Incorrecto:
```text
401 Unauthorized
```
Correcto:
```text
El correo o la contraseña no son correctos.
```
Otros estados:
```text
Tu cuenta está inactiva. Contacta al administrador.
```
```text
Tu sesión ha expirado. Vuelve a iniciar sesión.
```
```text
No pudimos completar el inicio de sesión. Intenta nuevamente.
```
No revelar información innecesaria que permita enumerar usuarios.
---
19. Recuperación de contraseña
Ruta:
```text
/forgot-password
```
Debe solicitar:
```text
Correo electrónico
```
Botón:
```text
Enviar instrucciones
```
Después de enviar:
```text
Si existe una cuenta asociada a este correo, recibirás instrucciones para recuperar el acceso.
```
El sistema no debe revelar si el correo existe.
---
20. Activación de cuenta
Ruta:
```text
/activate-account?token=...
```
Debe validar el token antes de mostrar el formulario completo.
Si es válido:
```text
Nombre
Correo
Nueva contraseña
Confirmar contraseña
```
Botón:
```text
Activar cuenta
```
Resultado:
```text
Cuenta activada correctamente.
```
Botón:
```text
Ir al inicio de sesión
```
---
21. Invitación expirada
Si el token expiró:
```text
Esta invitación ya no es válida.
```
Debe existir una explicación breve.
El usuario no debe poder activar la cuenta con un token expirado.
---
22. Correo de invitación
El correo debe contener:
identidad de la plataforma;
saludo;
indicación de invitación;
rol, si corresponde;
botón para activar;
expiración;
advertencia de seguridad;
información de soporte.
Nunca incluir:
```text
Contraseña
Service Role Key
Tokens internos adicionales
```
---
23. Layout administrativo
Después de autenticarse:
```text
┌────────────────────────────────────────────────────────────┐
│ Header                                                     │
├───────────────┬────────────────────────────────────────────┤
│ Sidebar       │ Main Content                               │
│               │                                            │
│ Dashboard     │                                            │
│ Lotes         │                                            │
│ Custodia      │                                            │
│ Transporte    │                                            │
│ Recepción     │                                            │
│ Pesajes       │                                            │
│ Balance       │                                            │
│ Alertas       │                                            │
│ Auditoría     │                                            │
│ ML            │                                            │
│ Usuarios      │                                            │
│ Configuración │                                            │
│               │                                            │
│ Perfil        │                                            │
│ Cerrar sesión │                                            │
└───────────────┴────────────────────────────────────────────┘
```
---
24. Sidebar
Ancho recomendado:
```text
240–280 px
```
Debe contener:
identidad;
navegación;
administración;
usuario;
logout.
El módulo actual debe tener una indicación visual.
---
25. Sidebar colapsado
Debe poder colapsarse.
Expandido:
```text
Icono + texto
```
Colapsado:
```text
Icono
```
Al pasar el cursor sobre un icono:
```text
Tooltip
```
La transición debe ser suave y no desplazar bruscamente el contenido.
---
26. Sidebar móvil
En móvil:
```text
Menu button
    |
Drawer
```
Debe existir overlay.
Al presionar fuera:
```text
Cerrar
```
Al cambiar de ruta:
```text
Cerrar
```
---
27. Header
Debe contener:
breadcrumb;
búsqueda global cuando corresponda;
notificaciones;
usuario;
avatar.
Ejemplo:
```text
Dashboard / Lotes

                      Buscar   Alertas   Usuario
```
---
28. Breadcrumb
Debe indicar la ubicación.
Ejemplo:
```text
Lotes / LOT-2026-00021
```
Los niveles anteriores pueden ser navegables.
El último nivel representa la ubicación actual.
---
29. Dashboard
Ruta:
```text
/dashboard
```
El dashboard debe variar según rol.
Debe mostrar información realmente útil para ese usuario.
---
30. Dashboard de Administrador
Debe mostrar:
total de lotes;
transferencias;
recepciones;
alertas abiertas;
operaciones recientes;
actividad general;
indicadores de estado.
Ejemplo de cards:
```text
Lotes
1,248

Transferencias
863

Recepciones
921

Alertas abiertas
17
```
Las cards deben poder dirigir al módulo correspondiente cuando sea pertinente.
---
31. Dashboard de Auditor
Priorizar:
alertas;
casos pendientes;
balances;
desviaciones;
trazabilidad;
actividad reciente.
---
32. Dashboard de Productor
Priorizar:
mis lotes;
estados;
custodias;
operaciones recientes.
---
33. Dashboard de Transportista
Priorizar:
transportes asignados;
salidas;
llegadas;
operaciones pendientes.
---
34. Dashboard de Receptor
Priorizar:
recepciones pendientes;
pesajes;
evidencias;
operaciones recientes.
---
35. Loading del dashboard
No utilizar spinner de pantalla completa como comportamiento estándar.
Utilizar skeleton:
```text
Card skeleton
Table skeleton
Chart skeleton
```
Cuando llegan los datos:
```text
Skeleton
    |
Contenido
```
---
36. Error del dashboard
Mostrar:
```text
No pudimos cargar el dashboard.
```
Botón:
```text
Reintentar
```
El usuario no debe quedar con una pantalla vacía.
---
37. Estado vacío
Ejemplo:
```text
No hay información disponible para este periodo.
```
Si existe una acción relevante:
```text
[Ver todos]
```
---
38. Módulo Lotes
Ruta:
```text
/lots
```
Debe mostrar:
código;
fecha;
productor;
ubicación;
cantidad;
estado;
trazabilidad;
acciones.
---
39. Barra de herramientas de Lotes
Debe incluir:
```text
Buscar
Filtros
Actualizar
Exportar
```
La acción de creación sólo aparecerá si el rol correspondiente puede crear lotes desde web.
---
40. Búsqueda de lotes
Debe permitir buscar por:
código;
identificador;
QR;
productor, cuando corresponda.
Debe utilizar debounce para consultas remotas.
No realizar una petición por cada pulsación.
---
41. Filtros de lotes
Filtros:
estado;
productor;
ubicación;
fecha;
rango de cantidad.
Botones:
```text
Aplicar
Limpiar
```
Los filtros activos pueden mostrarse como chips.
---
42. Tabla de lotes
La tabla debe:
soportar paginación;
ordenar columnas permitidas;
mostrar estados;
permitir acciones;
conservar filtros al abrir/cerrar detalles.
---
43. Acción Detalle
Este patrón será estándar.
Al presionar:
```text
Detalle
```
debe abrirse un drawer desde la derecha.
No debe navegar automáticamente a otra página si la información puede visualizarse de forma contextual.
---
44. Drawer de detalle
Dimensión aproximada:
```text
Desktop: 420–560 px
Tablet: 50–70% viewport
Mobile: casi 100% viewport
```
Estructura:
```text
┌───────────────────────────────┐
│ Detalle del lote          X   │
├───────────────────────────────┤
│ Resumen                       │
│                               │
│ Evidencias                    │
│                               │
│ Cadena de custodia            │
│                               │
│ Recepción                     │
│                               │
│ Pesaje                        │
│                               │
│ Balance                       │
│                               │
│ Auditoría                     │
└───────────────────────────────┘
```
---
45. Animación del drawer
Entrada:
```text
translateX(100%) -> translateX(0)
```
Salida:
```text
translateX(0) -> translateX(100%)
```
Duración:
```text
200–300 ms
```
Debe existir overlay cuando corresponda.
Debe poder cerrarse mediante:
botón X;
Escape;
click fuera.
Si existe un formulario con cambios sin guardar, debe solicitar confirmación antes de cerrar.
---
46. Información del lote
La cabecera debe mostrar:
código;
estado;
productor;
fecha;
ubicación;
cantidad;
unidad;
QR.
---
47. Evidencias del lote
Cada evidencia debe mostrar:
tipo;
fecha;
actor;
referencia;
vista previa cuando sea posible.
Al presionar:
```text
Ver
```
abrir visor.
---
48. Visor de evidencia
Para imágenes:
```text
Lightbox
```
Debe permitir:
ampliar;
cerrar;
navegar entre evidencias si corresponde.
Para documentos:
```text
visor o descarga controlada
```
No exponer URLs privadas sin control.
---
49. Timeline de trazabilidad
Mostrar:
```text
Registro
    |
Transferencia
    |
Salida
    |
Llegada
    |
Recepción
    |
Pesaje
    |
Auditoría
```
Cada evento:
fecha;
hora;
actor;
ubicación;
acción;
evidencia;
estado.
---
50. Expansión de evento
Al presionar un evento:
```text
Evento
```
se expande.
Mostrar:
metadata;
observaciones;
evidencia;
ubicación;
identificadores;
información adicional.
La expansión debe utilizar transición corta.
---
51. Custodia
Ruta:
```text
/custody
```
Tabla:
lote;
origen;
destino;
responsable;
fecha;
estado;
evidencia;
acciones.
---
52. Detalle de custodia
Al presionar `Detalle`:
```text
Drawer derecho
```
Mostrar:
lote;
origen;
destino;
responsable;
fecha/hora;
ubicación;
estado;
evidencias;
historial.
---
53. Transporte
Ruta:
```text
/transport
```
Mostrar:
transportista;
lote;
vehículo, si corresponde;
salida;
llegada;
estado;
evidencia.
Detalle mediante drawer.
---
54. Recepción
Ruta:
```text
/receptions
```
Mostrar:
lote;
receptor;
fecha;
cantidad declarada;
cantidad recibida;
estado;
evidencia.
---
55. Pesajes
Ruta:
```text
/weighings
```
Mostrar:
lote;
receptor;
fecha;
cantidad;
unidad;
ubicación;
evidencia.
---
56. Balance de masas
Ruta:
```text
/mass-balance
```
Debe mostrar:
```text
Cantidad de origen
Cantidad recibida
Diferencia
Tolerancia
Estado
```
Debe existir una representación visual clara.
Estados:
```text
Dentro de tolerancia
Revisión requerida
Sin información suficiente
```
---
57. Alertas
Ruta:
```text
/alerts
```
Tabla:
severidad;
tipo;
lote;
fecha;
estado;
responsable;
acciones.
Estados:
```text
Nueva
En revisión
Atendida
Cerrada
```
---
58. Detalle de alerta
Al presionar:
```text
Revisar
```
abrir drawer.
Mostrar:
resumen;
motivo;
datos involucrados;
evidencia;
regla aplicada;
resultado ML si corresponde;
historial;
acciones.
---
59. Atender alerta
Al presionar:
```text
Atender alerta
```
abrir formulario.
Campos:
```text
Resultado de revisión
Observación
```
Botones:
```text
Cancelar
Guardar revisión
```
Durante guardado:
```text
Guardando...
```
Después:
```text
Revisión registrada correctamente.
```
La alerta debe actualizarse sin exigir refresh manual.
---
60. Auditoría
Ruta:
```text
/audit
```
Debe mostrar:
fecha;
actor;
acción;
entidad;
identificador;
resultado.
Debe permitir:
búsqueda;
filtros;
fechas;
actor;
tipo de acción.
---
61. Expediente de trazabilidad
Ruta conceptual:
```text
/audit/cases/:id
```
Debe ser una vista completa.
Secciones:
```text
Resumen
Datos del lote
Cadena de custodia
Transporte
Recepción
Pesajes
Balance
Evidencias
Alertas
ML
Auditoría
```
Esta pantalla sí puede ser una página completa, porque su volumen de información puede superar lo recomendable para un drawer.
---
62. Análisis ML
Ruta:
```text
/ml
```
Mostrar:
modelos;
versión activa;
métricas;
inferencias;
desviaciones;
señales revisables.
Nunca presentar una predicción como una sentencia.
Utilizar:
```text
Señal para revisión
```
```text
Desviación estimada
```
No utilizar:
```text
Fraude confirmado
```
---
63. Detalle de inferencia ML
Al presionar `Detalle`:
```text
Drawer derecho
```
Mostrar:
lote;
modelo;
versión;
cantidad esperada;
cantidad observada;
desviación;
fecha;
variables relevantes;
señal generada;
estado de revisión.
---
64. Usuarios
Ruta:
```text
/users
```
Sólo Administrador.
Tabla:
nombre;
correo;
rol;
estado;
última actividad;
acciones.
---
65. Invitar usuario
Botón:
```text
Invitar usuario
```
abre drawer.
Campos:
```text
Nombre
Correo
Rol
```
Botón:
```text
Enviar invitación
```
Flujo:
```text
Validar
    |
Loading
    |
Backend
    |
Correo
    |
Success
```
Mensaje:
```text
Invitación enviada correctamente.
```
El usuario debe aparecer con estado:
```text
Invitación pendiente
```
---
66. Reenviar invitación
Si el estado es:
```text
Invitación pendiente
```
mostrar:
```text
Reenviar invitación
```
Antes de enviar puede utilizarse una confirmación breve.
Resultado:
```text
Invitación reenviada correctamente.
```
---
67. Desactivar usuario
Al presionar:
```text
Desactivar
```
mostrar modal:
```text
¿Desactivar usuario?

El usuario ya no podrá ingresar al sistema.

[Cancelar] [Desactivar]
```
Durante ejecución:
```text
Desactivando...
```
Después:
```text
Usuario desactivado correctamente.
```
---
68. Activar usuario
Mismo patrón:
```text
¿Activar usuario?
```
Después:
```text
Usuario activado correctamente.
```
---
69. Configuración
Ruta:
```text
/settings
```
Secciones:
```text
General
Seguridad
Tolerancias
Notificaciones
Integraciones
Auditoría
```
Sólo mostrar opciones permitidas.
---
70. Configuración de tolerancias
Debe mostrar:
regla;
valor;
unidad;
versión;
vigencia;
usuario modificador;
fecha.
Al modificar:
```text
Editar
    |
Formulario
    |
Validación
    |
Confirmación
    |
Guardar
    |
Auditoría
```
No sobrescribir silenciosamente el historial.
---
71. Notificaciones
El icono de notificaciones debe abrir un panel.
Mostrar:
alertas;
cambios relevantes;
eventos;
invitaciones;
información operativa.
Al presionar una notificación:
```text
Abrir recurso relacionado
```
Puede abrir drawer cuando el detalle sea contextual.
---
72. Menú de usuario
Al presionar avatar:
```text
Perfil
Preferencias
Cerrar sesión
```
Debe utilizar dropdown.
---
73. Logout
Al presionar:
```text
Cerrar sesión
```
debe:
cerrar sesión;
limpiar información sensible;
invalidar cache sensible;
redirigir a `/login`.
No conservar información privada en estado del cliente después del logout.
---
74. Formularios
Todo formulario debe:
tener labels;
validación;
mensajes junto al campo;
estado loading;
prevención de doble envío;
manejo de error;
conservación de información cuando sea seguro.
---
75. Formularios dentro de Drawer
Estructura:
```text
Header
Contenido
Footer fijo
```
Footer:
```text
Cancelar
Guardar
```
El footer debe permanecer accesible aunque el contenido tenga scroll.
---
76. Cambios sin guardar
Si el usuario intenta cerrar un formulario modificado:
```text
¿Descartar cambios?

Tienes cambios que aún no se han guardado.

[Seguir editando]
[Descartar]
```
---
77. Uso de Modal
Utilizar modal para:
confirmaciones;
acciones críticas;
formularios pequeños.
No utilizar modal para páginas completas.
---
78. Uso de Drawer
Utilizar drawer para:
detalles;
revisión rápida;
edición contextual;
historial;
información relacionada.
Patrón estándar:
```text
Tabla
    |
Detalle
    |
Drawer derecho
```
---
79. Uso de página completa
Utilizar página para:
dashboards;
expedientes;
análisis;
configuraciones grandes;
formularios complejos.
---
80. Toasts
Éxito:
```text
Lote registrado correctamente.
```
Error:
```text
No se pudo guardar el lote.
```
Los mensajes deben ser concretos.
---
81. Loading
Cada componente debe manejar su propio loading.
Preferir:
```text
Skeleton
```
sobre:
```text
Spinner de pantalla completa
```
salvo procesos que realmente bloqueen toda la aplicación.
---
82. Empty State
Cada módulo debe tener un estado vacío.
Ejemplo:
```text
No hay lotes registrados.

Cuando se registre un lote, aparecerá aquí.
```
Si existe acción:
```text
[Registrar lote]
```
---
83. Error State
Ejemplo:
```text
No pudimos cargar esta información.
[Reintentar]
```
No mostrar stack traces.
---
84. Botones
Todo botón debe tener una acción real.
Para cada botón debe estar definido:
qué hace;
quién puede utilizarlo;
qué llamada ejecuta;
qué ocurre durante loading;
qué ocurre si funciona;
qué ocurre si falla;
qué feedback recibe;
si requiere confirmación;
qué vista se actualiza.
No debe haber botones decorativos sin comportamiento.
---
85. Estados de botones
Cada botón importante debe contemplar:
```text
default
hover
focus
active
disabled
loading
```
---
86. Tablas
Las tablas deben incluir cuando corresponda:
búsqueda;
filtros;
ordenamiento;
paginación;
selección;
acciones;
loading;
empty;
error.
---
87. Paginación
Mostrar:
```text
1–20 de 248
```
Controles:
```text
Anterior
1
2
3
Siguiente
```
No descargar miles de registros sin necesidad.
---
88. Ordenamiento
Columnas ordenables deben indicar visualmente:
```text
Ascendente
Descendente
```
El orden debe enviarse al backend cuando corresponda.
---
89. Exportación
Cuando el usuario tenga permiso:
```text
Exportar
```
Opciones:
```text
CSV
PDF
```
La exportación debe respetar:
permisos;
filtros;
alcance de datos.
---
90. Búsqueda global
Puede implementarse:
```text
Ctrl + K
```
Debe permitir buscar recursos autorizados.
No debe devolver información que el usuario no puede consultar.
---
91. Responsive
La aplicación debe funcionar correctamente en:
desktop;
laptop;
tablet;
móvil.
El diseño principal puede estar optimizado para escritorio, pero ninguna vista debe romperse en resoluciones menores.
---
92. Tablas en móvil
No intentar mantener todas las columnas.
Opciones:
ocultar columnas secundarias;
convertir filas en cards;
scroll horizontal controlado;
abrir detalle mediante drawer.
---
93. Accesibilidad
Obligatorio:
teclado;
focus visible;
labels;
contraste;
nombres accesibles;
diálogo con focus controlado;
Escape;
soporte para lectores de pantalla donde corresponda.
---
94. Protección de rutas
Rutas públicas:
```text
/login
/forgot-password
/activate-account
```
Rutas protegidas:
```text
/dashboard
/lots
/custody
/transport
/receptions
/weighings
/mass-balance
/alerts
/audit
/ml
```
Administrativas:
```text
/users
/settings
```
---
95. Usuario no autenticado
Si intenta:
```text
/lots
```
debe ser redirigido:
```text
/login
```
Si el usuario está autenticado pero no tiene permisos:
```text
403
```
---
96. Página 403
Contenido:
```text
Acceso no autorizado

No tienes permisos para consultar este recurso.

[Volver al inicio]
```
---
97. Página 404
Contenido:
```text
Página no encontrada

El recurso solicitado no existe o ya no está disponible.

[Volver al inicio]
```
---
98. Página 500
Contenido:
```text
Algo salió mal

No pudimos completar la solicitud.

[Reintentar]
[Volver al inicio]
```
No mostrar información técnica interna.
---
99. Cliente HTTP
No hacer llamadas HTTP directamente desde cada componente.
Evitar:
```text
React Component
    |
fetch(...)
```
como patrón general.
Usar:
```text
Component
    |
Use Case
    |
Port
    |
API Adapter
    |
HTTP
    |
Backend
```
Debe existir un cliente HTTP centralizado.
---
100. TanStack Query
Utilizar para:
consultas;
cache;
invalidación;
refetch;
estados de carga;
estados de error.
Después de una mutación:
```text
Mutation
    |
Success
    |
Invalidate query
    |
UI actualizada
```
---
101. Zustand
Utilizar únicamente para estado cliente/UI cuando sea necesario.
Ejemplos:
preferencias;
filtros globales puntuales;
estado de navegación;
UI.
No utilizarlo como sustituto general del estado servidor.
---
102. Formularios
Utilizar:
```text
React Hook Form
+
Zod
```
El frontend valida para mejorar UX.
El backend continúa siendo la autoridad.
---
103. Componentes reutilizables
Crear un sistema común:
```text
Button
Input
Select
DatePicker
Badge
StatusBadge
Table
Drawer
Modal
Dialog
Toast
Skeleton
EmptyState
ErrorState
Pagination
FilterBar
Timeline
FileViewer
```
No duplicar componentes visualmente equivalentes.
---
104. Componentes específicos del dominio
Ejemplos:
```text
LotStatusBadge
CustodyTimeline
MassBalanceCard
AlertSeverityBadge
EvidenceViewer
AuditEventTimeline
MLDeviationCard
```
Estos componentes presentan información.
No deben contener reglas críticas de negocio.
---
105. Drawer reutilizable
Debe existir un componente base:
```text
DetailDrawer
```
Capacidades:
abrir;
cerrar;
loading;
error;
contenido;
footer;
ancho configurable;
Escape;
overlay;
cambios sin guardar.
---
106. Seguridad del frontend
Nunca almacenar en frontend:
service role key;
secretos privados;
credenciales administrativas;
claves de servidor.
Las variables públicas sólo deben contener valores destinados al cliente.
---
107. Logging
No registrar:
```text
password
tokens
service role keys
datos sensibles completos
```
Eliminar logs de desarrollo antes de producción.
---
108. Manejo de errores HTTP
Debe mapear como mínimo:
```text
400
401
403
404
409
422
429
500
503
```
Ejemplo:
```text
403
No tienes permisos para realizar esta acción.
```
No mostrar directamente:
```text
Forbidden
```
---
109. Optimización
Aplicar:
lazy loading;
code splitting;
cache;
paginación;
debounce;
imágenes optimizadas;
reducción de renders innecesarios.
No introducir optimizaciones complejas sin necesidad.
---
110. Fechas
Utilizar formato consistente:
```text
24/09/2026
```
Fecha y hora:
```text
24/09/2026 10:35
```
La zona horaria debe centralizarse.
---
111. Cantidades
Siempre mostrar unidad.
Ejemplo:
```text
125.40 kg
```
Nunca:
```text
125.40
```
sin contexto.
---
112. Identificadores
Ejemplo:
```text
LOT-2026-00021
```
Cuando sea posible copiar:
```text
Copiar
```
Después:
```text
Copiado
```
---
113. Clean Code
El código debe cumplir:
nombres descriptivos;
funciones pequeñas;
responsabilidad única;
baja duplicación;
tipado estricto;
manejo explícito de errores;
ausencia de código muerto;
imports limpios;
separación de responsabilidades.
---
114. TypeScript
Utilizar TypeScript strict.
Evitar:
```typescript
any
```
salvo justificación.
Preferir:
```typescript
unknown
```
cuando el tipo sea desconocido.
---
115. Componentes React
Evitar componentes monolíticos.
Incorrecto:
```text
DashboardPage
    1500 líneas
```
Preferir:
```text
DashboardPage
├── DashboardHeader
├── KPIGrid
├── AlertsWidget
├── ActivityChart
└── RecentLotsTable
```
---
116. Hooks
Cada hook debe tener responsabilidad clara.
Ejemplos:
```text
useLots
useLotDetail
useAlerts
useAuditCase
useCurrentUser
usePermissions
```
No crear hooks gigantes.
---
117. Reglas de arquitectura frontend
Prohibido:
```text
UI
    |
    └── PostgreSQL
```
Prohibido:
```text
Component
    |
    └── lógica crítica de negocio
```
Prohibido:
```text
Domain
    |
    └── Next.js
```
Prohibido:
```text
Component
    |
    └── crear repositorios concretos
```
---
118. Regla de autoridad
Las validaciones del frontend mejoran la experiencia.
Las reglas críticas pertenecen al backend.
Ejemplo:
```text
Frontend
    |
Validación rápida
    |
Backend
    |
Validación definitiva
```
Nunca asumir que una regla es segura sólo porque el botón está deshabilitado.
---
119. Invitaciones y correo desde arquitectura
El frontend debe consumir un endpoint de backend.
Conceptualmente:
```text
Frontend
    |
InviteUserUseCase
    |
Port
    |
Backend API
    |
Application
    |
EmailPort
    |
Email Adapter
    |
Proveedor de correo
```
El frontend nunca debe comunicarse directamente con un proveedor de correo utilizando secretos.
---
120. Estados de usuario
La interfaz debe diferenciar:
```text
Invitación pendiente
Activo
Inactivo
Invitación expirada
```
Cada estado debe tener badge consistente.
---
121. Auditoría de acciones
Las acciones relevantes deben generar registros en backend:
invitación;
activación;
desactivación;
modificación de tolerancia;
revisión de alerta;
cierre de revisión;
cambios de configuración.
El frontend únicamente ejecuta la operación.
---
122. Flujo genérico de cualquier operación
Toda operación importante debe seguir:
```text
Usuario
    |
Acción
    |
Validación
    |
Loading
    |
Use Case
    |
Port
    |
API Adapter
    |
Backend
    |
Respuesta
    |
Success / Error
    |
Feedback
    |
Actualización UI
```
---
123. Flujo de éxito
Ejemplo:
```text
Presionar Guardar
    |
Validar
    |
Guardando...
    |
API
    |
200/201
    |
Actualizar cache
    |
Cerrar drawer si corresponde
    |
Toast
```
---
124. Flujo de error
```text
Presionar Guardar
    |
Validar
    |
API
    |
Error
    |
Mostrar mensaje
    |
Conservar formulario
    |
Permitir reintento
```
No borrar la información introducida por el usuario sin motivo.
---
125. Cambios concurrentes
Si el backend detecta que otro usuario modificó el recurso:
```text
Este registro fue actualizado por otro usuario.

Actualiza la información antes de continuar.
```
Debe existir una forma de recuperar la información actualizada.
---
126. Estado de conexión
Cuando no exista conexión:
```text
No hay conexión con el servidor.

Verifica tu conexión e intenta nuevamente.
```
No afirmar que una operación se guardó si el backend no confirmó la operación.
---
127. Principio offline
El offline-first corresponde principalmente a `APP_MINERA`.
`WEB_MINERA` debe estar preparada para consumir los datos sincronizados y representar correctamente estados de sincronización cuando sean parte del dominio.
---
128. Animaciones de navegación
Las transiciones entre vistas deben ser discretas.
No utilizar transiciones largas.
Priorizar:
```text
fade
small translate
drawer slide
modal scale/fade
```
Evitar animaciones que ralenticen la operación.
---
129. Animaciones de tablas
Al actualizar datos:
evitar desaparecer y reaparecer toda la tabla;
mantener estructura estable;
actualizar únicamente contenido necesario cuando sea posible.
---
130. Animaciones de badges
Los cambios de estado pueden utilizar una pequeña transición de color/opacidad.
No utilizar:
```text
parpadeo
```
para estados normales.
---
131. Z-index
Definir jerarquía central:
```text
base
dropdown
sticky
drawer
overlay
modal
toast
```
No usar valores arbitrarios como:
```text
z-index: 999999
```
sin estrategia.
---
132. Persistencia de contexto
Al abrir un detalle:
```text
Tabla
    |
Drawer
```
al cerrar debe conservar:
página;
filtros;
búsqueda;
ordenamiento.
El usuario no debe perder su contexto.
---
133. Actualización después de mutación
Ejemplo:
```text
Editar usuario
    |
Guardar
    |
Success
    |
Invalidar users query
    |
Tabla actualizada
```
No exigir F5 al usuario.
---
134. Regla de consistencia
Todos los módulos deben utilizar:
mismo header;
mismo sidebar;
mismos botones;
mismos badges;
mismos drawers;
mismos modales;
mismos mensajes;
mismos estados de carga.
No crear una UX diferente para cada módulo.
---
135. Sistema de diseño
Centralizar:
```text
colors
spacing
typography
radius
shadows
breakpoints
transitions
z-index
```
Los componentes deben consumir estos tokens.
---
136. Pruebas
Unitarias
Probar:
validaciones;
transformaciones;
funciones;
utilidades.
Componentes
Probar:
botones;
formularios;
drawer;
modal;
tabla;
estados.
E2E
Probar como mínimo:
```text
Login
Logout
Recuperación
Activación
Invitación
Consulta de lote
Detalle de lote
Revisión de alerta
Auditoría
Control de permisos
```
---
137. E2E de Login
```text
Abrir /login
    |
Ingresar correo
    |
Ingresar contraseña
    |
Ingresar
    |
Loading
    |
Autenticación
    |
Dashboard
```
También:
```text
Credenciales incorrectas
Cuenta inactiva
Sesión expirada
Logout
```
---
138. E2E de detalle
```text
Lotes
    |
Buscar
    |
Detalle
    |
Drawer aparece
    |
Skeleton
    |
Datos
    |
Cerrar
    |
Tabla conserva contexto
```
---
139. E2E de invitación
```text
Administrador
    |
Usuarios
    |
Invitar
    |
Formulario
    |
Enviar
    |
Loading
    |
Backend
    |
Correo
    |
Success
    |
Estado pendiente
```
---
140. E2E de activación
```text
Enlace
    |
Validación
    |
Formulario
    |
Contraseña
    |
Activar
    |
Success
    |
Login
```
---
141. CI
Debe existir como mínimo:
```text
Lint
Type Check
Unit Tests
Build
```
Posteriormente:
```text
Integration Tests
E2E
Security Checks
SonarQube
```
---
142. Definition of Done
La web no se considera terminada si únicamente las páginas visualmente existen.
Debe cumplir:
[ ] Login funcional.
[ ] No existe registro público.
[ ] Recuperación de contraseña.
[ ] Invitación por correo.
[ ] Activación de cuenta.
[ ] Protección de rutas.
[ ] Roles y permisos.
[ ] Dashboard por rol.
[ ] Sidebar.
[ ] Header.
[ ] Breadcrumb.
[ ] Notificaciones.
[ ] Perfil.
[ ] Logout.
[ ] Lotes.
[ ] Custodia.
[ ] Transporte.
[ ] Recepción.
[ ] Pesajes.
[ ] Balance.
[ ] Alertas.
[ ] Auditoría.
[ ] ML.
[ ] Usuarios.
[ ] Configuración.
[ ] Drawers.
[ ] Modales.
[ ] Formularios.
[ ] Validaciones.
[ ] Loading states.
[ ] Empty states.
[ ] Error states.
[ ] Responsive.
[ ] Accesibilidad.
[ ] Pruebas.
[ ] Lint.
[ ] Type check.
[ ] Build de producción.
[ ] Sin secretos expuestos.
[ ] Sin lógica crítica únicamente en frontend.
[ ] Código limpio.
[ ] Componentes reutilizables.
[ ] Documentación actualizada.
---
143. Orden de implementación
El desarrollador debe seguir este orden:
Fase 1. Base
inicializar Next.js;
TypeScript strict;
Tailwind;
sistema de diseño;
ESLint;
Prettier.
Fase 2. Arquitectura
Crear:
```text
domain
application
ports
adapters
infrastructure
presentation
shared
```
Fase 3. Componentes base
Crear:
```text
Button
Input
Select
Badge
Table
Drawer
Modal
Dialog
Toast
Skeleton
EmptyState
ErrorState
Pagination
FilterBar
Timeline
```
Fase 4. Autenticación
Implementar:
login;
sesión;
logout;
recuperación;
activación;
protección de rutas.
Fase 5. Layout
Implementar:
sidebar;
header;
breadcrumb;
usuario;
notificaciones.
Fase 6. Dashboard
Implementar dashboard por rol.
Fase 7. Módulos
Implementar:
```text
Lotes
Custodia
Transporte
Recepción
Pesajes
Balance
Alertas
Auditoría
ML
Usuarios
Configuración
```
Fase 8. Refinamiento
Implementar:
responsive;
accesibilidad;
animaciones;
estados;
performance.
Fase 9. Testing
Implementar:
unit;
component;
E2E.
Fase 10. Calidad
Ejecutar:
lint;
typecheck;
tests;
build;
análisis de calidad;
revisión de seguridad.
---
144. Reglas obligatorias de Clean Code
El desarrollador debe:
utilizar nombres descriptivos;
mantener funciones pequeñas;
mantener componentes pequeños;
evitar duplicación;
aplicar responsabilidad única;
mantener tipado estricto;
separar UI y lógica;
separar dominio e infraestructura;
manejar errores explícitamente;
eliminar código muerto;
eliminar imports no utilizados;
documentar decisiones complejas;
evitar abstracciones innecesarias;
evitar dependencias innecesarias;
mantener una estructura predecible.
---
145. Regla de componentes grandes
Si un componente comienza a concentrar demasiadas responsabilidades:
```text
Data fetching
+
business logic
+
form
+
table
+
drawer
+
modal
+
notifications
```
debe dividirse.
Ejemplo:
```text
LotsPage
├── LotsToolbar
├── LotsFilters
├── LotsTable
├── LotDetailDrawer
└── LotExportMenu
```
---
146. Regla de lógica de negocio
La interfaz puede:
```text
mostrar
validar formato
solicitar
transformar para presentación
```
La interfaz no debe decidir reglas críticas.
Ejemplo incorrecto:
```text
if deviation > 3:
    fraud = true
```
El frontend no debe determinar fraude.
---
147. Regla de ML
ML sólo proporciona una estimación o señal.
La UI debe comunicar:
```text
Cantidad esperada
Cantidad observada
Desviación
Modelo
Versión
Señal para revisión
```
No debe afirmar automáticamente:
```text
Fraude
Ilegalidad
Culpabilidad
```
---
148. Regla de auditoría
La UI no crea por sí misma la verdad de auditoría.
El backend registra:
actor;
operación;
timestamp;
entidad;
resultado;
contexto.
La interfaz únicamente inicia la operación.
---
149. Regla de seguridad
Nunca confiar exclusivamente en:
```text
hidden button
disabled button
frontend route guard
```
El backend debe volver a verificar permisos.
---
150. Regla final de desarrollo
Cada funcionalidad debe implementarse verticalmente.
Ejemplo:
```text
UI
    |
Use Case
    |
Port
    |
API Adapter
    |
Backend
    |
Application
    |
Domain
    |
Repository Adapter
    |
Database
```
No crear primero una interfaz completamente desconectada y posteriormente intentar conectarla.
---
151. Resultado esperado
La entrega final debe ser una aplicación web profesional, coherente y mantenible.
Debe sentirse como una plataforma integral y no como un conjunto de páginas.
Cada interacción debe tener un comportamiento definido:
```text
Acción
    |
Validación
    |
Loading
    |
Procesamiento
    |
Resultado
    |
Feedback
    |
Actualización
```
Cada módulo debe tener:
```text
Success
Loading
Empty
Error
Disabled
Permission
Responsive
Accessible
```
La aplicación debe respetar la arquitectura hexagonal definida para `WEB_MINERA`, mantener separación de responsabilidades y permitir que los componentes evolucionen sin generar acoplamiento innecesario.
---
152. Criterio definitivo de finalización
`WEB_MINERA` estará lista para entrega cuando el desarrollador pueda demostrar:
```text
Autenticación
+
Invitación por correo
+
Control de roles
+
Dashboard
+
Navegación
+
Módulos operativos
+
Detalles mediante Drawer
+
Formularios
+
Confirmaciones
+
Estados de carga
+
Estados vacíos
+
Errores
+
Auditoría
+
ML
+
Responsive
+
Accesibilidad
+
Seguridad
+
Pruebas
+
Clean Code
+
Build
```
y cada flujo crítico haya sido probado de extremo a extremo.
La calidad final no se medirá únicamente por la apariencia visual. Debe existir coherencia entre:
```text
UX/UI
+
Arquitectura
+
Seguridad
+
Backend
+
Datos
+
Pruebas
+
Mantenibilidad
```
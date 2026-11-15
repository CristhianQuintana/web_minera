---
name: "Solicitud de Cambio (RFC)"
about: "Propuesta formal de modificación del sistema de gestión minera"
title: "[RFC] "
labels: "change-request, pendiente-evaluacion"
---

### 1. DESCRIPCIÓN DEL CAMBIO SOLICITADO

- **Módulo / Componente Afectado:** Panel web de administración de usuarios y gestión de empleados.
- **Tipo de Cambio:** Cambio de Requisito / Nueva Funcionalidad.
- **Justificación:** Actualmente se requiere implementar desde el panel web el registro y administración de empleados de la organización. Esta funcionalidad permitirá centralizar la incorporación de personal, asignar roles según las responsabilidades de cada empleado y controlar su acceso a las funcionalidades correspondientes del sistema. Con ello se mejorará la administración de usuarios, la seguridad y el control de accesos.

### 2. ANÁLISIS DE IMPACTO

- **Impacto en Tiempo / Esfuerzo:** Pendiente de estimación técnica.
- **Nivel de Riesgo:** Medio.
- **Justificación del Riesgo:** Una asignación incorrecta de roles o permisos podría permitir que un empleado acceda a funcionalidades no autorizadas o impedirle acceder a las necesarias para su trabajo.

### 3. CRITERIOS DE ACEPTACIÓN

- El administrador puede registrar nuevos empleados desde el panel web.
- El sistema permite ingresar los datos necesarios para identificar a cada empleado.
- El administrador puede asignar un rol al empleado durante su registro.
- Los roles determinan las funcionalidades y permisos a los que puede acceder cada empleado.
- El sistema valida los datos obligatorios antes de registrar al empleado.
- Se evita la creación de cuentas duplicadas.
- Las credenciales y los mecanismos de autenticación se gestionan de forma segura.
- Se realizan pruebas unitarias y de integración correspondientes.
- Las pruebas se ejecutan sin errores y no se afectan las funcionalidades existentes.

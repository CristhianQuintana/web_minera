# Aplicar tablas en el proyecto Supabase

**Archivo SQL completo:** [`bootstrap_full.sql`](./bootstrap_full.sql)  
(incluye migraciones `0001` + `0004` + `0005` + `0006` y organización piloto)

## Por qué hace falta este paso

Con la **anon/publishable key** se puede consumir la API, pero **no se pueden crear tablas**.  
Hace falta ejecutar SQL en el Dashboard (o usar la **database password** / `service_role` + conexión Postgres).

## Pasos (SQL Editor — recomendado)

1. Inicia sesión en https://supabase.com/dashboard  
2. Abre tu proyecto  
3. Ve a **SQL → New query**  
4. Copia **todo** el contenido de `database/bootstrap_full.sql`  
5. Pulsa **Run**  
6. Verifica en **Table Editor** que existan: `organizations`, `profiles`, `lots`, `custody_transfers`, `invitations`, `alerts`, etc.

## Después del SQL — usuario admin

1. **Authentication → Users → Add user**  
   - Email: el que usarás en la web  
   - Password: la que elijas  
   - Auto Confirm: sí  
2. Ejecuta en SQL (ajustando email y nombre):

```sql
-- Tras crear el usuario en Auth, promocionar a admin de la cooperativa piloto
insert into public.profiles (id, full_name, role, organization_id, status, email, invitation_status)
select u.id, 'Administrador', 'admin', 'e857fa80-1678-4b27-b80f-c38f471a8931', 'active', u.email, 'active'
from auth.users u
where u.email = 'TU_CORREO@dominio.com'
on conflict (id) do update set
  role = 'admin',
  status = 'active',
  invitation_status = 'active',
  organization_id = excluded.organization_id,
  email = excluded.email;
```

O usa `database/seeds/promote_admin.sql` si ya está alineado.

## Variables de entorno

Configura en backend y frontend (sin `ALLOW_DEMO_AUTH` ni flags demo):

```
APP_ENV=production
SUPABASE_URL=https://<proyecto>.supabase.co
SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_ROLE_KEY=<service_role>   # necesario para invitar usuarios
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_API_URL=https://<backend>
```

## Autenticación

Solo se admite **Supabase Auth** (JWT reales). No existe login demo ni tokens `demo-*`.

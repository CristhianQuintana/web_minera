# Aplicar tablas en el nuevo proyecto Supabase

**Proyecto:** `https://mxkegjxjhmlsujfjmaxw.supabase.co`  
**Archivo SQL completo:** [`bootstrap_full.sql`](./bootstrap_full.sql)  
(incluye migraciones `0001` + `0004` + `0005` + `0006` + organización demo)

## Por qué hace falta este paso

Con la **anon/publishable key** se puede consumir la API, pero **no se pueden crear tablas**.  
Hace falta ejecutar SQL en el Dashboard (o usar la **database password** / `service_role` + conexión Postgres).

## Pasos (SQL Editor — recomendado)

1. Inicia sesión en https://supabase.com/dashboard  
2. Abre el proyecto `mxkegjxjhmlsujfjmaxw`  
3. Ve a **SQL → New query**  
4. Copia **todo** el contenido de `database/bootstrap_full.sql`  
5. Pulsa **Run**  
6. Verifica en **Table Editor** que existan: `organizations`, `profiles`, `lots`, `custody_transfers`, `invitations`, `alerts`, etc.

## Después del SQL — usuario admin

1. **Authentication → Users → Add user**  
   - Email: el que usarás en la web (p. ej. `cristhian@gmail.com`)  
   - Password: la que elijas  
   - Auto Confirm: sí  
2. Ejecuta en SQL (ajustando email y nombre):

```sql
-- Tras crear el usuario en Auth, promocionar a admin
insert into public.profiles (id, full_name, role, organization_id, status, email, invitation_status)
select u.id, 'Administrador', 'admin', 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee', 'active', u.email, 'active'
from auth.users u
where u.email = 'cristhian@gmail.com'
on conflict (id) do update set
  role = 'admin',
  status = 'active',
  invitation_status = 'active',
  organization_id = excluded.organization_id,
  email = excluded.email;
```

O usa `database/seeds/promote_admin.sql` si ya está alineado.

## Credenciales ya configuradas en local

Archivos actualizados (gitignored donde corresponde):

- `backend/.env`
- `.env`
- `frontend/.env.local`

```
SUPABASE_URL=https://mxkegjxjhmlsujfjmaxw.supabase.co
SUPABASE_ANON_KEY=sb_publishable_RqbCkFxs4eidqmEKonxIGA_Dm26QiTZ
```

Para operaciones admin (invitar usuarios) hace falta además:

```
SUPABASE_SERVICE_ROLE_KEY=<Settings → API → service_role>
```

## Mientras no existan tablas

El **login demo** del PMV sigue funcionando sin Supabase:

- Correo: `cristhian@gmail.com`
- Contraseña: `Cristhian123`
- URL local: http://localhost:3000/login

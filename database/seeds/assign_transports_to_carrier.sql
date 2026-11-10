-- WEB_MINERA | Asignar transportes a un usuario transportista (carrier)
-- Ejecutar en Supabase > SQL Editor.
--
-- Objetivo (evidencia fotográfica / listado transportista):
--   Que existan transportes con assigned_to = perfil role 'carrier',
--   para que el transportista vea "transportes asignados" con estados.
--
-- Requisitos:
--   1) Debe existir en Auth un usuario con correo transportista.prueba@cooperativa.org
--      (o ya un profile con role = 'carrier' en la org piloto).
--   2) Si el correo no existe en auth.users, el script solo reporta NOTICE y no asigna.
--
-- Idempotente: puede re-ejecutarse.

begin;

insert into public.organizations (id, name)
values ('e857fa80-1678-4b27-b80f-c38f471a8931', 'Cooperativa piloto')
on conflict (id) do nothing;

do $$
declare
  v_org_id uuid := 'e857fa80-1678-4b27-b80f-c38f471a8931';
  v_carrier_id uuid;
  v_carrier_email text;
  v_carrier_name text;
  v_updated int;
begin
  -- 1) Preferir un profile carrier/transporter ya activo en la org.
  select p.id, coalesce(p.email, u.email), coalesce(p.full_name, 'Transportista piloto')
    into v_carrier_id, v_carrier_email, v_carrier_name
  from public.profiles p
  left join auth.users u on u.id = p.id
  where p.organization_id = v_org_id
    and p.role in ('carrier', 'transporter')
    and coalesce(p.status, 'active') = 'active'
  order by case when p.role = 'carrier' then 0 else 1 end, p.created_at nulls last
  limit 1;

  -- 2) Si no hay carrier, crear/actualizar profile desde auth user demo.
  if v_carrier_id is null then
    select u.id, u.email,
           coalesce(u.raw_user_meta_data->>'full_name', 'Carlos Rojas Transportista')
      into v_carrier_id, v_carrier_email, v_carrier_name
    from auth.users u
    where lower(u.email) in (
      'transportista.prueba@cooperativa.org',
      'carrier.prueba@cooperativa.org',
      'transportista@cooperativa.org'
    )
    order by case lower(u.email)
      when 'transportista.prueba@cooperativa.org' then 0
      when 'carrier.prueba@cooperativa.org' then 1
      else 2
    end
    limit 1;

    if v_carrier_id is null then
      raise notice 'NO HAY USUARIO TRANSPORTISTA. Crea en Auth el correo transportista.prueba@cooperativa.org y vuelve a ejecutar este script.';
      return;
    end if;

    insert into public.profiles (
      id, full_name, role, organization_id, status, email, invitation_status
    )
    values (
      v_carrier_id,
      v_carrier_name,
      'carrier',
      v_org_id,
      'active',
      v_carrier_email,
      'active'
    )
    on conflict (id) do update set
      role = 'carrier',
      status = 'active',
      invitation_status = 'active',
      organization_id = excluded.organization_id,
      email = excluded.email,
      full_name = excluded.full_name,
      updated_at = now();
  else
    update public.profiles
    set role = 'carrier',
        status = 'active',
        invitation_status = 'active',
        updated_at = now()
    where id = v_carrier_id
      and role <> 'carrier';
  end if;

  -- 3) Reasignar transportes de la org piloto al transportista.
  update public.transports t
  set assigned_to = v_carrier_id,
      driver = coalesce(nullif(trim(t.driver), ''), v_carrier_name),
      notes = coalesce(t.notes, 'Transporte asignado a transportista piloto.')
  from public.lots l
  where t.lot_id = l.id
    and l.organization_id = v_org_id;

  get diagnostics v_updated = row_count;

  raise notice 'Transportista listo: % (%) — transportes reasignados: %',
    v_carrier_email, v_carrier_id, v_updated;
end $$;

-- Evidencia rápida
select
  p.email,
  p.full_name,
  p.role,
  p.status,
  count(t.id) as transportes_asignados,
  count(*) filter (where t.status = 'pending') as pending,
  count(*) filter (where t.status = 'in_progress') as in_progress,
  count(*) filter (where t.status = 'completed') as completed
from public.profiles p
left join public.transports t on t.assigned_to = p.id
where p.role in ('carrier', 'transporter')
  and p.organization_id = 'e857fa80-1678-4b27-b80f-c38f471a8931'
group by p.email, p.full_name, p.role, p.status;

commit;

-- Evita invitaciones pendientes duplicadas por organización y correo.
-- Revoca duplicados históricos conservando la invitación pendiente más reciente.
with ranked as (
  select id, row_number() over (
    partition by organization_id, lower(email)
    order by created_at desc, id desc
  ) as position
  from public.invitations
  where status = 'pending'
)
update public.invitations i
set status = 'revoked'
from ranked r
where i.id = r.id and r.position > 1;

-- Reserva atómica para impedir activaciones concurrentes con el mismo token.
alter table public.invitations drop constraint if exists invitations_status_check;
alter table public.invitations add constraint invitations_status_check
  check (status in ('pending', 'accepting', 'accepted', 'expired', 'revoked'));

create or replace function public.claim_invitation(p_token_hash text)
returns setof public.invitations
language plpgsql
security definer
set search_path = public
as $$
begin
  update public.invitations
  set status = 'expired'
  where token_hash = p_token_hash and status = 'pending' and expires_at <= now();

  return query
  update public.invitations i
  set status = 'accepting'
  where i.token_hash = p_token_hash and i.status = 'pending' and i.expires_at > now()
  returning i.*;
end;
$$;

revoke all on function public.claim_invitation(text) from public, anon, authenticated;
grant execute on function public.claim_invitation(text) to service_role;

create unique index if not exists invitations_one_pending_per_org_email_idx
  on public.invitations (organization_id, lower(email))
  where status = 'pending';

-- Productor puede registrar/asignar transportes (assigned_to = transportista).
-- Transportista sigue viendo/actualizando solo los suyos.

drop policy if exists transports_insert on public.transports;
create policy transports_insert on public.transports
  for insert with check (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and public.current_role() in ('transporter', 'carrier', 'admin', 'producer')
  );

drop policy if exists transports_update on public.transports;
create policy transports_update on public.transports
  for update using (
    exists (
      select 1 from public.lots l
      where l.id = lot_id and l.organization_id = public.current_org_id()
    )
    and (
      public.current_role() = 'admin'
      or public.current_role() = 'producer'
      or (
        public.current_role() in ('transporter', 'carrier')
        and (assigned_to = auth.uid() or assigned_to is null)
      )
    )
  );

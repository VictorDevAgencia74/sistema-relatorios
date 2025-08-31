create table public.tipos_relatorio (
  id serial not null,
  nome text not null,
  template text not null,
  campos jsonb not null,
  destinatario_whatsapp text null,
  constraint tipos_relatorio_pkey primary key (id)
) TABLESPACE pg_default;
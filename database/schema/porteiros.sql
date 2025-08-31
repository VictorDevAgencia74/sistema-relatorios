create table public.porteiros (
  id uuid not null default extensions.uuid_generate_v4 (),
  nome text not null,
  codigo_acesso text not null,
  ativo boolean null default true,
  criado_em timestamp without time zone null default now(),
  constraint porteiros_pkey primary key (id),
  constraint porteiros_codigo_acesso_key unique (codigo_acesso)
) TABLESPACE pg_default;
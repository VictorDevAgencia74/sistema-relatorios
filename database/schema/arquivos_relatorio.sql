create table public.arquivos_relatorio (
  id serial not null,
  relatorio_id uuid not null,
  nome character varying(255) not null,
  nome_arquivo character varying(255) not null,
  caminho text not null,
  url text not null,
  tamanho integer not null,
  tipo character varying(100) null,
  criado_em timestamp with time zone null default now(),
  constraint arquivos_relatorio_pkey primary key (id),
  constraint idx_relatorio_id unique (relatorio_id, nome_arquivo),
  constraint fk_relatorio foreign KEY (relatorio_id) references relatorios (id) on delete CASCADE
) TABLESPACE pg_default;

create index IF not exists idx_arquivos_relatorio_id on public.arquivos_relatorio using btree (relatorio_id) TABLESPACE pg_default;

create index IF not exists idx_arquivos_criado_em on public.arquivos_relatorio using btree (criado_em) TABLESPACE pg_default;
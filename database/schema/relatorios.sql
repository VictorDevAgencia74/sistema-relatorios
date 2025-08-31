create table public.relatorios (
  id uuid not null default extensions.uuid_generate_v4 (),
  porteiro_id uuid null,
  tipo_id integer null,
  dados jsonb not null,
  enviado_em timestamp without time zone null default now(),
  destinatario_whatsapp text not null,
  criado_em timestamp with time zone null default now(),
  fotos json null,
  status character varying(20) null default 'PENDENTE'::character varying,
  motorista text null,
  valor numeric(10, 2) null,
  documentos jsonb null,
  constraint relatorios_pkey primary key (id),
  constraint relatorios_porteiro_id_fkey foreign KEY (porteiro_id) references porteiros (id),
  constraint relatorios_tipo_id_fkey foreign KEY (tipo_id) references tipos_relatorio (id),
  constraint relatorios_status_check check (
    (
      (status)::text = any (
        array[
          ('PENDENTE'::character varying)::text,
          ('EM_DP'::character varying)::text,
          ('EM_TRAFEGO'::character varying)::text,
          ('COBRADO'::character varying)::text,
          ('FINALIZADA'::character varying)::text
        ]
      )
    )
  )
) TABLESPACE pg_default;
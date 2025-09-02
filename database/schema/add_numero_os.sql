-- Script para adicionar campo numero_os na tabela relatorios
-- Este campo será usado para referência amigável das ocorrências

-- Adicionar o campo numero_os
ALTER TABLE public.relatorios 
ADD COLUMN numero_os VARCHAR(20) UNIQUE;

-- Criar índice para melhor performance nas buscas
CREATE INDEX idx_relatorios_numero_os ON public.relatorios(numero_os);

-- Criar sequência para gerar números automáticos
CREATE SEQUENCE IF NOT EXISTS public.relatorios_numero_os_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 999999
    CACHE 1;

-- Função para gerar número de OS automaticamente
CREATE OR REPLACE FUNCTION gerar_numero_os()
RETURNS TRIGGER AS $$
DECLARE
    proximo_numero INTEGER;
    numero_formatado VARCHAR(20);
    ano_atual VARCHAR(4);
BEGIN
    -- Obter o próximo número da sequência
    SELECT nextval('public.relatorios_numero_os_seq') INTO proximo_numero;
    
    -- Obter o ano atual
    SELECT EXTRACT(YEAR FROM CURRENT_DATE)::VARCHAR INTO ano_atual;
    
    -- Formatar o número: OS-2024-000001
    numero_formatado := 'OS-' || ano_atual || '-' || LPAD(proximo_numero::VARCHAR, 6, '0');
    
    -- Atribuir o número gerado
    NEW.numero_os := numero_formatado;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criar trigger para executar automaticamente
CREATE TRIGGER trigger_gerar_numero_os
    BEFORE INSERT ON public.relatorios
    FOR EACH ROW
    EXECUTE FUNCTION gerar_numero_os();

-- Comentário explicativo
COMMENT ON COLUMN public.relatorios.numero_os IS 'Número da Ordem de Serviço (formato: OS-YYYY-NNNNNN)';
COMMENT ON SEQUENCE public.relatorios_numero_os_seq IS 'Sequência para gerar números únicos de OS';


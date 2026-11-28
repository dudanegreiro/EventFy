ALTER TABLE public.servico
    ADD COLUMN localizacao varchar(200);

CREATE INDEX servico_localizacao_ix
    ON public.servico (localizacao)
    WHERE ativo;

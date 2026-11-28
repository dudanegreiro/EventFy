ALTER TABLE public.disponibilidade_servico
    ADD COLUMN id_reserva integer;

ALTER TABLE public.disponibilidade_servico
    ADD CONSTRAINT disponibilidade_reserva_fk
    FOREIGN KEY (id_reserva) REFERENCES public.reserva (id_reserva)
    ON UPDATE RESTRICT ON DELETE RESTRICT;

UPDATE public.disponibilidade_servico AS d
SET id_reserva = r.id_reserva
FROM public.reserva AS r
WHERE d.tipo = 'RESERVA'
  AND d.id_reserva IS NULL
  AND d.ativo
  AND r.ativo
  AND r.status IN ('SOLICITADA', 'EM_ANALISE', 'APROVADA', 'CONFIRMADA')
  AND d.id_servico = r.id_servico
  AND d.data_inicio = r.data_inicio
  AND d.data_fim = r.data_fim;

CREATE UNIQUE INDEX disponibilidade_reserva_ativa_uk
    ON public.disponibilidade_servico (id_reserva)
    WHERE ativo AND id_reserva IS NOT NULL;

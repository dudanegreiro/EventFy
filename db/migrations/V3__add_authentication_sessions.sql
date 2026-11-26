CREATE TABLE public.sessao_autenticacao (
    token_id uuid PRIMARY KEY,
    id_usuario integer NOT NULL,
    expira_em timestamptz NOT NULL,
    revogada_em timestamptz,
    criada_em timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT sessao_autenticacao_usuario_fk
        FOREIGN KEY (id_usuario) REFERENCES public.usuario (id_usuario)
        ON UPDATE RESTRICT ON DELETE RESTRICT
);

CREATE INDEX sessao_autenticacao_usuario_ix
    ON public.sessao_autenticacao (id_usuario);

CREATE INDEX sessao_autenticacao_expiracao_ix
    ON public.sessao_autenticacao (expira_em)
    WHERE revogada_em IS NULL;

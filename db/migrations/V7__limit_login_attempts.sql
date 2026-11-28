CREATE TABLE public.tentativa_login (
    email_digest bytea PRIMARY KEY,
    falhas integer NOT NULL CHECK (falhas > 0),
    janela_inicio timestamptz NOT NULL,
    bloqueado_ate timestamptz,
    atualizado_em timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT tentativa_login_digest_ck CHECK (octet_length(email_digest) = 32)
);

CREATE INDEX tentativa_login_atualizacao_ix
    ON public.tentativa_login (atualizado_em);

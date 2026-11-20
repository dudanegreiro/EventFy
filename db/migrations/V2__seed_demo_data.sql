INSERT INTO public.usuario (
    id_usuario, nome, email, senha_hash, tipo_usuario
) VALUES
    (
        1001,
        'Organizador de Demonstracao',
        'organizador.demo@eventfy.local',
        crypt('EventFyDemo123!', gen_salt('bf', 12)),
        'ORGANIZADOR'
    ),
    (
        1002,
        'Prestador de Demonstracao',
        'prestador.demo@eventfy.local',
        crypt('EventFyDemo123!', gen_salt('bf', 12)),
        'PRESTADOR'
    ),
    (
        1003,
        'Administrador de Demonstracao',
        'admin.demo@eventfy.local',
        crypt('EventFyDemo123!', gen_salt('bf', 12)),
        'ADMINISTRADOR'
    );

INSERT INTO public.evento (
    id_evento, id_organizador, nome, descricao, data_inicio, data_fim, local
) VALUES
    (
        1001,
        1001,
        'Confraternizacao de Demonstracao',
        'Evento futuro para demonstrar uma reserva aprovada.',
        '2027-07-17 18:00:00-03',
        '2027-07-17 23:00:00-03',
        'Palmas - TO'
    ),
    (
        1002,
        1001,
        'Encontro de Demonstracao',
        'Evento futuro para demonstrar uma solicitacao pendente.',
        '2027-09-10 18:00:00-03',
        '2027-09-10 22:00:00-03',
        'Palmas - TO'
    ),
    (
        1003,
        1001,
        'Evento Concluido de Demonstracao',
        'Evento passado para demonstrar avaliacao e historico.',
        '2026-03-20 18:00:00-03',
        '2026-03-20 23:00:00-03',
        'Palmas - TO'
    );

INSERT INTO public.servico (
    id_servico, id_prestador, nome, categoria, descricao, preco
) VALUES (
    1001,
    1002,
    'Buffet Regional de Demonstracao',
    'Alimentacao',
    'Servico ficticio usado apenas para desenvolvimento e demonstracao.',
    2500.00
);

INSERT INTO public.disponibilidade_servico (
    id_disponibilidade, id_servico, data_inicio, data_fim, tipo, motivo
) VALUES
    (
        1001,
        1001,
        '2027-01-01 00:00:00-03',
        '2028-01-01 00:00:00-03',
        'DISPONIVEL',
        'Janela ficticia de disponibilidade para demonstracao.'
    ),
    (
        1002,
        1001,
        '2027-07-17 18:00:00-03',
        '2027-07-17 23:00:00-03',
        'RESERVA',
        'Pre-bloqueio de demonstracao para reserva aprovada.'
    );

INSERT INTO public.arquivo (
    id_arquivo, id_servico, nome_original, url, tipo_mime, tamanho
) VALUES (
    1001,
    1001,
    'buffet-demonstracao.jpg',
    'https://example.invalid/eventfy/buffet-demonstracao.jpg',
    'image/jpeg',
    128000
);

INSERT INTO public.reserva (
    id_reserva, id_evento, id_servico, id_solicitante, status,
    data_inicio, data_fim, observacao
) VALUES
    (
        1001,
        1001,
        1001,
        1001,
        'APROVADA',
        '2027-07-17 18:00:00-03',
        '2027-07-17 23:00:00-03',
        'Reserva aprovada de demonstracao, aguardando confirmacao.'
    ),
    (
        1002,
        1002,
        1001,
        1001,
        'SOLICITADA',
        '2027-09-10 18:00:00-03',
        '2027-09-10 22:00:00-03',
        'Solicitacao pendente de demonstracao.'
    ),
    (
        1003,
        1003,
        1001,
        1001,
        'FINALIZADA',
        '2026-03-20 18:00:00-03',
        '2026-03-20 23:00:00-03',
        'Reserva concluida de demonstracao.'
    );

INSERT INTO public.historico_reserva (
    id_historico, id_reserva, id_usuario, status_anterior, status_novo,
    data_hora, observacao
) VALUES
    (
        1001, 1001, 1001, NULL, 'SOLICITADA',
        '2027-06-01 10:00:00-03', 'Solicitacao criada.'
    ),
    (
        1002, 1001, 1002, 'SOLICITADA', 'EM_ANALISE',
        '2027-06-01 11:00:00-03', 'Prestador iniciou a analise.'
    ),
    (
        1003, 1001, 1002, 'EM_ANALISE', 'APROVADA',
        '2027-06-01 12:00:00-03', 'Solicitacao aprovada.'
    ),
    (
        1004, 1002, 1001, NULL, 'SOLICITADA',
        '2027-06-02 10:00:00-03', 'Solicitacao criada.'
    ),
    (
        1005, 1003, 1001, NULL, 'SOLICITADA',
        '2026-02-01 10:00:00-03', 'Solicitacao criada.'
    ),
    (
        1006, 1003, 1002, 'SOLICITADA', 'EM_ANALISE',
        '2026-02-01 11:00:00-03', 'Prestador iniciou a analise.'
    ),
    (
        1007, 1003, 1002, 'EM_ANALISE', 'APROVADA',
        '2026-02-01 12:00:00-03', 'Solicitacao aprovada.'
    ),
    (
        1008, 1003, 1001, 'APROVADA', 'CONFIRMADA',
        '2026-02-02 10:00:00-03', 'Contratacao confirmada.'
    ),
    (
        1009, 1003, NULL, 'CONFIRMADA', 'FINALIZADA',
        '2026-03-21 00:00:00-03', 'Finalizacao automatica pelo sistema.'
    );

INSERT INTO public.avaliacao (
    id_avaliacao, id_reserva, id_avaliador, nota
) VALUES (1001, 1003, 1001, 5);

SELECT setval(
    pg_get_serial_sequence('public.usuario', 'id_usuario'),
    (SELECT max(id_usuario) FROM public.usuario),
    true
);
SELECT setval(
    pg_get_serial_sequence('public.evento', 'id_evento'),
    (SELECT max(id_evento) FROM public.evento),
    true
);
SELECT setval(
    pg_get_serial_sequence('public.servico', 'id_servico'),
    (SELECT max(id_servico) FROM public.servico),
    true
);
SELECT setval(
    pg_get_serial_sequence('public.disponibilidade_servico', 'id_disponibilidade'),
    (SELECT max(id_disponibilidade) FROM public.disponibilidade_servico),
    true
);
SELECT setval(
    pg_get_serial_sequence('public.arquivo', 'id_arquivo'),
    (SELECT max(id_arquivo) FROM public.arquivo),
    true
);
SELECT setval(
    pg_get_serial_sequence('public.reserva', 'id_reserva'),
    (SELECT max(id_reserva) FROM public.reserva),
    true
);
SELECT setval(
    pg_get_serial_sequence('public.historico_reserva', 'id_historico'),
    (SELECT max(id_historico) FROM public.historico_reserva),
    true
);
SELECT setval(
    pg_get_serial_sequence('public.avaliacao', 'id_avaliacao'),
    (SELECT max(id_avaliacao) FROM public.avaliacao),
    true
);

'use strict';

/*
 * Lista de reservas, análise pelo prestador e páginas de estado.
 *
 * reservas.html: o organizador vê as próprias reservas e o prestador vê as
 * solicitações recebidas. em-analise.html: o prestador inicia a análise e
 * aprova ou recusa. aprovada.html, confirmada.html e recusada.html: mostram a
 * reserva naquele estado; na aprovada, o organizador confirma a contratação.
 * O servidor decide o que cada papel pode fazer e em quais estados; a página
 * só oferece os botões coerentes com o estado e o papel e mostra a mensagem
 * de erro da API quando a operação é recusada.
 */
(function () {
  const api = window.EventFyApi;
  const dateTime = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
  const MIN_REFUSAL_LENGTH = 10;
  const STATUS_PAGES = {
    SOLICITADA: 'solicitada.html',
    EM_ANALISE: 'em-analise.html',
    APROVADA: 'aprovada.html',
    CONFIRMADA: 'confirmada.html',
    RECUSADA: 'recusada.html',
    CANCELADA: 'cancelada.html'
  };

  function byId(id) {
    return document.getElementById(id);
  }

  function showMessage(element, text) {
    element.textContent = text;
    element.hidden = false;
  }

  function formatPeriod(reservation) {
    return `${dateTime.format(new Date(reservation.data_inicio))} a ${dateTime.format(new Date(reservation.data_fim))}`;
  }

  function reservationIdFromUrl() {
    const value = new URLSearchParams(window.location.search).get('reserva');
    return /^[0-9]+$/.test(value || '') ? value : null;
  }

  /* Busca cada serviço uma única vez, mesmo que várias reservas o citem. */
  async function loadServices(ids) {
    const services = new Map();
    await Promise.all([...new Set(ids)].map(async id => {
      try {
        services.set(id, await api.apiFetch(`/api/servicos/${id}`, { auth: false }));
      } catch (error) {
        services.set(id, null);
      }
    }));
    return services;
  }

  /*
   * Nome do evento. Só o organizador pode listar eventos na API; para o
   * prestador, a reserva traz apenas o número do evento.
   */
  async function eventLabel(reservation, role) {
    if (role === 'ORGANIZADOR') {
      try {
        const events = await api.apiFetch('/api/eventos');
        const event = events.find(item => item.id_evento === reservation.id_evento);
        if (event) {
          return event.nome;
        }
      } catch (error) {
        // Cai no número do evento.
      }
    }
    return `Evento ${reservation.id_evento}`;
  }

  /* ---------- reservas.html: lista ---------- */

  function buildReservationItem(reservation, service, role, onError) {
    const item = document.createElement('li');
    item.className = 'history-entry';

    const title = document.createElement('h2');
    title.textContent = service ? service.nome : `Serviço ${reservation.id_servico}`;
    item.appendChild(title);

    const pill = document.createElement('span');
    pill.className = 'status-pill';
    pill.textContent = reservation.status;
    item.appendChild(pill);

    const period = document.createElement('p');
    period.textContent = `Período: ${formatPeriod(reservation)}`;
    item.appendChild(period);

    if (reservation.observacao) {
      const note = document.createElement('p');
      note.textContent = `Observação: ${reservation.observacao}`;
      item.appendChild(note);
    }

    const actions = document.createElement('div');
    actions.className = 'flow-actions';

    if (role === 'PRESTADOR' && reservation.status === 'SOLICITADA') {
      const start = document.createElement('button');
      start.type = 'button';
      start.className = 'button small';
      start.textContent = 'Iniciar análise';
      start.addEventListener('click', async () => {
        start.disabled = true;
        try {
          await api.apiFetch(`/api/reservas/${reservation.id_reserva}/analise`, { method: 'POST' });
          window.location.href = `em-analise.html?reserva=${encodeURIComponent(reservation.id_reserva)}`;
        } catch (failure) {
          onError(failure.message);
          start.disabled = false;
        }
      });
      actions.appendChild(start);
    } else {
      const open = document.createElement('a');
      open.className = 'button small secondary';
      open.href = `${STATUS_PAGES[reservation.status] || 'historico.html'}?reserva=${encodeURIComponent(reservation.id_reserva)}`;
      open.textContent = role === 'PRESTADOR' && reservation.status === 'EM_ANALISE' ? 'Analisar' : 'Abrir';
      actions.appendChild(open);
    }

    item.appendChild(actions);
    return item;
  }

  async function initializeReservationList() {
    const list = byId('reservation-list');
    if (!list) {
      return;
    }
    const loading = byId('list-loading');
    const error = byId('list-error');
    const empty = byId('list-empty');
    const session = api.requireSession();
    if (!session) {
      return;
    }
    if (session.role !== 'ORGANIZADOR' && session.role !== 'PRESTADOR') {
      loading.hidden = true;
      showMessage(error, 'Somente organizadores e prestadores têm reservas.');
      return;
    }

    const isProvider = session.role === 'PRESTADOR';
    byId('list-title').textContent = isProvider ? 'Solicitações recebidas' : 'Minhas reservas';
    byId('list-eyebrow').textContent = isProvider ? 'PRESTADOR' : 'ORGANIZADOR';
    byId('new-reservation').hidden = isProvider;

    try {
      const reservations = await api.apiFetch('/api/reservas');
      const services = await loadServices(reservations.map(item => item.id_servico));
      list.replaceChildren(...reservations.map(reservation => buildReservationItem(
        reservation,
        services.get(reservation.id_servico),
        session.role,
        text => showMessage(error, text)
      )));
      empty.hidden = reservations.length > 0;
    } catch (failure) {
      showMessage(error, failure.message);
    } finally {
      loading.hidden = true;
    }
  }

  /* ---------- em-analise.html: análise pelo prestador ---------- */

  const STATUS_TEXT = {
    SOLICITADA: 'A solicitação aguarda o início da análise pelo prestador.',
    EM_ANALISE: 'O prestador está analisando o pedido.',
    APROVADA: 'A solicitação foi aprovada e aguarda a confirmação do organizador.',
    RECUSADA: 'A solicitação foi recusada pelo prestador.',
    CONFIRMADA: 'A reserva foi confirmada.',
    CANCELADA: 'A reserva foi cancelada.',
    EXPIRADA: 'O prazo da reserva expirou sem resposta.',
    FINALIZADA: 'O serviço foi prestado e a reserva foi finalizada.'
  };

  async function initializeAnalysisPage() {
    const view = byId('analysis-view');
    if (!view) {
      return;
    }
    const loading = byId('analysis-loading');
    const problem = byId('analysis-error');

    function showProblem(text) {
      loading.hidden = true;
      view.hidden = true;
      byId('analysis-error-message').textContent = text;
      problem.hidden = false;
    }

    const reservationId = reservationIdFromUrl();
    if (!reservationId) {
      showProblem('Abra esta tela pela lista de reservas.');
      return;
    }
    const session = api.requireSession();
    if (!session) {
      return;
    }

    const form = byId('provider-decision-form');
    const reason = byId('refusal-reason-input');
    const startButton = byId('start-analysis');
    const flowError = byId('flow-error');
    const result = byId('decision-result');
    const isProvider = session.role === 'PRESTADOR';

    let eventName = '';

    function showReservation(reservation, service) {
      byId('summary-service').textContent = service ? service.nome : `Serviço ${reservation.id_servico}`;
      byId('summary-event').textContent = eventName;
      byId('summary-start').textContent = dateTime.format(new Date(reservation.data_inicio));
      byId('summary-end').textContent = dateTime.format(new Date(reservation.data_fim));
      byId('summary-observation').textContent = reservation.observacao || 'Nenhuma';
      byId('summary-status').textContent = reservation.status;
      byId('status-text').textContent = STATUS_TEXT[reservation.status] || '';
      byId('refusal-box').hidden = !(reservation.status === 'RECUSADA' && reservation.motivo_recusa);
      byId('refusal-reason').textContent = reservation.motivo_recusa || '';
      startButton.hidden = !(isProvider && reservation.status === 'SOLICITADA');
      form.hidden = !(isProvider && reservation.status === 'EM_ANALISE');
      const cancel = byId('cancel-link');
      cancel.href = `cancelar.html?reserva=${encodeURIComponent(reservation.id_reserva)}`;
      cancel.hidden = !api.canCancel(session.role, reservation);
      byId('history-link').href = `historico.html?reserva=${encodeURIComponent(reservation.id_reserva)}`;
    }

    let reservation;
    let service;
    try {
      reservation = await api.apiFetch(`/api/reservas/${reservationId}`);
      service = await api.apiFetch(`/api/servicos/${reservation.id_servico}`, { auth: false });
      eventName = await eventLabel(reservation, session.role);
    } catch (failure) {
      showProblem(failure.status === 404
        ? 'Esta reserva não existe ou não está ligada à sua conta.'
        : failure.message);
      return;
    }

    showReservation(reservation, service);
    byId('back-link').href = 'reservas.html';
    loading.hidden = true;
    view.hidden = false;

    async function refresh() {
      reservation = await api.apiFetch(`/api/reservas/${reservationId}`);
      showReservation(reservation, service);
    }

    startButton.addEventListener('click', async () => {
      flowError.hidden = true;
      startButton.disabled = true;
      try {
        await api.apiFetch(`/api/reservas/${reservationId}/analise`, { method: 'POST' });
        await refresh();
      } catch (failure) {
        showMessage(flowError, failure.message);
      } finally {
        startButton.disabled = false;
      }
    });

    form.querySelectorAll('[data-decision]').forEach(button => {
      button.addEventListener('click', () => {
        form.dataset.decision = button.dataset.decision;
      });
    });
    reason.addEventListener('input', () => reason.setCustomValidity(''));

    form.addEventListener('submit', async event => {
      event.preventDefault();
      flowError.hidden = true;
      result.hidden = true;
      const decision = form.dataset.decision;
      const justification = reason.value.trim();
      if (!decision) {
        showMessage(flowError, 'Escolha aprovar ou recusar a solicitação.');
        return;
      }
      if (decision === 'RECUSADA' && justification.length < MIN_REFUSAL_LENGTH) {
        reason.setCustomValidity(`A justificativa deve ter pelo menos ${MIN_REFUSAL_LENGTH} caracteres.`);
        reason.reportValidity();
        return;
      }

      const buttons = form.querySelectorAll('button');
      buttons.forEach(button => { button.disabled = true; });
      try {
        await api.apiFetch(`/api/reservas/${reservationId}/decisao`, {
          method: 'POST',
          body: {
            decisao: decision,
            motivo: decision === 'RECUSADA' ? justification : null
          }
        });
        await refresh();
        showMessage(result, decision === 'APROVADA'
          ? 'Solicitação aprovada. O organizador já pode confirmar a reserva.'
          : 'Solicitação recusada. O organizador verá a justificativa.');
      } catch (failure) {
        showMessage(flowError, failure.message);
      } finally {
        buttons.forEach(button => { button.disabled = false; });
      }
    });
  }

  /* ---------- aprovada.html, confirmada.html, recusada.html ---------- */

  async function initializeStatePage() {
    const view = byId('state-view');
    if (!view) {
      return;
    }
    const expected = document.body.dataset.expectedStatus;
    const loading = byId('state-loading');
    const problem = byId('state-error');

    function showProblem(text) {
      loading.hidden = true;
      view.hidden = true;
      byId('state-error-message').textContent = text;
      problem.hidden = false;
    }

    const reservationId = reservationIdFromUrl();
    if (!reservationId) {
      showProblem('Abra esta tela pela lista de reservas.');
      return;
    }
    const session = api.requireSession();
    if (!session) {
      return;
    }

    let reservation;
    let service;
    let eventName;
    try {
      reservation = await api.apiFetch(`/api/reservas/${reservationId}`);
      service = await api.apiFetch(`/api/servicos/${reservation.id_servico}`, { auth: false });
      eventName = await eventLabel(reservation, session.role);
    } catch (failure) {
      showProblem(failure.status === 404
        ? 'Esta reserva não existe ou não está ligada à sua conta.'
        : failure.message);
      return;
    }

    if (reservation.status !== expected) {
      const page = STATUS_PAGES[reservation.status];
      showProblem(`Esta reserva está no estado ${reservation.status}, e não em ${expected}. `
        + (page ? 'Abra-a pela lista de reservas para ver a tela do estado atual.' : ''));
      return;
    }

    byId('summary-service').textContent = service.nome;
    byId('summary-event').textContent = eventName;
    byId('summary-start').textContent = dateTime.format(new Date(reservation.data_inicio));
    byId('summary-end').textContent = dateTime.format(new Date(reservation.data_fim));
    byId('summary-observation').textContent = reservation.observacao || 'Nenhuma';
    byId('summary-status').textContent = reservation.status;
    byId('history-link').href = `historico.html?reserva=${encodeURIComponent(reservation.id_reserva)}`;

    const refusalBox = byId('refusal-box');
    if (refusalBox) {
      byId('refusal-reason').textContent = reservation.motivo_recusa
        || 'O fornecedor não informou um motivo.';
    }

    const cancel = byId('cancel-link');
    if (cancel) {
      cancel.href = `cancelar.html?reserva=${encodeURIComponent(reservation.id_reserva)}`;
      cancel.hidden = !api.canCancel(session.role, reservation);
    }

    // Na tela de cancelamento, quem cancelou e a justificativa vêm do histórico.
    if (byId('cancellation-box')) {
      const summaryText = byId('cancellation-summary');
      try {
        const entries = await api.apiFetch(`/api/reservas/${reservationId}/historico`);
        const entry = entries.filter(item => item.status_novo === 'CANCELADA').pop();
        summaryText.textContent = entry
          ? `Cancelada por ${entry.autor_nome}${entry.autor_perfil ? ` (${api.roleLabel(entry.autor_perfil)})` : ''}. `
            + `Justificativa: ${entry.motivo || 'não informada'}.`
          : 'O registro do cancelamento não foi encontrado no histórico.';
      } catch (failure) {
        summaryText.textContent = failure.message;
      }
    }

    const confirm = byId('confirm-button');
    if (confirm) {
      confirm.hidden = session.role !== 'ORGANIZADOR';
      confirm.addEventListener('click', async () => {
        const flowError = byId('flow-error');
        flowError.hidden = true;
        confirm.disabled = true;
        confirm.textContent = 'Confirmando...';
        try {
          await api.apiFetch(`/api/reservas/${reservationId}/confirmacao`, { method: 'POST' });
          window.location.href = `confirmada.html?reserva=${encodeURIComponent(reservationId)}`;
        } catch (failure) {
          showMessage(flowError, failure.message);
          confirm.disabled = false;
          confirm.textContent = 'Confirmar reserva';
        }
      });
    }

    loading.hidden = true;
    view.hidden = false;
  }

  /* ---------- cancelar.html: cancelamento justificado ---------- */

  async function initializeCancellationPage() {
    const form = byId('cancellation-form');
    if (!form) {
      return;
    }
    const loading = byId('cancellation-loading');
    const error = byId('cancellation-error');
    const reason = byId('cancellation-reason');
    const submit = byId('cancellation-submit');

    function showProblem(text) {
      loading.hidden = true;
      form.hidden = true;
      showMessage(error, text);
    }

    const reservationId = reservationIdFromUrl();
    if (!reservationId) {
      showProblem('Abra esta tela pela reserva que deseja cancelar.');
      return;
    }
    const session = api.requireSession(['ORGANIZADOR', 'PRESTADOR']);
    if (!session) {
      return;
    }
    if (session.forbidden) {
      showProblem('Somente organizadores e prestadores podem cancelar reservas.');
      return;
    }
    byId('history-link').href = `historico.html?reserva=${encodeURIComponent(reservationId)}`;

    let reservation;
    try {
      reservation = await api.apiFetch(`/api/reservas/${reservationId}`);
      const service = await api.apiFetch(`/api/servicos/${reservation.id_servico}`, { auth: false });
      byId('cancellation-context').textContent =
        `${service.nome} · ${reservation.status} · ${api.roleLabel(session.role)}`;
    } catch (failure) {
      showProblem(failure.status === 404
        ? 'Esta reserva não existe ou não está ligada à sua conta.'
        : failure.message);
      return;
    }

    if (!api.canCancel(session.role, reservation)) {
      showProblem('Este papel não pode cancelar a reserva no estado atual, ou o período já começou.');
      return;
    }

    loading.hidden = true;
    form.hidden = false;
    reason.addEventListener('input', () => reason.setCustomValidity(''));
    form.addEventListener('submit', async event => {
      event.preventDefault();
      error.hidden = true;
      const justification = reason.value.trim();
      if (!justification) {
        reason.setCustomValidity('Informe a justificativa para cancelar a reserva.');
        reason.reportValidity();
        return;
      }
      submit.disabled = true;
      submit.textContent = 'Cancelando...';
      try {
        await api.apiFetch(`/api/reservas/${reservationId}/cancelamento`, {
          method: 'POST',
          body: { motivo: justification }
        });
        window.location.href = `cancelada.html?reserva=${encodeURIComponent(reservationId)}`;
      } catch (failure) {
        showMessage(error, failure.message);
        submit.disabled = false;
        submit.textContent = 'Confirmar cancelamento';
      }
    });
  }

  /* ---------- historico.html: trilha de auditoria ---------- */

  function buildHistoryEntry(entry) {
    const item = document.createElement('li');
    item.className = 'history-entry';

    const title = document.createElement('h2');
    title.textContent = entry.status_anterior
      ? `${entry.status_anterior} → ${entry.status_novo}`
      : `Início → ${entry.status_novo}`;
    item.appendChild(title);

    const details = document.createElement('p');
    const profile = entry.autor_perfil ? api.roleLabel(entry.autor_perfil) : null;
    details.textContent = `${dateTime.format(new Date(entry.data_hora))} · Responsável: ${entry.autor_nome}`
      + (profile ? ` (${profile})` : '');
    item.appendChild(details);

    if (entry.motivo) {
      const reason = document.createElement('p');
      reason.textContent = `Justificativa: ${entry.motivo}`;
      item.appendChild(reason);
    }
    if (entry.observacao) {
      const note = document.createElement('p');
      note.textContent = `Observação: ${entry.observacao}`;
      item.appendChild(note);
    }
    return item;
  }

  async function initializeHistoryPage() {
    const view = byId('history-view');
    if (!view) {
      return;
    }
    const loading = byId('history-loading');
    const problem = byId('history-error');

    function showProblem(text) {
      loading.hidden = true;
      view.hidden = true;
      byId('history-error-message').textContent = text;
      problem.hidden = false;
    }

    const reservationId = reservationIdFromUrl();
    if (!reservationId) {
      showProblem('Abra o histórico pela lista de reservas.');
      return;
    }
    const session = api.requireSession();
    if (!session) {
      return;
    }

    try {
      const [reservation, entries] = await Promise.all([
        api.apiFetch(`/api/reservas/${reservationId}`),
        api.apiFetch(`/api/reservas/${reservationId}/historico`)
      ]);
      const service = await api.apiFetch(`/api/servicos/${reservation.id_servico}`, { auth: false });

      byId('history-context').textContent = `${service.nome} · Estado atual: ${reservation.status}`;
      byId('history-list').replaceChildren(...entries.map(buildHistoryEntry));
      const page = STATUS_PAGES[reservation.status];
      byId('history-back').href = page
        ? `${page}?reserva=${encodeURIComponent(reservation.id_reserva)}`
        : 'reservas.html';
      loading.hidden = true;
      view.hidden = false;
    } catch (failure) {
      showProblem(failure.status === 404
        ? 'Esta reserva não existe ou não está ligada à sua conta.'
        : failure.message);
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initializeReservationList();
    initializeAnalysisPage();
    initializeStatePage();
    initializeCancellationPage();
    initializeHistoryPage();
  });
})();

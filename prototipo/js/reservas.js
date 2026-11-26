'use strict';

/*
 * Lista de reservas e análise pelo prestador.
 *
 * reservas.html: o organizador vê as próprias reservas e o prestador vê as
 * solicitações recebidas. em-analise.html: o prestador inicia a análise e
 * aprova ou recusa. O servidor decide o que cada papel pode fazer e em quais
 * estados; a página só oferece os botões coerentes com o estado e o papel e
 * mostra a mensagem de erro da API quando a operação é recusada.
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

    function showReservation(reservation, service) {
      byId('summary-service').textContent = service ? service.nome : `Serviço ${reservation.id_servico}`;
      byId('summary-event').textContent = `Evento ${reservation.id_evento}`;
      byId('summary-start').textContent = dateTime.format(new Date(reservation.data_inicio));
      byId('summary-end').textContent = dateTime.format(new Date(reservation.data_fim));
      byId('summary-observation').textContent = reservation.observacao || 'Nenhuma';
      byId('summary-status').textContent = reservation.status;
      byId('status-text').textContent = STATUS_TEXT[reservation.status] || '';
      byId('refusal-box').hidden = !(reservation.status === 'RECUSADA' && reservation.motivo_recusa);
      byId('refusal-reason').textContent = reservation.motivo_recusa || '';
      startButton.hidden = !(isProvider && reservation.status === 'SOLICITADA');
      form.hidden = !(isProvider && reservation.status === 'EM_ANALISE');
      byId('history-link').href = `historico.html?reserva=${encodeURIComponent(reservation.id_reserva)}`;
    }

    let reservation;
    let service;
    try {
      reservation = await api.apiFetch(`/api/reservas/${reservationId}`);
      service = await api.apiFetch(`/api/servicos/${reservation.id_servico}`, { auth: false });
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

  document.addEventListener('DOMContentLoaded', () => {
    initializeReservationList();
    initializeAnalysisPage();
  });
})();

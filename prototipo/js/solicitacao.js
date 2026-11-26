'use strict';

/*
 * Solicitação de reserva pelo organizador, com a criação de evento.
 *
 * reserva.html: escolhe (ou cria) um evento, informa o período e envia a
 * solicitação. solicitada.html: mostra a reserva gravada, lida da API.
 * Todas as regras (papel, período do evento, disponibilidade, conflito de
 * agenda) são decididas pelo servidor; aqui só se validam os formatos para
 * dar retorno rápido, e as mensagens de erro da API são mostradas como vêm.
 */
(function () {
  const api = window.EventFyApi;
  const NEW_EVENT = 'novo';
  const dateTime = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' });

  function byId(id) {
    return document.getElementById(id);
  }

  function showMessage(element, text) {
    element.textContent = text;
    element.hidden = false;
  }

  /* Valor para um campo datetime-local (horário local, sem fuso). */
  function toLocalInput(date) {
    const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
    return local.toISOString().slice(0, 16);
  }

  /* Texto do campo datetime-local para ISO com fuso, como a API exige. */
  function toIso(localValue) {
    return new Date(localValue).toISOString();
  }

  function serviceIdFromUrl() {
    const value = new URLSearchParams(window.location.search).get('servico');
    return /^[0-9]+$/.test(value || '') ? value : null;
  }

  function reservationIdFromUrl() {
    const value = new URLSearchParams(window.location.search).get('reserva');
    return /^[0-9]+$/.test(value || '') ? value : null;
  }

  /* ---------- reserva.html: formulário de solicitação ---------- */

  async function initializeRequestForm() {
    const form = byId('request-form');
    if (!form) {
      return;
    }

    const error = byId('request-error');
    const serviceId = serviceIdFromUrl();
    if (!serviceId) {
      showMessage(error, 'Selecione um serviço válido no catálogo antes de continuar.');
      return;
    }
    const session = api.requireSession(['ORGANIZADOR']);
    if (!session) {
      return;
    }
    if (session.forbidden) {
      showMessage(error, 'Somente organizadores podem solicitar reservas. Saia e entre com uma conta de organizador.');
      return;
    }

    const select = byId('event');
    const newEventFields = byId('new-event-fields');
    const start = byId('starts-at');
    const end = byId('ends-at');
    const submit = byId('request-submit');
    const events = new Map();
    let createdEvent = false;
    let periodEdited = false;

    byId('service-back').href = `servico.html?servico=${encodeURIComponent(serviceId)}`;

    let service;
    try {
      service = await api.apiFetch(`/api/servicos/${serviceId}`, { auth: false });
      const eventList = await api.apiFetch('/api/eventos');
      eventList
        .sort((a, b) => new Date(a.data_inicio) - new Date(b.data_inicio))
        .forEach(addEventOption);
    } catch (failure) {
      showMessage(error, failure.status === 404
        ? 'Este serviço não existe ou foi desativado. Volte ao catálogo e escolha outro.'
        : failure.message);
      return;
    }

    byId('selected-service').textContent = `Serviço selecionado: ${service.nome}`;
    const windows = service.disponibilidades.slice(0, 3)
      .map(period => `${dateTime.format(new Date(period.data_inicio))} a ${dateTime.format(new Date(period.data_fim))}`);
    byId('availability-hint').textContent = windows.length > 0
      ? `Períodos disponíveis: ${windows.join(' · ')}.`
      : 'Este serviço não tem períodos disponíveis publicados.';

    const newOption = document.createElement('option');
    newOption.value = NEW_EVENT;
    newOption.textContent = '➕ Criar um novo evento';
    select.appendChild(newOption);
    form.hidden = false;

    function addEventOption(event) {
      events.set(String(event.id_evento), event);
      const option = document.createElement('option');
      option.value = String(event.id_evento);
      const over = new Date(event.data_fim) <= new Date();
      option.disabled = over;
      option.textContent = `${event.nome} · ${dateTime.format(new Date(event.data_inicio))}${over ? ' (encerrado)' : ''}`;
      select.appendChild(option);
      return option;
    }

    /* Limites do período da reserva: o evento escolhido ou, se for novo, o que está sendo digitado. */
    function eventBounds() {
      if (select.value === NEW_EVENT) {
        const from = byId('new-event-start').value;
        const to = byId('new-event-end').value;
        return from && to ? { from, to } : null;
      }
      const event = events.get(select.value);
      return event
        ? { from: toLocalInput(new Date(event.data_inicio)), to: toLocalInput(new Date(event.data_fim)) }
        : null;
    }

    function applyBounds() {
      const now = toLocalInput(new Date());
      const bounds = eventBounds();
      start.min = bounds ? (bounds.from > now ? bounds.from : now) : now;
      end.min = start.min;
      start.max = bounds ? bounds.to : '';
      end.max = bounds ? bounds.to : '';
      if (bounds && !periodEdited) {
        start.value = bounds.from > now ? bounds.from : now;
        end.value = bounds.to;
      }
    }

    select.addEventListener('change', () => {
      newEventFields.hidden = select.value !== NEW_EVENT;
      periodEdited = false;
      applyBounds();
    });
    ['new-event-start', 'new-event-end'].forEach(id => byId(id).addEventListener('input', applyBounds));
    [start, end].forEach(input => input.addEventListener('input', () => {
      periodEdited = true;
      input.setCustomValidity('');
    }));

    function validate() {
      if (select.value === NEW_EVENT) {
        const from = byId('new-event-start').value;
        const to = byId('new-event-end').value;
        if (!byId('new-event-name').value.trim() || !byId('new-event-location').value.trim() || !from || !to) {
          return 'Informe nome, local, início e fim do novo evento.';
        }
        if (from >= to) {
          return 'O fim do evento deve ser posterior ao início.';
        }
      }
      if (!select.value) {
        return 'Selecione um evento ou crie um novo.';
      }
      if (start.value >= end.value) {
        end.setCustomValidity('O fim do período deve ser posterior ao início.');
        end.reportValidity();
        return 'O fim do período deve ser posterior ao início.';
      }
      const bounds = eventBounds();
      if (bounds && (start.value < bounds.from || end.value > bounds.to)) {
        return 'O período solicitado deve estar dentro do período do evento.';
      }
      return null;
    }

    /* Cria o evento novo (uma única vez) e passa o formulário a usá-lo. */
    async function resolveEventId() {
      if (select.value !== NEW_EVENT) {
        return Number(select.value);
      }
      const created = await api.apiFetch('/api/eventos', {
        method: 'POST',
        body: {
          nome: byId('new-event-name').value.trim(),
          descricao: byId('new-event-description').value.trim() || null,
          local: byId('new-event-location').value.trim(),
          data_inicio: toIso(byId('new-event-start').value),
          data_fim: toIso(byId('new-event-end').value)
        }
      });
      // Se a reserva falhar em seguida, uma nova tentativa reaproveita este evento.
      const option = addEventOption(created);
      select.insertBefore(option, newOption);
      select.value = String(created.id_evento);
      newEventFields.hidden = true;
      createdEvent = true;
      return created.id_evento;
    }

    form.addEventListener('submit', async event => {
      event.preventDefault();
      error.hidden = true;
      const problem = validate();
      if (problem) {
        showMessage(error, problem);
        return;
      }

      submit.disabled = true;
      submit.textContent = 'Enviando...';
      try {
        const eventId = await resolveEventId();
        const reservation = await api.apiFetch('/api/reservas', {
          method: 'POST',
          body: {
            id_evento: eventId,
            id_servico: Number(serviceId),
            data_inicio: toIso(start.value),
            data_fim: toIso(end.value),
            observacao: byId('observation').value.trim() || null
          }
        });
        window.location.href = `solicitada.html?reserva=${encodeURIComponent(reservation.id_reserva)}`;
      } catch (failure) {
        const prefix = createdEvent ? 'O evento foi criado, mas a solicitação não foi enviada. ' : '';
        showMessage(error, prefix + failure.message);
        submit.disabled = false;
        submit.textContent = 'Enviar solicitação';
      }
    });
  }

  /* ---------- solicitada.html: reserva gravada ---------- */

  async function initializeRequestSummary() {
    const summary = byId('request-summary');
    const invalid = byId('invalid-request');
    if (!summary || !invalid) {
      return;
    }

    function showInvalid(text) {
      byId('summary-loading').hidden = true;
      byId('request-error-message').textContent = text;
      invalid.hidden = false;
      summary.hidden = true;
    }

    const reservationId = reservationIdFromUrl();
    if (!reservationId) {
      showInvalid('Volte ao catálogo, selecione um serviço e envie uma solicitação.');
      return;
    }
    const session = api.requireSession(['ORGANIZADOR']);
    if (!session) {
      return;
    }
    if (session.forbidden) {
      showInvalid('Somente o organizador da reserva pode ver esta página.');
      return;
    }

    try {
      const reservation = await api.apiFetch(`/api/reservas/${reservationId}`);
      const [service, events] = await Promise.all([
        api.apiFetch(`/api/servicos/${reservation.id_servico}`, { auth: false }),
        api.apiFetch('/api/eventos')
      ]);
      const event = events.find(item => item.id_evento === reservation.id_evento);

      byId('summary-service').textContent = service.nome;
      byId('summary-event').textContent = event ? event.nome : `Evento ${reservation.id_evento}`;
      byId('summary-start').textContent = dateTime.format(new Date(reservation.data_inicio));
      byId('summary-end').textContent = dateTime.format(new Date(reservation.data_fim));
      byId('summary-observation').textContent = reservation.observacao || 'Nenhuma';
      byId('summary-status').textContent = reservation.status;
      byId('history-link').href = `historico.html?reserva=${encodeURIComponent(reservation.id_reserva)}`;
      byId('summary-loading').hidden = true;
      summary.hidden = false;
      invalid.hidden = true;
    } catch (failure) {
      showInvalid(failure.status === 404
        ? 'Esta reserva não existe ou não pertence à sua conta.'
        : failure.message);
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initializeRequestForm();
    initializeRequestSummary();
  });
})();

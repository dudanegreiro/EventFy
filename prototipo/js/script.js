const services = {
  'som-iluminacao': {
    name: 'Som e iluminação profissional',
    category: 'Som e iluminação',
    description: 'Estrutura completa de som e iluminação para eventos de médio e grande porte, com montagem e suporte durante o período contratado.',
    price: 'R$ 1.800',
    provider: 'EventFy Serviços',
    image: '🔊'
  },
  'espaco-eventos': {
    name: 'Espaço para eventos',
    category: 'Espaço',
    description: 'Ambiente para confraternizações, festas e eventos corporativos.',
    price: 'R$ 2.500',
    provider: 'EventFy Espaços',
    image: '🏛️'
  },
  'equipe-apoio': {
    name: 'Equipe de apoio',
    category: 'Equipe',
    description: 'Profissionais para apoio operacional durante o evento.',
    price: 'R$ 900',
    provider: 'EventFy Equipe',
    image: '👥'
  }
};

const events = {
  aniversario: 'Festa de aniversário',
  casamento: 'Casamento',
  confraternizacao: 'Confraternização'
};

const validStatuses = [
  'SOLICITADA',
  'EM_ANALISE',
  'APROVADA',
  'RECUSADA',
  'CONFIRMADA',
  'CANCELADA',
  'EXPIRADA',
  'FINALIZADA'
];

const allowedTransitions = {
  SOLICITADA: ['EM_ANALISE', 'CANCELADA'],
  EM_ANALISE: ['APROVADA', 'RECUSADA', 'CANCELADA'],
  APROVADA: ['CONFIRMADA', 'CANCELADA'],
  CONFIRMADA: ['CANCELADA']
};

const transitionActors = {
  'SOLICITADA>EM_ANALISE': ['Prestador'],
  'EM_ANALISE>APROVADA': ['Prestador'],
  'EM_ANALISE>RECUSADA': ['Prestador'],
  'SOLICITADA>CANCELADA': ['Organizador'],
  'EM_ANALISE>CANCELADA': ['Organizador'],
  'APROVADA>CANCELADA': ['Organizador'],
  'APROVADA>CONFIRMADA': ['Organizador'],
  'CONFIRMADA>CANCELADA': ['Organizador', 'Prestador']
};

const cancellationStates = {
  organizador: ['SOLICITADA', 'EM_ANALISE', 'APROVADA', 'CONFIRMADA'],
  prestador: ['CONFIRMADA']
};

function selectedService() {
  const serviceId = new URLSearchParams(window.location.search).get('servico');
  return serviceId && Object.prototype.hasOwnProperty.call(services, serviceId)
    ? services[serviceId]
    : null;
}

function selectedEvent(eventId) {
  return eventId && Object.prototype.hasOwnProperty.call(events, eventId)
    ? events[eventId]
    : null;
}

function readHistory(parameters) {
  const serializedHistory = parameters.get('historico');
  if (!serializedHistory) {
    return { entries: null, error: 'O histórico não foi informado. Inicie a navegação pela solicitação.' };
  }

  let entries;
  try {
    entries = JSON.parse(serializedHistory);
  } catch (error) {
    return { entries: null, error: 'Os dados do histórico estão inválidos.' };
  }

  if (!Array.isArray(entries) || entries.length === 0) {
    return { entries: null, error: 'Os dados do histórico estão inválidos.' };
  }

  const validEntries = entries.every(entry => {
    return entry
      && typeof entry === 'object'
      && (entry.previousStatus === '' || validStatuses.includes(entry.previousStatus))
      && validStatuses.includes(entry.newStatus)
      && typeof entry.actor === 'string'
      && entry.actor.length > 0
      && typeof entry.changedAt === 'string'
      && Number.isFinite(Date.parse(entry.changedAt))
      && typeof entry.justification === 'string'
      && (entry.newStatus !== 'RECUSADA' && entry.newStatus !== 'CANCELADA'
        || entry.justification.trim().length > 0);
  });
  const validSequence = validEntries && entries.every((entry, index) => {
    const expectedPreviousStatus = index === 0 ? '' : entries[index - 1].newStatus;
    if (entry.previousStatus !== expectedPreviousStatus) {
      return false;
    }
    if (index === 0) {
      return entry.actor === 'Organizador';
    }
    const transition = `${entry.previousStatus}>${entry.newStatus}`;
    return allowedTransitions[entry.previousStatus]
      && allowedTransitions[entry.previousStatus].includes(entry.newStatus)
      && transitionActors[transition]
      && transitionActors[transition].includes(entry.actor);
  });

  if (!validSequence || entries[0].previousStatus !== '' || entries[0].newStatus !== 'SOLICITADA') {
    return { entries: null, error: 'Os dados do histórico estão inválidos.' };
  }

  return { entries, error: null };
}

function appendTransition(parameters, nextStatus, actor, justification) {
  const history = readHistory(parameters);
  if (!history.entries) {
    return history.error;
  }

  const previousStatus = history.entries[history.entries.length - 1].newStatus;
  if (parameters.get('status') !== previousStatus) {
    return 'O estado atual não corresponde ao último registro do histórico.';
  }
  if (!allowedTransitions[previousStatus] || !allowedTransitions[previousStatus].includes(nextStatus)) {
    return `A transição de ${previousStatus} para ${nextStatus} não é permitida.`;
  }
  const transition = `${previousStatus}>${nextStatus}`;
  if (!transitionActors[transition] || !transitionActors[transition].includes(actor)) {
    return 'O papel indicado não pode realizar esta transição.';
  }

  history.entries.push({
    previousStatus,
    newStatus: nextStatus,
    changedAt: new Date().toISOString(),
    actor,
    justification
  });
  parameters.set('status', nextStatus);
  parameters.set('historico', JSON.stringify(history.entries));
  return null;
}

function validateStateContext(parameters, expectedStatus) {
  const serviceId = parameters.get('servico');
  const service = serviceId && Object.prototype.hasOwnProperty.call(services, serviceId)
    ? services[serviceId]
    : null;
  const eventName = selectedEvent(parameters.get('evento'));
  const start = parameters.get('inicio');
  const end = parameters.get('fim');
  if (!service || !eventName || !start || !end
      || !Number.isFinite(Date.parse(start)) || !Number.isFinite(Date.parse(end))
      || Date.parse(start) >= Date.parse(end)) {
    return 'Os dados da solicitação estão ausentes ou inválidos.';
  }

  const history = readHistory(parameters);
  if (!history.entries) {
    return history.error;
  }
  if (parameters.get('status') !== expectedStatus
      || history.entries[history.entries.length - 1].newStatus !== expectedStatus) {
    return `A solicitação não está no estado ${expectedStatus}.`;
  }
  return null;
}

function showFlowError(message, errorId) {
  const error = document.getElementById(errorId || 'flow-error');
  if (!error) {
    console.error(message);
    return;
  }
  error.textContent = message;
  error.hidden = false;
}

function filterCards() {
  const search = document.getElementById('search');
  const category = document.getElementById('category');
  const cards = document.querySelectorAll('.card');
  const emptyState = document.getElementById('empty-state');

  if (!search || !category || !emptyState) {
    return;
  }

  const query = search.value.trim().toLocaleLowerCase('pt-BR');
  let visibleCount = 0;

  cards.forEach(card => {
    const nameMatches = card.dataset.name.toLocaleLowerCase('pt-BR').includes(query);
    const categoryMatches = !category.value || card.dataset.category === category.value;
    card.hidden = !(nameMatches && categoryMatches);
    if (!card.hidden) {
      visibleCount += 1;
    }
  });

  emptyState.hidden = visibleCount > 0;
}

function initializeCatalog() {
  const search = document.getElementById('search');
  const category = document.getElementById('category');

  if (!search || !category) {
    return;
  }

  search.addEventListener('input', filterCards);
  category.addEventListener('change', filterCards);
  filterCards();
}

function initializeServiceDetails() {
  const detail = document.getElementById('service-detail');
  const notFound = document.getElementById('service-not-found');
  if (!detail || !notFound) {
    return;
  }

  const service = selectedService();
  if (!service) {
    notFound.hidden = false;
    return;
  }

  document.getElementById('service-image').textContent = service.image;
  document.getElementById('service-category').textContent = service.category;
  document.getElementById('service-name').textContent = service.name;
  document.getElementById('service-description').textContent = service.description;
  document.getElementById('service-price').textContent = service.price;
  document.getElementById('service-provider').textContent = service.provider;
  const serviceId = new URLSearchParams(window.location.search).get('servico');
  document.getElementById('request-link').href = `reserva.html?servico=${encodeURIComponent(serviceId)}`;
  detail.hidden = false;
  notFound.hidden = true;
}

function localDateTimeValue(date) {
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return localDate.toISOString().slice(0, 16);
}

function initializeRequestForm() {
  const form = document.getElementById('request-form');
  const error = document.getElementById('request-error');
  if (!form || !error) {
    return;
  }

  const service = selectedService();
  if (!service) {
    error.hidden = false;
    return;
  }

  const serviceLabel = document.getElementById('selected-service');
  const serviceBack = document.getElementById('service-back');
  const serviceId = new URLSearchParams(window.location.search).get('servico');
  const start = document.getElementById('starts-at');
  const end = document.getElementById('ends-at');
  const currentLocalTime = localDateTimeValue(new Date());
  serviceLabel.textContent = `Serviço selecionado: ${service.name}`;
  serviceBack.href = `servico.html?servico=${encodeURIComponent(serviceId)}`;
  start.min = currentLocalTime;
  end.min = currentLocalTime;
  form.hidden = false;

  start.addEventListener('change', () => {
    end.min = start.value || currentLocalTime;
    end.setCustomValidity('');
  });
  end.addEventListener('input', () => end.setCustomValidity(''));

  form.addEventListener('submit', event => {
    event.preventDefault();
    if (start.value >= end.value) {
      end.setCustomValidity('O fim do período deve ser posterior ao início.');
      end.reportValidity();
      return;
    }

    const parameters = new URLSearchParams({
      servico: new URLSearchParams(window.location.search).get('servico'),
      evento: document.getElementById('event').value,
      inicio: start.value,
      fim: end.value,
      observacao: document.getElementById('observation').value.trim()
    });
    const initialHistory = [{
      previousStatus: '',
      newStatus: 'SOLICITADA',
      changedAt: new Date().toISOString(),
      actor: 'Organizador',
      justification: ''
    }];
    parameters.set('status', 'SOLICITADA');
    parameters.set('historico', JSON.stringify(initialHistory));
    window.location.href = `solicitada.html?${parameters.toString()}`;
  });
}

function formatDateTime(value) {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(new Date(value));
}

function initializeRequestSummary() {
  const summary = document.getElementById('request-summary');
  const invalidRequest = document.getElementById('invalid-request');
  if (!summary || !invalidRequest) {
    return;
  }

  const parameters = new URLSearchParams(window.location.search);
  const validationError = validateStateContext(parameters, 'SOLICITADA');
  const service = selectedService();
  const eventName = selectedEvent(parameters.get('evento'));
  const start = parameters.get('inicio');
  const end = parameters.get('fim');
  const status = parameters.get('status');
  const history = readHistory(parameters);
  if (validationError || !service || !eventName || !start || !end) {
    document.getElementById('request-error-message').textContent =
      validationError || 'Os dados da solicitação estão ausentes ou inválidos.';
    invalidRequest.hidden = false;
    return;
  }

  document.getElementById('summary-service').textContent = service.name;
  document.getElementById('summary-event').textContent = eventName;
  document.getElementById('summary-start').textContent = formatDateTime(start);
  document.getElementById('summary-end').textContent = formatDateTime(end);
  document.getElementById('summary-observation').textContent = parameters.get('observacao') || 'Nenhuma';
  document.getElementById('summary-status').textContent = status || 'SOLICITADA';
  summary.hidden = false;
  invalidRequest.hidden = true;

  const actions = document.getElementById('request-actions');
  if (actions && status === 'SOLICITADA' && history.entries
      && history.entries[history.entries.length - 1].newStatus === status) {
    actions.hidden = false;
  } else if (actions) {
    showFlowError(history.error || 'A solicitação não está no estado SOLICITADA.', 'flow-error');
  }
}

function initializeTransitionLinks() {
  document.querySelectorAll('[data-transition]').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      const parameters = new URLSearchParams(window.location.search);
      const error = appendTransition(
        parameters,
        link.dataset.transition,
        link.dataset.actor,
        link.dataset.justification || ''
      );
      if (error) {
        showFlowError(error);
        return;
      }

      const target = new URL(link.getAttribute('href'), window.location.href);
      target.search = parameters.toString();
      window.location.href = target.href;
    });
  });
}

function initializeProviderDecisionForm() {
  const form = document.getElementById('provider-decision-form');
  if (!form) {
    return;
  }

  const parameters = new URLSearchParams(window.location.search);
  const history = readHistory(parameters);
  if (validateStateContext(parameters, 'EM_ANALISE') || !history.entries) {
    return;
  }

  form.hidden = false;
  const reason = document.getElementById('refusal-reason-input');
  reason.addEventListener('input', () => reason.setCustomValidity(''));
  form.querySelectorAll('[data-decision]').forEach(button => {
    button.addEventListener('click', () => {
      form.dataset.decision = button.dataset.decision;
    });
  });

  form.addEventListener('submit', event => {
    event.preventDefault();
    const decision = form.dataset.decision;
    const justification = reason.value.trim();
    if (!decision) {
      showFlowError('Escolha aprovar ou recusar a solicitação.');
      return;
    }
    if (decision === 'RECUSADA' && !justification) {
      reason.setCustomValidity('Informe a justificativa para recusar a solicitação.');
      reason.reportValidity();
      return;
    }

    const nextParameters = new URLSearchParams(window.location.search);
    const transitionError = appendTransition(
      nextParameters,
      decision,
      'Prestador',
      decision === 'RECUSADA' ? justification : ''
    );
    if (transitionError) {
      showFlowError(transitionError);
      return;
    }
    if (decision === 'RECUSADA') {
      nextParameters.set('justificativa', justification);
    }

    const targetPage = decision === 'APROVADA' ? 'aprovada.html' : 'recusada.html';
    window.location.href = `${targetPage}?${nextParameters.toString()}`;
  });
}

function initializeHistoryPage() {
  const historyView = document.getElementById('history-view');
  if (!historyView) {
    return;
  }

  const parameters = new URLSearchParams(window.location.search);
  const history = readHistory(parameters);
  const service = selectedService();
  const eventName = selectedEvent(parameters.get('evento'));
  const status = parameters.get('status');
  const validationError = validateStateContext(parameters, status);

  if (validationError || !history.entries || !service || !eventName) {
    document.getElementById('history-error-message').textContent =
      validationError || history.error || 'Os dados da solicitação não correspondem ao histórico.';
    return;
  }

  document.getElementById('history-context').textContent =
    `${service.name} · ${eventName} · Estado atual: ${status}`;
  const list = document.getElementById('history-list');
  history.entries.forEach(entry => {
    const item = document.createElement('li');
    item.className = 'history-entry';

    const title = document.createElement('h2');
    title.textContent = entry.previousStatus
      ? `${entry.previousStatus} → ${entry.newStatus}`
      : `Início → ${entry.newStatus}`;
    item.appendChild(title);

    const details = document.createElement('p');
    details.textContent = `${formatDateTime(entry.changedAt)} · Responsável: ${entry.actor}`;
    item.appendChild(details);

    if (entry.justification) {
      const justification = document.createElement('p');
      justification.textContent = `Justificativa: ${entry.justification}`;
      item.appendChild(justification);
    }
    list.appendChild(item);
  });

  historyView.hidden = false;
  document.getElementById('history-error').hidden = true;
}

function initializeContextLinks() {
  document.querySelectorAll('[data-history-link]').forEach(link => {
    const parameters = new URLSearchParams(window.location.search);
    link.href = `historico.html?${parameters.toString()}`;
  });

  document.querySelectorAll('[data-cancel-link]').forEach(link => {
    const parameters = new URLSearchParams(window.location.search);
    parameters.set('papel', link.dataset.actor);
    link.href = `cancelar.html?${parameters.toString()}`;
  });
}

function initializeCancellationForm() {
  const form = document.getElementById('cancellation-form');
  if (!form) {
    return;
  }

  const error = document.getElementById('cancellation-error');
  const parameters = new URLSearchParams(window.location.search);
  const status = parameters.get('status');
  const role = parameters.get('papel');
  const service = selectedService();
  const eventName = selectedEvent(parameters.get('evento'));
  const start = parameters.get('inicio');
  const history = readHistory(parameters);
  const startTime = start ? Date.parse(start) : NaN;
  const stateError = validateStateContext(parameters, status);
  const allowedStatuses = Object.prototype.hasOwnProperty.call(cancellationStates, role)
    ? cancellationStates[role]
    : null;
  const canCancel = allowedStatuses && allowedStatuses.includes(status);

  if (stateError || !service || !eventName || !history.entries) {
    error.textContent = stateError || history.error || 'Os dados da solicitação não correspondem ao histórico.';
    return;
  }
  if (!canCancel) {
    error.textContent = 'Este papel não pode cancelar a solicitação no estado atual.';
    return;
  }
  if (!Number.isFinite(startTime) || startTime <= Date.now()) {
    error.textContent = 'O cancelamento só está disponível antes do início do evento.';
    return;
  }

  document.getElementById('cancellation-context').textContent =
    `${service.name} · ${eventName} · ${status} · ${role}`;
  error.hidden = true;
  form.hidden = false;

  const reason = document.getElementById('cancellation-reason');
  reason.addEventListener('input', () => reason.setCustomValidity(''));
  form.addEventListener('submit', event => {
    event.preventDefault();
    const justification = reason.value.trim();
    if (!justification) {
      reason.setCustomValidity('Informe a justificativa para cancelar a reserva.');
      reason.reportValidity();
      return;
    }
    if (startTime <= Date.now()) {
      error.textContent = 'O evento já começou; o cancelamento não pode ser realizado.';
      error.hidden = false;
      form.hidden = true;
      return;
    }

    const nextParameters = new URLSearchParams(window.location.search);
    const actor = role === 'organizador' ? 'Organizador' : 'Prestador';
    const transitionError = appendTransition(nextParameters, 'CANCELADA', actor, justification);
    if (transitionError) {
      error.textContent = transitionError;
      error.hidden = false;
      return;
    }

    nextParameters.set('justificativa', justification);
    window.location.href = `cancelada.html?${nextParameters.toString()}`;
  });
}

function initializeOutcomePages() {
  const parameters = new URLSearchParams(window.location.search);
  const outcomes = [
    { status: 'EM_ANALISE', viewId: 'analysis-view', errorId: 'analysis-error', messageId: 'analysis-error-message' },
    { status: 'APROVADA', viewId: 'approved-view', errorId: 'approved-error', messageId: 'approved-error-message' },
    { status: 'RECUSADA', viewId: 'refused-view', errorId: 'refused-error', messageId: 'refused-error-message' },
    { status: 'CONFIRMADA', viewId: 'confirmed-view', errorId: 'confirmed-error', messageId: 'confirmed-error-message' },
    { status: 'CANCELADA', viewId: 'cancelled-view', errorId: 'cancelled-error', messageId: 'cancelled-error-message' }
  ];

  outcomes.forEach(outcome => {
    const view = document.getElementById(outcome.viewId);
    if (!view) {
      return;
    }

    const error = document.getElementById(outcome.errorId);
    const message = document.getElementById(outcome.messageId);
    const validationError = validateStateContext(parameters, outcome.status);
    if (validationError) {
      message.textContent = validationError;
      error.hidden = false;
      return;
    }
    view.hidden = false;
    error.hidden = true;
  });

  const history = readHistory(parameters);
  const refusalReason = document.getElementById('refusal-reason');
  if (refusalReason && parameters.get('status') === 'RECUSADA' && history.entries) {
    refusalReason.textContent = history.entries[history.entries.length - 1].justification
      || 'O fornecedor não informou um motivo nesta demonstração.';
  }

  const cancellationSummary = document.getElementById('cancellation-summary');
  if (cancellationSummary && parameters.get('status') === 'CANCELADA' && history.entries) {
    const actor = history.entries[history.entries.length - 1].actor;
    cancellationSummary.textContent =
      `Cancelado por ${actor}. Justificativa: ${history.entries[history.entries.length - 1].justification}`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initializeCatalog();
  initializeServiceDetails();
  initializeRequestForm();
  initializeRequestSummary();
  initializeTransitionLinks();
  initializeProviderDecisionForm();
  initializeHistoryPage();
  initializeContextLinks();
  initializeCancellationForm();
  initializeOutcomePages();
});

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

function selectedService() {
  const serviceId = new URLSearchParams(window.location.search).get('servico');
  return serviceId && Object.prototype.hasOwnProperty.call(services, serviceId)
    ? services[serviceId]
    : null;
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
  const serviceId = parameters.get('servico');
  const eventId = parameters.get('evento');
  const service = serviceId && Object.prototype.hasOwnProperty.call(services, serviceId)
    ? services[serviceId]
    : null;
  const eventName = eventId && Object.prototype.hasOwnProperty.call(events, eventId)
    ? events[eventId]
    : null;
  const start = parameters.get('inicio');
  const end = parameters.get('fim');
  if (!service || !eventName || !start || !end || start >= end) {
    invalidRequest.hidden = false;
    return;
  }

  document.getElementById('summary-service').textContent = service.name;
  document.getElementById('summary-event').textContent = eventName;
  document.getElementById('summary-start').textContent = formatDateTime(start);
  document.getElementById('summary-end').textContent = formatDateTime(end);
  document.getElementById('summary-observation').textContent = parameters.get('observacao') || 'Nenhuma';
  summary.hidden = false;
  invalidRequest.hidden = true;
}

document.addEventListener('DOMContentLoaded', () => {
  initializeCatalog();
  initializeServiceDetails();
  initializeRequestForm();
  initializeRequestSummary();
});

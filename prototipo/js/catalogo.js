'use strict';

/*
 * Catálogo e detalhe de serviço lidos da API.
 *
 * As consultas são públicas (não exigem login). Os filtros são enviados ao
 * servidor, que faz a busca; a página só valida o formato do que foi digitado
 * e mostra o resultado, os estados de carregamento, de lista vazia e de erro.
 */
(function () {
  const api = window.EventFyApi;
  const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
  const dateTime = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' });
  const ICONS = [
    ['som', '🔊'], ['ilumin', '🔊'], ['espaco', '🏛️'],
    ['equipe', '👥'], ['aliment', '🍽️'], ['buffet', '🍽️']
  ];
  const SEARCH_DELAY_MS = 300;

  function byId(id) {
    return document.getElementById(id);
  }

  function normalize(text) {
    return String(text || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  }

  function iconFor(category) {
    const key = normalize(category);
    const match = ICONS.find(([word]) => key.includes(word));
    return match ? match[1] : '🎉';
  }

  function formatPrice(value) {
    const number = Number(value);
    return Number.isFinite(number) ? currency.format(number) : 'Preço a consultar';
  }

  function formatPeriod(period) {
    return `${dateTime.format(new Date(period.data_inicio))} a ${dateTime.format(new Date(period.data_fim))}`;
  }

  /* ---------- Catálogo ---------- */

  function buildCard(service) {
    const card = document.createElement('article');
    card.className = 'card';

    const thumb = document.createElement('div');
    thumb.className = 'thumb';
    thumb.textContent = iconFor(service.categoria);
    card.appendChild(thumb);

    const body = document.createElement('div');
    body.className = 'card-body';

    const pill = document.createElement('span');
    pill.className = 'pill';
    pill.textContent = service.categoria;
    body.appendChild(pill);

    const title = document.createElement('h2');
    title.textContent = service.nome;
    body.appendChild(title);

    const description = document.createElement('p');
    description.textContent = service.descricao || 'Sem descrição informada.';
    body.appendChild(description);

    const place = document.createElement('p');
    place.className = 'muted';
    place.textContent = service.localizacao || 'Local não informado';
    body.appendChild(place);

    const price = document.createElement('strong');
    price.textContent = `${formatPrice(service.preco)} / evento`;
    body.appendChild(price);

    const link = document.createElement('a');
    link.className = 'button small';
    link.href = `servico.html?servico=${encodeURIComponent(service.id_servico)}`;
    link.textContent = 'Ver detalhes';
    body.appendChild(link);

    card.appendChild(body);
    return card;
  }

  /* Lê os campos de filtro; devolve { query } ou { error } com a mensagem de validação. */
  function readFilters() {
    const text = id => byId(id).value.trim();
    const minPrice = text('price-min') === '' ? null : Number(text('price-min'));
    const maxPrice = text('price-max') === '' ? null : Number(text('price-max'));
    const start = text('date-start');
    const end = text('date-end');

    if ((minPrice !== null && (!Number.isFinite(minPrice) || minPrice < 0))
        || (maxPrice !== null && (!Number.isFinite(maxPrice) || maxPrice < 0))
        || (minPrice !== null && maxPrice !== null && maxPrice < minPrice)) {
      return { error: 'Informe uma faixa de preço válida.' };
    }
    if ((start && !end) || (!start && end) || (start && end && end < start)) {
      return { error: 'Informe um período de disponibilidade válido.' };
    }

    const query = {
      termo: text('search'),
      categoria: byId('category').value,
      preco_minimo: minPrice,
      preco_maximo: maxPrice,
      localizacao: text('location'),
      limit: 100
    };
    if (start && end) {
      // O servidor exige data e hora com fuso; o dia inteiro, no horário local.
      query.data_inicio = new Date(`${start}T00:00:00`).toISOString();
      query.data_fim = new Date(`${end}T23:59:59`).toISOString();
    }
    return { query };
  }

  function initializeCatalog() {
    const cards = byId('cards');
    if (!cards) {
      return;
    }
    const emptyState = byId('empty-state');
    const filterError = byId('filter-error');
    const catalogError = byId('catalog-error');
    const status = byId('catalog-status');
    const category = byId('category');
    let latestRequest = 0;

    function showMessage(element, message) {
      element.textContent = message;
      element.hidden = false;
    }

    async function loadCategories() {
      try {
        const services = await api.apiFetch('/api/servicos', { auth: false, query: { limit: 100 } });
        const names = [...new Set(services.map(service => service.categoria))]
          .sort((a, b) => a.localeCompare(b, 'pt-BR'));
        names.forEach(name => {
          const option = document.createElement('option');
          option.value = name;
          option.textContent = name;
          category.appendChild(option);
        });
      } catch (error) {
        // As categorias são um atalho; a listagem principal mostra o erro.
      }
    }

    async function loadServices() {
      const request = ++latestRequest;
      const filters = readFilters();
      filterError.hidden = true;
      catalogError.hidden = true;
      emptyState.hidden = true;

      if (filters.error) {
        cards.replaceChildren();
        status.hidden = true;
        showMessage(filterError, filters.error);
        return;
      }

      status.textContent = 'Carregando serviços...';
      status.hidden = false;
      try {
        const services = await api.apiFetch('/api/servicos', { auth: false, query: filters.query });
        if (request !== latestRequest) {
          return; // chegou uma resposta mais nova; esta já não vale
        }
        cards.replaceChildren(...services.map(buildCard));
        status.hidden = true;
        emptyState.hidden = services.length > 0;
      } catch (error) {
        if (request !== latestRequest) {
          return;
        }
        cards.replaceChildren();
        status.hidden = true;
        showMessage(catalogError, error.message);
      }
    }

    let timer = null;
    function scheduleSearch() {
      window.clearTimeout(timer);
      timer = window.setTimeout(loadServices, SEARCH_DELAY_MS);
    }

    ['search', 'price-min', 'price-max', 'location'].forEach(id => {
      byId(id).addEventListener('input', scheduleSearch);
    });
    ['category', 'date-start', 'date-end'].forEach(id => {
      byId(id).addEventListener('change', loadServices);
    });

    loadCategories();
    loadServices();
  }

  /* ---------- Detalhe do serviço ---------- */

  function initializeServiceDetails() {
    const detail = byId('service-detail');
    if (!detail) {
      return;
    }
    const loading = byId('service-loading');
    const notFound = byId('service-not-found');
    const message = byId('service-error-message');
    const serviceId = new URLSearchParams(window.location.search).get('servico');

    function showProblem(text) {
      loading.hidden = true;
      message.textContent = text;
      notFound.hidden = false;
    }

    if (!/^[0-9]+$/.test(serviceId || '')) {
      showProblem('Volte ao catálogo e escolha um serviço para consultar os detalhes.');
      return;
    }

    api.apiFetch(`/api/servicos/${serviceId}`, { auth: false }).then(service => {
      byId('service-image').textContent = iconFor(service.categoria);
      byId('service-category').textContent = service.categoria;
      byId('service-name').textContent = service.nome;
      byId('service-description').textContent = service.descricao || 'Sem descrição informada.';
      byId('service-price').textContent = formatPrice(service.preco);
      byId('service-location').textContent = service.localizacao || 'Local não informado';

      const availability = byId('service-availability');
      const periods = service.disponibilidades.slice(0, 3).map(formatPeriod);
      availability.textContent = periods.length > 0
        ? periods.join(' · ')
        : 'Nenhum período publicado pelo prestador';

      byId('request-link').href = `reserva.html?servico=${encodeURIComponent(service.id_servico)}`;
      loading.hidden = true;
      detail.hidden = false;
    }).catch(error => {
      showProblem(error.status === 404
        ? 'Este serviço não existe ou foi desativado. Volte ao catálogo e escolha outro.'
        : error.message);
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initializeCatalog();
    initializeServiceDetails();
  });
})();

'use strict';

/*
 * Módulo de acesso à API do EventFy.
 *
 * Reúne em um só lugar: o endereço da API, a guarda do token de sessão e a
 * função apiFetch, que envia as requisições e traduz os erros do servidor.
 * As páginas não montam requisições por conta própria; usam este módulo.
 *
 * O servidor continua sendo quem decide o que cada papel pode fazer. O papel
 * lido do token serve apenas para a tela mostrar as opções certas.
 */
(function () {
  const DEFAULT_API_URL = 'http://127.0.0.1:8000';
  const API_BASE = (window.EVENTFY_API_URL || DEFAULT_API_URL).replace(/\/+$/, '');
  const TOKEN_KEY = 'eventfy.token';
  const ROLE_LABELS = {
    ORGANIZADOR: 'Organizador',
    PRESTADOR: 'Prestador',
    ADMINISTRADOR: 'Administrador'
  };

  // O armazenamento do navegador pode estar bloqueado; nesse caso a sessão
  // dura apenas enquanto a página estiver aberta.
  let memoryToken = null;

  function readToken() {
    try {
      return window.sessionStorage.getItem(TOKEN_KEY) || memoryToken;
    } catch (error) {
      return memoryToken;
    }
  }

  function saveToken(token) {
    memoryToken = token;
    try {
      window.sessionStorage.setItem(TOKEN_KEY, token);
    } catch (error) {
      // Segue com a cópia em memória.
    }
  }

  function clearToken() {
    memoryToken = null;
    try {
      window.sessionStorage.removeItem(TOKEN_KEY);
    } catch (error) {
      // Nada a limpar.
    }
  }

  function decodeTokenPayload(token) {
    const part = token.split('.')[1];
    if (!part) {
      return null;
    }
    try {
      const base64 = part.replace(/-/g, '+').replace(/_/g, '/');
      const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4);
      const binary = window.atob(padded);
      const json = decodeURIComponent(
        Array.from(binary, char => '%' + char.charCodeAt(0).toString(16).padStart(2, '0')).join('')
      );
      return JSON.parse(json);
    } catch (error) {
      return null;
    }
  }

  /* Devolve { token, userId, role, expiresAt } ou null quando não há sessão válida. */
  function getSession() {
    const token = readToken();
    if (!token) {
      return null;
    }
    const payload = decodeTokenPayload(token);
    if (!payload || !payload.role || !Number.isFinite(payload.exp)
        || payload.exp * 1000 <= Date.now()) {
      clearToken();
      return null;
    }
    return {
      token,
      userId: Number(payload.sub),
      role: payload.role,
      expiresAt: payload.exp * 1000
    };
  }

  function roleLabel(role) {
    return ROLE_LABELS[role] || role;
  }

  class ApiError extends Error {
    constructor(status, code, message) {
      super(message);
      this.name = 'ApiError';
      this.status = status;
      this.code = code;
    }
  }

  function messageFromBody(body, status) {
    if (body && body.error && body.error.message) {
      return { code: body.error.code || 'ERROR', message: body.error.message };
    }
    if (body && Array.isArray(body.detail) && body.detail.length > 0) {
      return {
        code: 'VALIDATION_ERROR',
        message: body.detail.map(item => item.msg).filter(Boolean).join(' ')
      };
    }
    return { code: 'ERROR', message: `A API respondeu com erro (HTTP ${status}).` };
  }

  /*
   * Envia uma requisição à API e devolve o JSON da resposta.
   * options: method, body (objeto), query (objeto) e auth (padrão true).
   * Em caso de falha lança ApiError com status, code e message em português.
   */
  async function apiFetch(path, options = {}) {
    const { method = 'GET', body, query, auth = true } = options;
    const url = new URL(API_BASE + path);
    if (query) {
      Object.entries(query).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          url.searchParams.set(key, value);
        }
      });
    }

    const headers = { Accept: 'application/json' };
    if (body !== undefined) {
      headers['Content-Type'] = 'application/json';
    }
    const session = auth ? getSession() : null;
    if (session) {
      headers.Authorization = `Bearer ${session.token}`;
    }

    let response;
    try {
      response = await window.fetch(url, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body)
      });
    } catch (error) {
      throw new ApiError(
        0,
        'NETWORK_ERROR',
        `Não foi possível conectar à API (${API_BASE}). Verifique se ela está em execução.`
      );
    }

    let data = null;
    if (response.status !== 204) {
      try {
        data = await response.json();
      } catch (error) {
        data = null;
      }
    }

    if (!response.ok) {
      const { code, message } = messageFromBody(data, response.status);
      if (response.status === 401 && auth) {
        clearToken();
      }
      throw new ApiError(response.status, code, message);
    }
    return data;
  }

  async function login(email, password) {
    const data = await apiFetch('/api/auth/login', {
      method: 'POST',
      body: { email, senha: password },
      auth: false
    });
    saveToken(data.access_token);
    return getSession();
  }

  /* Revoga a sessão no servidor e limpa o token local, mesmo se a API não responder. */
  async function logout() {
    try {
      await apiFetch('/api/auth/logout', { method: 'POST' });
    } catch (error) {
      // O token local é descartado de qualquer forma.
    }
    clearToken();
  }

  /*
   * Aceita só endereços relativos de páginas do próprio protótipo
   * (por exemplo "catalogo.html?servico=2"), para o parâmetro "retorno"
   * não poder levar o usuário a outro site.
   */
  function safeReturnTarget(value) {
    return typeof value === 'string' && /^[a-z0-9-]+\.html(\?[^#\s]*)?$/i.test(value)
      ? value
      : 'catalogo.html';
  }

  function currentPageTarget() {
    const page = window.location.pathname.split('/').pop() || 'index.html';
    return safeReturnTarget(page + window.location.search);
  }

  /*
   * Garante que há sessão (e, se informado, um dos papéis permitidos).
   * Sem sessão, envia a pessoa para a tela de entrada e depois de volta aqui.
   * Devolve a sessão, ou null quando redirecionou.
   */
  function requireSession(allowedRoles) {
    const session = getSession();
    if (!session) {
      const target = encodeURIComponent(currentPageTarget());
      window.location.replace(`entrar.html?retorno=${target}`);
      return null;
    }
    if (allowedRoles && !allowedRoles.includes(session.role)) {
      return { ...session, forbidden: true };
    }
    return session;
  }

  /*
   * Estados em que cada papel pode cancelar (RF14 e RN09). O servidor aplica a
   * regra de verdade, inclusive a janela antes do início do evento; aqui ela só
   * decide se o botão "Cancelar reserva" deve aparecer.
   */
  const CANCELLABLE_STATES = {
    ORGANIZADOR: ['SOLICITADA', 'EM_ANALISE', 'APROVADA', 'CONFIRMADA'],
    PRESTADOR: ['CONFIRMADA']
  };

  function canCancel(role, reservation) {
    const states = CANCELLABLE_STATES[role];
    return Boolean(states)
      && states.includes(reservation.status)
      && new Date(reservation.data_inicio) > new Date();
  }

  window.EventFyApi = {
    API_BASE,
    canCancel,
    ApiError,
    apiFetch,
    login,
    logout,
    getSession,
    requireSession,
    roleLabel,
    safeReturnTarget,
    currentPageTarget
  };
})();

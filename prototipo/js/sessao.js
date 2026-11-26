'use strict';

/*
 * Interface da sessão: a faixa "Entrar / Sair" do cabeçalho e o formulário
 * da tela de entrada. Depende de api.js, que deve ser carregado antes.
 */
(function () {
  const api = window.EventFyApi;

  function buildSessionBox() {
    const header = document.querySelector('header');
    if (!header) {
      return;
    }

    // Reúne os links existentes e a faixa de sessão em um único bloco à direita.
    const links = document.createElement('div');
    links.className = 'header-links';
    header.querySelectorAll(':scope > a').forEach(link => links.appendChild(link));

    const box = document.createElement('div');
    box.className = 'session-box';
    const session = api.getSession();

    if (session) {
      const who = document.createElement('span');
      who.className = 'session-role';
      who.textContent = api.roleLabel(session.role);
      box.appendChild(who);

      const exit = document.createElement('button');
      exit.type = 'button';
      exit.className = 'session-exit';
      exit.textContent = 'Sair';
      exit.addEventListener('click', async () => {
        exit.disabled = true;
        await api.logout();
        window.location.href = 'entrar.html';
      });
      box.appendChild(exit);
    } else if (!document.getElementById('login-form')) {
      const enter = document.createElement('a');
      enter.href = `entrar.html?retorno=${encodeURIComponent(api.currentPageTarget())}`;
      enter.textContent = 'Entrar';
      box.appendChild(enter);
    }

    links.appendChild(box);
    header.appendChild(links);
  }

  function initializeLoginPage() {
    const form = document.getElementById('login-form');
    if (!form) {
      return;
    }

    const error = document.getElementById('login-error');
    const submit = document.getElementById('login-submit');
    const returnTarget = api.safeReturnTarget(
      new URLSearchParams(window.location.search).get('retorno')
    );

    if (api.getSession()) {
      window.location.replace(returnTarget);
      return;
    }

    form.addEventListener('submit', async event => {
      event.preventDefault();
      error.hidden = true;
      submit.disabled = true;
      submit.textContent = 'Entrando...';
      try {
        await api.login(
          document.getElementById('login-email').value.trim(),
          document.getElementById('login-password').value
        );
        window.location.href = returnTarget;
      } catch (failure) {
        error.textContent = failure.status === 401
          ? 'E-mail ou senha incorretos.'
          : failure.message;
        error.hidden = false;
        submit.disabled = false;
        submit.textContent = 'Entrar';
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    buildSessionBox();
    initializeLoginPage();
  });
})();

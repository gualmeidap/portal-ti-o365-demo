/* Runs the Flask app inside the browser (Pyodide) and shows its pages in an iframe.
 * Links and forms inside the page are intercepted and handed to navegador.pedir(),
 * which goes through Flask's own routing, guards and session. No server involved. */
(() => {
  const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.29.5/full/';
  const pt = (navigator.language || '').toLowerCase().startsWith('pt');
  const T = pt ? {
    runtime: 'Carregando o Python…', packages: 'Carregando o Flask…', code: 'Carregando o portal…',
    start: 'Iniciando…', note: 'O código Python de verdade roda dentro do seu navegador (WebAssembly). Nada é enviado a um servidor.',
    failed: 'Não foi possível iniciar a demo neste navegador: ',
  } : {
    runtime: 'Loading Python…', packages: 'Loading Flask…', code: 'Loading the portal…',
    start: 'Starting…', note: 'The real Python code runs inside your browser (WebAssembly). Nothing is sent to a server.',
    failed: 'Could not start the demo in this browser: ',
  };
  const $ = (id) => document.getElementById(id);
  const tela = $('tela');
  let pedir = null;
  let atual = '/';

  function progresso(chave, pct) {
    $('passo').textContent = T[chave] || '';
    $('progresso').style.width = `${pct}%`;
  }

  function carregarScript(src) {
    return new Promise((ok, falha) => {
      const s = document.createElement('script');
      s.src = src;
      s.onload = ok;
      s.onerror = () => falha(new Error(`could not load ${src}`));
      document.head.append(s);
    });
  }

  async function iniciar() {
    $('nota').textContent = T.note;
    progresso('runtime', 10);
    await carregarScript(`${PYODIDE}pyodide.js`);
    const py = await window.loadPyodide({ indexURL: PYODIDE });
    const manifesto = await (await fetch('py/manifest.json', { cache: 'no-cache' })).json();
    progresso('packages', 40);
    await py.loadPackage(['sqlite3', 'jinja2', 'markupsafe', 'click',
      ...manifesto.wheels.map((w) => new URL(`py/wheels/${w}`, location.href).href)]);
    progresso('code', 70);
    for (const arquivo of manifesto.files) {
      const texto = await (await fetch(`py/${arquivo}`, { cache: 'no-cache' })).text();
      const caminho = `/home/pyodide/portal/${arquivo}`;
      py.FS.mkdirTree(caminho.slice(0, caminho.lastIndexOf('/')));
      py.FS.writeFile(caminho, texto);
    }
    progresso('start', 90);
    py.runPython('import os, sys; os.chdir("/home/pyodide/portal"); sys.path.insert(0, "/home/pyodide/portal")\nimport navegador');
    pedir = py.globals.get('navegador').pedir;
    progresso('start', 100);
  }

  /* Script injected into every page: hands links and forms back to this shell. */
  const PONTE = `<script>(function(){
    var shell = window.parent;
    function enviar(form, botao){
      var dados = new FormData(form);
      if (botao && botao.name) dados.append(botao.name, botao.value);
      var pares = []; dados.forEach(function(v,k){ pares.push([k, String(v)]); });
      shell.portalNavegar((form.getAttribute('method')||'GET').toUpperCase(), form.getAttribute('action') || shell.location.hash.slice(1) || '/', pares);
    }
    document.addEventListener('click', function(e){
      var a = e.target.closest('a[href]');
      if (!a) return;
      var href = a.getAttribute('href');
      if (href.charAt(0) === '/' ) { e.preventDefault(); shell.portalNavegar('GET', href, []); }
    });
    document.addEventListener('submit', function(e){ e.preventDefault(); enviar(e.target, e.submitter); });
    HTMLFormElement.prototype.submit = function(){ enviar(this, null); };
  })();<\/script>`;

  function mostrar(html) {
    const comPonte = html.includes('</body>') ? html.replace('</body>', `${PONTE}</body>`) : html + PONTE;
    tela.srcdoc = comPonte;
  }

  window.portalNavegar = (metodo, caminho, campos) => {
    if (metodo === 'GET' && caminho.includes('?') === false && campos.length) {
      caminho += '?' + new URLSearchParams(campos).toString();
    }
    const res = pedir(metodo, caminho, campos, navigator.language || 'pt-BR');
    const [status, final, html] = res.toJs();
    res.destroy();
    // A POST answered in place (no redirect) is not a page you can come back to.
    const navegavel = metodo === 'GET' || final !== caminho.split('?')[0];
    if (navegavel) {
      atual = final;
      if (location.hash.slice(1) !== final) history.pushState(null, '', `#${final}`);
    }
    mostrar(html);
    return status;
  };

  window.addEventListener('popstate', () => {
    const destino = location.hash.slice(1) || '/';
    if (destino !== atual) window.portalNavegar('GET', destino, []);
  });

  iniciar().then(() => {
    $('boot').hidden = true;
    tela.hidden = false;
    window.portalNavegar('GET', location.hash.slice(1) || '/', []);
  }).catch((e) => { $('passo').textContent = T.failed + e.message; });
})();

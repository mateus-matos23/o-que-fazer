// O VLibras só é carregado quando o cidadão pede: antes disso nada sai para terceiros (ADR 0008).
const PLUGIN = "https://vlibras.gov.br/app/vlibras-plugin.js";
const TIMEOUT_MS = 15000;
const POLL_MS = 200;

const aside = document.getElementById("libras");
const openButton = document.getElementById("libras-open");
const status = document.getElementById("libras-status");

// Espera uma condição do widget, que se monta de forma assíncrona depois do carregamento.
function waitFor(find, onFound, onTimeout) {
  const started = Date.now();
  const timer = setInterval(() => {
    const found = find();
    if (found) { clearInterval(timer); onFound(found); }
    else if (Date.now() - started > TIMEOUT_MS) { clearInterval(timer); onTimeout(); }
  }, POLL_MS);
  return timer;
}

function fail() {
  openButton.removeAttribute("aria-disabled");
  status.textContent = "Não foi possível abrir o VLibras agora. Tente de novo mais tarde.";
}

// Primeiro botão visível do painel do VLibras, que fica numa shadow root aberta.
function widgetControl() {
  const buttons = document.getElementById("vlibras-app-root")?.shadowRoot?.querySelectorAll("button") ?? [];
  return [...buttons].find((b) => b.tabIndex === 0 && b.getBoundingClientRect().width > 0);
}

function start(initButton) {
  initButton.style.width = initButton.style.height = "44px"; // o oficial tem 40 px; o site adota 44 (Fase 11c)
  aside.remove();
  initButton.click();
  waitFor(widgetControl, (control) => control.focus(), () => document.getElementById("conteudo").focus());
}

openButton.addEventListener("click", () => {
  if (openButton.getAttribute("aria-disabled") === "true") return;
  openButton.setAttribute("aria-disabled", "true");
  status.textContent = "Carregando o VLibras…";
  const timer = waitFor(() => window.VLibrasWidget?.initBtn, start, fail);
  // Numa nova tentativa o script já pode ter rodado; injetá-lo de novo duplicaria o widget.
  if (window.VLibras) return;
  const script = document.createElement("script");
  script.src = PLUGIN;
  script.onerror = () => { clearInterval(timer); script.remove(); fail(); };
  document.body.append(script);
});

aside.hidden = false;

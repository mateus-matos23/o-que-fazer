// Varredura de acessibilidade com axe-core (WCAG 2.x A/AA) via Chromium headless e CDP.
// Uso: node scripts/a11y-scan.mjs [URL_BASE]  (padrão http://127.0.0.1:8000; servidor no ar e conteúdo carregado)
// O Chromium vem de CHROME_BIN ou do cache do Playwright. Sai com código 1 se houver violação.
import { spawn } from "node:child_process";
import { mkdtempSync, readFileSync, readdirSync, rmSync, existsSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { join } from "node:path";
import { setTimeout as sleep } from "node:timers/promises";

const BASE = (process.argv[2] ?? "http://127.0.0.1:8000").replace(/\/$/, "");
const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
const MAX_STEPS = 30; // limite de páginas por jornada; mais que isso indica laço no fluxo
const AXE = readFileSync(new URL("../node_modules/axe-core/axe.min.js", import.meta.url), "utf8");

function chromeBin() {
  if (process.env.CHROME_BIN) return process.env.CHROME_BIN;
  const cache = join(homedir(), ".cache", "ms-playwright");
  const builds = existsSync(cache) ? readdirSync(cache).filter((d) => /^chromium-\d+$/.test(d)).sort() : [];
  if (!builds.length) throw new Error("Chromium não encontrado: defina CHROME_BIN.");
  return join(cache, builds.at(-1), "chrome-linux64", "chrome");
}

async function launch() {
  const profile = mkdtempSync(join(tmpdir(), "a11y-scan-"));
  const proc = spawn(chromeBin(), ["--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`, "about:blank"], { stdio: "ignore" });
  const portFile = join(profile, "DevToolsActivePort");
  for (let i = 0; i < 100 && !existsSync(portFile); i++) await sleep(100);
  if (!existsSync(portFile)) throw new Error("Chromium não abriu a porta de depuração.");
  await sleep(100); // o arquivo é criado antes de ser escrito
  const port = readFileSync(portFile, "utf8").split("\n")[0];
  const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" })).json();
  const exited = new Promise((resolve) => proc.once("exit", resolve));
  // O perfil só pode ser apagado depois que o Chromium termina de escrever nele.
  const close = async () => { proc.kill(); await exited; rmSync(profile, { recursive: true, force: true }); };
  return { wsUrl: target.webSocketDebuggerUrl, close };
}

function connect(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let nextId = 0;
  const pending = new Map();
  const waiters = [];
  ws.onmessage = ({ data }) => {
    const msg = JSON.parse(data);
    if (msg.id !== undefined) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
    } else {
      for (const w of waiters.filter((w) => w.method === msg.method)) { waiters.splice(waiters.indexOf(w), 1); w.resolve(msg.params); }
    }
  };
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++nextId;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });
  const once = (method) => new Promise((resolve) => waiters.push({ method, resolve }));
  return new Promise((resolve) => { ws.onopen = () => resolve({ send, once, close: () => ws.close() }); });
}

async function evaluate(cdp, expression) {
  const { result, exceptionDetails } = await cdp.send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (exceptionDetails) throw new Error(`Erro no navegador: ${exceptionDetails.exception?.description ?? exceptionDetails.text}`);
  return result.value;
}

// Executa a ação (navegar, enviar formulário) e espera a próxima página carregar.
async function untilLoaded(cdp, action) {
  const loaded = cdp.once("Page.loadEventFired");
  await action();
  await loaded;
  return evaluate(cdp, "location.href");
}

const goto = (cdp, path) => untilLoaded(cdp, () => cdp.send("Page.navigate", { url: BASE + path }));
const submit = (cdp, script) => untilLoaded(cdp, () => evaluate(cdp, script));

const report = new Map();
async function scan(cdp, label) {
  // Todas as perguntas de uma situação têm a mesma URL e o mesmo título; o h1 distingue as páginas.
  const key = `${label} ${await evaluate(cdp, "location.pathname + location.search + ' — ' + (document.title.startsWith('Erro') ? 'Erro: ' : '') + document.querySelector('h1')?.textContent.trim()")}`;
  if (report.has(key)) return;
  await evaluate(cdp, AXE);
  const violations = await evaluate(cdp, `axe.run(document, { runOnly: { type: "tag", values: ${JSON.stringify(TAGS)} } })
    .then((r) => r.violations.map((v) => ({ id: v.id, impact: v.impact, help: v.help, targets: v.nodes.map((n) => n.target.join(" ")) })))`);
  report.set(key, violations);
}

const links = (cdp, pattern) => evaluate(cdp, `[...new Set([...document.querySelectorAll("main a[href]")]
  .map((a) => a.pathname).filter((p) => ${pattern}.test(p)))]`);

// Marca a primeira opção de cada grupo e envia o formulário da página.
const ANSWER_FIRST = `(() => {
  const form = document.querySelector("form.answer-form");
  form.querySelector(".choices input").click();
  form.requestSubmit();
})()`;

async function walkJourney(cdp, situationPath) {
  let url = await goto(cdp, situationPath);
  for (let step = 0; step < MAX_STEPS; step++) {
    const path = new URL(url).pathname;
    if (path.endsWith("/plano/")) {
      await scan(cdp, "plano");
      await goto(cdp, path.replace(/plano\/$/, "respostas/"));
      await scan(cdp, "revisão");
      return;
    }
    await scan(cdp, path.endsWith("/atendimento/") ? "atendimento" : "pergunta");
    url = await submit(cdp, ANSWER_FIRST);
  }
  throw new Error(`Jornada ${situationPath} passou de ${MAX_STEPS} páginas sem chegar ao plano.`);
}

const browser = await launch();
let failed = false;
try {
  const cdp = await connect(browser.wsUrl);
  await cdp.send("Page.enable");

  // Autoverificação: uma imagem sem alt precisa ser apontada, senão a varredura não vale.
  await goto(cdp, "/");
  await evaluate(cdp, `document.querySelector("main").insertAdjacentHTML("beforeend", '<img src="x.png">')`);
  await scan(cdp, "autoverificação");
  if (!report.get([...report.keys()][0]).some((v) => v.id === "image-alt")) throw new Error("O axe não apontou image-alt: a varredura não está funcionando.");
  report.clear();

  await goto(cdp, "/");
  await scan(cdp, "início");
  for (const path of (await links(cdp, /^\/comecar\//)).slice(0, 2)) { await goto(cdp, path); await scan(cdp, "triagem"); }
  await goto(cdp, "/fora-da-cobertura/");
  await scan(cdp, "fora da cobertura");
  await goto(cdp, "/onde-resolvo/?q=cpf");
  await scan(cdp, "busca");
  const [procedure] = await links(cdp, /^\/onde-resolvo\/[^/]+\/$/);
  if (procedure) { await goto(cdp, procedure); await scan(cdp, "procedimento"); }

  await goto(cdp, "/situacoes/");
  await scan(cdp, "situações");
  const situations = await links(cdp, /^\/s\/[^/]+\/$/);
  if (!situations.length) throw new Error("Nenhuma situação em /situacoes/: o conteúdo foi carregado?");
  // Estado de erro: enviar a primeira pergunta sem resposta; submit() pula o "required" do navegador.
  await goto(cdp, situations[0]);
  await submit(cdp, `document.querySelector("form.answer-form").submit()`);
  await scan(cdp, "pergunta com erro");
  for (const path of situations) await walkJourney(cdp, path);
  cdp.close();
} finally {
  await browser.close();
}

for (const [page, violations] of report) {
  if (!violations.length) { console.log(`ok     ${page}`); continue; }
  failed = true;
  console.log(`FALHOU ${page}`);
  for (const v of violations) console.log(`  [${v.impact}] ${v.id}: ${v.help}\n    ${v.targets.slice(0, 5).join("\n    ")}`);
}
console.log(`\n${report.size} páginas verificadas (${TAGS.join(", ")}).`);
process.exit(failed ? 1 : 0);

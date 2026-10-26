# ADR 0008 — Tradução para Libras com o VLibras, carregado só a pedido

**Estado:** Proposto. Aguarda decisão do autor; nada foi implementado.
**Data:** 26/10/2026

## Contexto

O VLibras é a suíte gratuita do governo federal (MGI, MDHC e LAVID/UFPB) que traduz texto de páginas web para Libras com um avatar 3D. Para quem tem Libras como primeira língua, o português escrito pode ser uma segunda língua, então o ganho é real. A [ADR 0007](0007-criterio-js-e-dependencias.md) exige que um script de terceiro seja oficial e opcional, carregado por ação do cidadão, e nunca usado em página que exibe as respostas dele. O custo também precisa ser medido antes da decisão.

### O que diz a documentação oficial

- **Instalação:** uma tag `<script src="https://vlibras.gov.br/app/vlibras-plugin.js">`; o widget se inicializa sozinho ([integração](https://www.vlibras.gov.br/doc/widget/installation/webpageintegration.html)).
- **Hospedagem própria:** é possível com `rootPath`, mas assim o widget deixa de receber atualizações e correções.
- **CSP:** a página oficial cita só `frame-src https://vlibras.gov.br` e `font-src https://vlibras.gov.br https://cdn.jsdelivr.net` ([CSP](https://www.vlibras.gov.br/doc/widget/installation/content-security-policy.html)).
- **Tradução:** o cidadão ativa o widget, passa o ponteiro sobre um texto e clica nele ([tradução de texto](https://www.vlibras.gov.br/doc/widget/functionalities/text-translation.html)).
- **Navegadores suportados:** Chrome, Firefox e Safari.
- **Licença:** LGPL-3.0 ([repositório](https://github.com/spbgovbr-vlibras/vlibras-web-browsers)).
- **Lacunas:** a documentação não diz para onde vai o texto nem quanto o widget pesa.

### O que foi medido

Medição em 26/10/2026, no Chromium headless via CDP, com captura de rede da página, do iframe e do worker. A página de teste era descartável, fora do repositório, com um parágrafo do plano de perda de documentos. Versão servida: 7.12.2.

| Momento | O que foi transferido | Para onde |
| --- | --- | --- |
| Carregar a página com o script | cerca de 16 KB (script, ícone e imagem do convite) | `vlibras.gov.br`, que redireciona para `cdn.jsdelivr.net` |
| Abrir o widget (primeira vez) | cerca de **20,7 MB** (build Unity do avatar, fontes Rawline e ícones) | `cdn.jsdelivr.net` e `vlibras.gov.br/app/unity/` |
| Traduzir uma frase de 19 palavras | 1,2 KB na tradução e cerca de 267 KB nas animações dos sinais | `traducao2.vlibras.gov.br` e `dicionario2.vlibras.gov.br` |

- **O que é enviado:** só o texto clicado, em `POST /translate` com corpo `{"text": "..."}`. Não houve requisição de analytics (PostHog ou outro) nem outro POST. O próprio carregamento expõe ao jsdelivr e ao vlibras.gov.br o IP do cidadão e o endereço da página (`Referer`), mesmo que ele nunca use o widget.
- **Teclado:**
  - O botão é um `<button>` com `aria-label` em português, alcançável por Tab, com foco visível, e abre com Enter.
  - A tradução de um texto foi testada com clique. O caminho só por teclado não foi verificado, e a documentação descreve apenas o uso com ponteiro.
- **Alvo:** o botão mede 40×40 px. Cumpre o AA (24 px), mas fica abaixo dos 44 px que o projeto adotou (Fase 11c). A documentação só permite personalizar contorno, foco e filtro.
- **Disponibilidade:** na primeira tentativa, a tradução expirou ("A tradução demorou muito e foi cancelada"). Na segunda, respondeu. O serviço está fora do nosso controle.
- **Não medido:** o cache entre visitas e o comportamento em celular real, Firefox e Safari.

## Decisão proposta

1. **Um botão próprio "Ver em Libras"** no cabeçalho, com 44 px. O script do VLibras **só é injetado quando o cidadão aciona esse botão**, e depois o foco vai para o botão do widget.
   - Sem esse clique, nenhuma requisição sai para terceiros. Isso evita os 16 KB e a exposição de IP e página em todo acesso.
   - O botão avisa o tamanho antes ("pode baixar cerca de 20 MB"), porque o público tem conexão instável.
2. **Fora da página "Rever respostas"** e de qualquer página que mostre fatos declarados pelo cidadão (ADR 0007, ponto 4). Lá, o texto clicado seria uma resposta pessoal enviada a um servidor externo.
3. **Sem JavaScript, nada muda.** O botão é escondido até o script próprio confirmar que pode rodar, então nunca aparece um controle que não funciona.
4. **Script próprio pequeno** em `guidance/static/guidance/`, servido localmente, só com a injeção sob demanda, sem dependência.
5. **CSP:** o projeto não define CSP hoje. Se definir, precisa liberar:
   - `script-src` e `font-src`: `vlibras.gov.br` e `cdn.jsdelivr.net`;
   - `frame-src`: `vlibras.gov.br`;
   - `connect-src`: `traducao2.vlibras.gov.br` e `dicionario2.vlibras.gov.br`;
   - `worker-src`: `blob:`.

   Pela medição, isso vai além do que a documentação lista.
6. **Integridade (SRI):** o endereço oficial redireciona para uma versão fixa do jsdelivr, que hoje é a 7.12.2.
   - Um `integrity` no endereço oficial quebraria a cada atualização.
   - A alternativa é apontar para a URL versionada do jsdelivr, com `integrity`, e atualizar a versão à mão. Assim, só o primeiro script é verificado: os demais, como `vlibras-plugin-app.js`, o Unity e os sinais, são carregados por ele e não têm SRI.
   - O risco de CDN comprometida fica só reduzido, não eliminado. A escolha entre receber as atualizações oficiais e fixar a versão com SRI fica para o autor.
7. **Texto de privacidade:** junto ao botão, uma linha diz que o texto escolhido é enviado ao serviço VLibras do governo federal.

## Alternativas consideradas

| Alternativa | Motivo da rejeição |
| --- | --- |
| Tag oficial em todas as páginas | Contata terceiros em todo acesso, sem ação do cidadão (ADR 0007, ponto 4), e inclui a página de respostas. |
| Hospedar a build própria (`rootPath`) | São cerca de 20 MB no repositório e na imagem, sem as atualizações oficiais. A tradução e o dicionário continuam externos, então o ganho de privacidade é pequeno. |
| Não adotar | Deixa sem atendimento quem tem Libras como primeira língua, num serviço ao cidadão. O custo, com o carregamento a pedido, só recai sobre quem escolhe usar. |

## Consequências, se aceita

- É a primeira dependência de produção fora do servidor. Se o serviço sair do ar, só a tradução para Libras falha. O fluxo principal não depende dela.
- A verificação precisa cobrir:
  - a página sem JavaScript (botão ausente);
  - nenhuma requisição externa antes do clique;
  - foco depois da ativação;
  - ausência do botão em "Rever respostas".
- Os testes de HTML cobrem a presença e a ausência do botão. A medição de rede fica na verificação no navegador.

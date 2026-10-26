# ADR 0004 — Frontend em templates Django com CSS próprio e meta WCAG 2.2 AA

**Estado:** Aceito. Decisão do autor em 24/10/2026.
**Data:** 24/10/2026

## Contexto

O núcleo (Fases 0 a 5) entrega o fluxo completo em templates Django sem estilo. A Fase 6 precisa definir três coisas:
- a abordagem de frontend (pendência 5);
- o nível de acessibilidade pretendido e como verificá-lo (pendência 10);
- o que entra dos requisitos RF18 ("Onde resolvo?") e RF02 (texto livre).

O público é o cidadão, em grande parte usando smartphone e conexões instáveis.

## Decisão

1. **Frontend:**
   - Templates Django renderizados no servidor.
   - Um único arquivo CSS próprio em `guidance/static/guidance/`.
   - Sem etapa de build, sem JavaScript obrigatório e sem dependência nova.
   - A fonte Atkinson Hyperlegible Next (licença SIL OFL 1.1, arquivo junto às fontes) é servida localmente, sem CDN.
   - Revisto em 26/10/2026: "sem JavaScript obrigatório e sem dependência nova" passou a seguir o critério da [ADR 0007](0007-criterio-js-e-dependencias.md). O fluxo principal continua funcionando sem JavaScript.
2. **Acessibilidade:** a meta é WCAG 2.2 nível AA. A verificação é própria:
   - testes de HTML para rótulos, landmarks, idioma e associação de erros;
   - verificação no navegador com o agente `verificador-ui`: só teclado, foco visível, zoom de 200%, largura de 360 px e contraste calculado das cores do tema.
   - O resultado é registrado em `docs/implementacao/README.md`. Não é certificação.
3. **RF18 em versão simples:**
   - Busca por texto no título e na descrição dos procedimentos publicados.
   - O resultado leva a uma página de detalhe com órgão, requisitos, canais, custo, prazo e fonte.
   - A página não avalia aplicabilidade, porque não há fatos.
4. **RF02 continua pendente.** A estratégia de interpretação de texto livre (pendência 6) não foi decidida.
5. **Identidade visual:**
   - Paleta própria, que não imita a do gov.br, para o site não se passar por portal oficial.
   - O plano é apresentado como um roteiro em sequência, e as etapas da mesma camada aparecem como independentes.
   - Revisto em 26/10/2026 (Fase 9): a paleta passou a vir das fachadas e dos azulejos de São Luís (cal, cobalto, ocre e verde-petróleo). As restrições desta ADR não mudaram.

## Alternativas consideradas

| Alternativa | Motivo da rejeição |
| --- | --- |
| htmx (trocas parciais de página) | Dependência nova, e cada troca parcial exige gerenciar foco e anúncios para leitores de tela. O ganho é pequeno em um fluxo de poucas perguntas. |
| Tailwind com build | Exige uma toolchain extra e um passo de build para um CSS pequeno. |
| SPA (React ou similar) | Duplica no cliente o estado que já está na sessão e piora o desempenho em aparelhos modestos. |
| Varredura automática com axe-core | Exige uma dependência de teste ou um script externo. Pode ser acrescentada depois, sem mudar esta decisão. |

## Consequências

- Cada tela funciona sem JavaScript, e voltar e corrigir respostas usa navegação comum.
- A verificação de acessibilidade é manual e assistida. Ela fica sujeita a omissões que uma ferramenta automática pegaria.
- O CSS é mantido à mão. Com poucas telas, um arquivo continua legível.

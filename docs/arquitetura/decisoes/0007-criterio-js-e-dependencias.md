# ADR 0007 — Critério para JavaScript e dependências no frontend

**Estado:** Consolidado. Decisão do autor em 26/10/2026.
**Data:** 26/10/2026

## Contexto

A [ADR 0004](0004-frontend-e-acessibilidade.md) fixou "sem JavaScript obrigatório e sem dependência nova". Na prática isso funcionou como proibição: qualquer acréscimo seria rejeitado, mesmo que o ganho fosse alto e o custo, baixo.

Uma revisão externa sugeriu govbr-ds, Bootstrap, Tailwind, HTMX com Alpine.js, widget-tweaks ou crispy-forms e VLibras. Avaliar essas sugestões mostrou o problema da proibição:
- ela rejeita com o mesmo argumento uma ferramenta sem ganho, como o widget-tweaks;
- ela também rejeita uma ferramenta com ganho real de acessibilidade, como o VLibras, ou uma que nunca chega ao cidadão, como o axe-core no dev.

O que a ADR 0004 protege continua válido. O público usa celular modesto e conexão instável. A navegação de página inteira é a mais acessível: o leitor de tela anuncia a página nova e o botão Voltar funciona. A verificação de acessibilidade é manual, então cada interação nova custa trabalho de verificação.

## Decisão

O item 1 da ADR 0004 passa a seguir este critério:

1. **O fluxo principal funciona sem JavaScript.** Escolher a situação, responder, ver o plano, rever respostas e buscar não podem depender de script. Este ponto não é negociável.
2. **Dependência ou JavaScript em produção só entra se resolver uma necessidade observada que HTML e CSS não resolvem.** A proposta registra o custo em quatro frentes:
   - peso transferido;
   - trabalho de acessibilidade (foco, anúncios, teclado);
   - manutenção;
   - privacidade.
3. **Dependências de desenvolvimento e de teste têm exigência menor**, porque não chegam ao cidadão. Ainda passam pela aprovação do autor.
4. **Script de terceiro só entra se for de órgão oficial e opcional.** Ele só carrega por ação do cidadão e nunca em página que exibe as respostas dele, para cumprir o invariante 9 (o mínimo de dados pessoais).

## Alternativas reavaliadas

| Alternativa | Resultado | Motivo |
| --- | --- | --- |
| Padrão Digital de Governo (govbr-ds) | Rejeitada | Imita a identidade do portal oficial, e o site não pode se passar por ele (ADR 0004, item 5). Também exigiria reescrever o CSS. As boas práticas do padrão continuam servindo de referência. |
| Bootstrap 5 | Rejeitada | Exige reescrever o CSS para obter componentes que já existem. Não fecha nenhuma lacuna observada. |
| Tailwind | Rejeitada | Exige build e reescrita, e não fecha nenhuma lacuna observada. |
| HTMX com Alpine.js | Rejeitada | Cada troca parcial exige gerenciar foco e `aria-live`. As páginas são leves e o CSS fica em cache, então o ganho de não recarregar é pequeno. |
| django-widget-tweaks ou crispy-forms | Rejeitada | Ganho nulo. Os poucos formulários já são renderizados com `fieldset`, `legend` e erros associados. |
| axe-core (só no dev) | Aceita (Fase 11b) | A verificação manual pode deixar omissões passar. O pacote não chega ao cidadão (ponto 3). |
| VLibras | Em estudo (Fase 11d) | O ganho real é atender quem tem Libras como primeira língua. Antes de decidir, é preciso medir o peso, os domínios contatados e o que é enviado (ponto 4). |

## Consequências

- Uma sugestão futura é avaliada pelos quatro pontos. Ela não é mais rejeitada só por existir.
- Toda dependência de produção nova precisa de ADR ou de registro com o custo medido.
- A verificação manual continua. O axe-core a complementa, não a substitui.

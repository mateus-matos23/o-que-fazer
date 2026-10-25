# Interface, experiência do usuário e acessibilidade

> Princípios de interação, telas previstas, estrutura do plano, direção visual, acessibilidade e briefing de prototipação.

## Experiência do usuário, interface e acessibilidade

### Princípios de interação

- Começar por uma situação reconhecível pelo cidadão.
- Fazer uma pergunta principal por tela.
- Apresentar somente distinções relevantes para o contexto.
- Oferecer “não sei” quando a ausência de informação for plausível.
- Permitir voltar e corrigir respostas.
- Mostrar progresso sem prometer uma quantidade fixa de perguntas em um fluxo adaptativo.
- Apresentar o plano resumido antes dos detalhes.
- Explicar o motivo de cada providência em linguagem simples.
- Manter fonte e encaminhamento oficial acessíveis.

### Linguagem simples

Proposto (Fase 7, 25/10/2026): regras de redação para perguntas e opções, pensadas para públicos com idade, escolaridade e familiaridade com tecnologia variadas.

- Frases curtas.
- Opções na primeira pessoa, descrevendo o que aconteceu com o cidadão: "A empresa me mandou embora".
- Termo oficial entre parênteses, quando existir: "(dispensa sem justa causa)".
- A dica da pergunta é opcional e fica ligada ao fieldset por `aria-describedby`.
- O efeito de cada resposta aparece em texto, sem animação.
- "Saiu do seu plano" nunca é redigido como "você não tem direito". Não aplicável é avaliação orientativa sobre os fatos informados, não decisão oficial.

### Telas previstas no documento inicial

| Tela ou estado | Conteúdo principal |
| --- | --- |
| Home | “O que aconteceu?”, situações frequentes e acesso aos dois modos. |
| Seleção de situação | Categorias e acontecimentos compreensíveis. |
| Perguntas | Uma pergunta principal, opções, retorno e progresso. |
| Orientação intermediária | Próximo passo para descobrir uma informação desconhecida. |
| Seu plano | Providências ordenadas e resumo do contexto. |
| Detalhe da etapa | Motivo, requisitos, órgão, canal, custo, prazo, dependências e fonte. |
| Onde resolvo? | Busca direta e contexto mínimo do serviço. |
| Lista de situações | Documentos, trabalho, família, veículos e cadastros. |
| Divergência ou desatualização | Informação sobre o limite e encaminhamento para confirmação. |
| Visualização mobile | Adaptação das telas principais a smartphones. |

### Estrutura do plano

Cada etapa deve apresentar título, explicação curta, motivo de aplicabilidade, órgão, canais, requisitos, dependências e fonte. Custos e prazos aparecem quando disponíveis. A ordem deve tornar visíveis os pré-requisitos e as etapas independentes.

Proposto (Fase 7, 25/10/2026): o plano começa por "Comece por aqui", que indica por onde começar. Em seguida vem "O que separar antes", agrupado por etapa e sem mesclar requisitos parecidos de procedimentos diferentes. O plano também tem versão para impressão.

### Direção visual discutida

Interface clara, pouco carregada, com espaço em branco, tipografia legível, cards grandes, ícones simples e destaque para a ação principal. A aparência deve transmitir confiança, neutralidade e acolhimento, com atenção prioritária ao smartphone.

Proposto (24/10/2026): paleta própria em verde-petróleo sobre fundo claro, que não imita o gov.br, e a fonte Atkinson Hyperlegible Next, servida localmente. Os tokens e os contrastes estão no topo de `guidance/static/guidance/site.css` ([ADR 0004](../arquitetura/decisoes/0004-frontend-e-acessibilidade.md)). Não há sistema de componentes; uma identidade visual final não foi confirmada.

### Acessibilidade

Considerar contraste, redimensionamento de texto, alvos de interação adequados, navegação por teclado, rótulos compreensíveis, leitores de tela e informação que não dependa somente de cor ou ícone.

As WCAG 2.2 foram incorporadas como referência conceitual no referencial. Consolidado (24/10/2026): a meta é WCAG 2.2 nível AA, com verificação própria ([ADR 0004](../arquitetura/decisoes/0004-frontend-e-acessibilidade.md)). O resultado está no [registro de implementação](../implementacao/README.md). Não há certificação de acessibilidade, e o uso com leitor de tela real ainda não foi verificado.

## Direção para prototipação visual

O primeiro Markdown foi produzido para gerar uma amostra em V0, Lovable, Base44 ou ferramenta semelhante. O objetivo era visualizar a experiência antes de aprofundar a implementação.

Uma instrução coerente com o recorte atual é:

> Criar uma aplicação web responsiva chamada O que Fazer?, voltada a cidadãos que precisam descobrir os próximos passos de situações cotidianas envolvendo serviços públicos. Priorizar perda de documentos, CPF irregular e desligamento do trabalho. Na Home, apresentar “O que aconteceu?”, situações frequentes e o acesso “Já sei o que procuro — Onde resolvo?”. Conduzir uma pergunta principal por tela, com respostas compreensíveis, opção “não sei” e possibilidade de corrigir respostas. Ao final, apresentar “Seu plano”, com procedimentos aplicáveis, ordem, dependências, motivo da inclusão, requisitos, órgão, canal e fonte oficial. Demonstrar um esclarecimento intermediário para CPF desconhecido. Adotar interface leve, acessível e adequada a smartphones. As informações de demonstração devem ser identificadas como exemplos quando não houver conteúdo oficial validado. A plataforma orienta e encaminha aos canais oficiais; não confirma direitos nem executa serviços públicos.

Uma demonstração visual não comprova a implementação do motor de decisão nem a validação das fontes. Esses componentes precisam ser construídos e documentados separadamente.

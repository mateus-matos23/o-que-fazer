# Motor de orientação

> Como o sistema decide o que se aplica (aplicabilidade) e em que ordem apresentar (ordenação).

## Estruturas de dados e algoritmos

### Dois problemas separados

| Problema | Entrada | Saída |
| --- | --- | --- |
| Descobrir o que se aplica | Situação, fatos, regras e respostas. | Procedimentos aplicáveis e questões ainda indeterminadas. |
| Organizar a ordem | Procedimentos selecionados e dependências pertinentes. | Plano que respeita pré-requisitos e distingue ações independentes. |

Essa separação é central no referencial e na introdução. Um grafo de dependências não decide sozinho a elegibilidade ou a aplicabilidade.

### Estruturas propostas no histórico

| Estrutura | Uso proposto |
| --- | --- |
| Objeto ou `Map` | Manter fatos conhecidos da sessão. |
| `Set` | Manter candidatos sem duplicação. |
| Regras/predicados | Classificar aplicabilidade a partir dos fatos. |
| Grafo direcionado | Representar relações entre procedimentos. |
| DAG, quando válido | Representar dependências sem ciclos. |
| Máquina de estados | Organizar início, perguntas, esclarecimento e resultado da sessão. |

São alternativas de implementação discutidas, sem um código definitivo registrado.

### Avaliação ternária

- **Aplicável:** há informação suficiente e compatível com a regra.
- **Não aplicável:** há informação que afasta o procedimento naquele contexto.
- **Indeterminado:** faltam fatos necessários ou há ambiguidade relevante.

“Não sei” mantém o fato desconhecido. Pode gerar outra pergunta ou uma providência intermediária para consultar o canal oficial.

### Próxima pergunta

Foram discutidos critérios de prioridade e de ganho de informação: escolher perguntas capazes de diferenciar os candidatos remanescentes, evitando repetições e condições irrelevantes.

O trabalho de Quinlan sobre árvores de decisão foi incorporado como base conceitual. Isso não significa que o protótipo necessariamente adotará ID3, aprenderá regras administrativas automaticamente ou usará dados de treinamento.

A forma de calcular a utilidade da pergunta, os pesos, os desempates e a condição de parada permanecem pendentes. Um fluxo baseado em regras verificadas pode ser especificado antes de qualquer estratégia estatística.

### Ordenação topológica

Após selecionar os procedimentos, as dependências obrigatórias pertinentes podem ser representadas em um grafo dirigido sem ciclos e ordenadas topologicamente. Kahn foi utilizado como referência conceitual no referencial.

Etapas sem relação de precedência podem ser apresentadas como independentes. Em caso de várias ordens válidas, a prioridade de exibição precisa ser fundamentada, sem criar obrigação inexistente.

Um ciclo indica que o modelo ou a interpretação das fontes exige revisão. O sistema não deve produzir uma sequência aparentemente válida ignorando essa inconsistência.

### Explicabilidade e mudança de resposta

Cada etapa deve manter relação com fatos, regras e fontes que justificaram sua inclusão. Ao corrigir uma resposta, o motor reavalia candidatos e dependências e atualiza o plano.

### Requisitos e canais condicionais

`Requirement` e `ServiceChannel` podem ter uma `rule` opcional (RF25). `visible_items(items, facts)` (`guidance/engine/evaluation.py`) reaproveita `evaluate_rule` e devolve pares `(item, Tri)` na ordem original: sem regra, o item vale sempre; `APPLICABLE` aparece; `NOT_APPLICABLE` sai; `UNDETERMINED` (pergunta não respondida ou "não sei", RN03) aparece marcado "Pode valer para você". `PlanStep.requirements` e `PlanStep.channels` guardam o resultado, então mudar uma resposta muda os itens (invariante 8). `next_question` pontua as perguntas ainda não respondidas das regras de item indeterminadas, só para procedimentos `APPLICABLE`. Limite: itens condicionais de pré-requisitos puxados e de esclarecimentos não geram pergunta (a marca "pode valer" persiste), porque `next_question` só pontua candidatos `APPLICABLE`. O carregador exige que toda pergunta citada por regra de um procedimento relevante esteja ligada à situação. Se todos os itens ficam escondidos, a página diz que nenhum item da fonte vale para o que o cidadão informou, e não "Não informado" (RN11). `pending_rule_questions(catalog, facts, evaluations)` (`guidance/engine/evaluation.py`) reúne essas perguntas ainda relevantes; `next_question` a usa e descarta as já respondidas. Um esclarecimento (`clarifies`) só entra no plano enquanto o fato é "não sei" e a pergunta ainda é relevante: se o procedimento que a cita deixa de se aplicar (por exemplo, o cidadão edita os documentos e tira o CPF), a resposta antiga não gera etapa sem motivo. Na busca "Onde resolvo?" não há fatos, e os itens com regra aparecem marcados.

### Efeito da resposta

`answer_effect(catalog, before, after)` (`guidance/engine/effect.py`) compara o plano de antes com o de depois, sendo "no plano" as etapas de `build_plan`. Devolve as etapas que entraram (`entered`), as que saíram (`left`) e quantos procedimentos seguem em análise (`in_play`, igual a `len(plan.undetermined)`). Comparar planos, e não apenas aplicabilidade, evita dizer que saiu algo que nunca esteve nas etapas e inclui o esclarecimento de "não sei". É função pura; a camada de visão guarda o resultado na sessão como aviso de uso único (só slugs e um inteiro), consumido ao ser mostrado. Ciclo entre dependências propaga `DependencyCycleError`.

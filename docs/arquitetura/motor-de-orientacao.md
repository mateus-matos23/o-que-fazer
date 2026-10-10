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

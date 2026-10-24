# ADR 0002 — Motor de orientação baseado em regras, sem aprendizado de máquina

**Estado:** Aceito (aprovado pelo autor em 10/10/2026)  
**Data:** 10/10/2026

## Contexto

O motor precisa resolver dois problemas separados (ver [motor de orientação](../motor-de-orientacao.md)): decidir **o que se aplica** à situação do cidadão e decidir **em que ordem** apresentar as providências. A questão aberta era usar um algoritmo próprio ou um modelo de aprendizado de máquina (ML).

Restrições já registradas na documentação:

- **RN01 / RF15**: toda orientação publicada tem fundamento rastreável em fonte oficial.
- **RF19**: o sistema explica por que uma etapa aparece e por que depende de outra.
- **RN03 / RN04**: fato desconhecido não vira negativa; aplicabilidade é ternária.
- **RN08**: prioridade de exibição não cria requisito administrativo.
- **RN09 / RF16**: corrigir uma resposta recalcula o plano de forma previsível.
- Não há dados de treinamento: não existem sessões rotuladas nem histórico de atendimentos, e o protótipo cobre poucas jornadas.
- A referência a Quinlan (1986) é conceitual e não implica treinamento automático de regras ([referencial](../../academico/referencial-teorico.md)).

## Decisão

Adotar um **algoritmo próprio, baseado em conhecimento explícito**, composto por:

1. **Avaliação de regras** sobre os fatos da sessão, com resultado ternário (`APPLICABLE`, `NOT_APPLICABLE`, `UNDETERMINED`). Cada regra é cadastrada e revisada por humanos e aponta para uma fonte.
2. **Seleção da próxima pergunta** por critério determinístico calculado sobre as regras: escolher, entre as perguntas ainda não respondidas, a que pode alterar a aplicabilidade do maior número de candidatos indeterminados (inspiração no ganho de informação de Quinlan, **sem treinamento**). Pesos, desempate e condição de parada serão especificados com as jornadas reais (etapa 3).
3. **Ordenação topológica (Kahn)** sobre as dependências obrigatórias dos procedimentos aplicáveis; ciclo gera erro explícito de modelagem.

Aprendizado de máquina e modelos de linguagem **não** participam da decisão de aplicabilidade nem da ordenação.

## Alternativas consideradas

| Alternativa | Motivo da rejeição |
| --- | --- |
| Árvore de decisão treinada (ID3/C4.5) ou classificador | Sem dados rotulados; regras administrativas vêm de normas, não de padrões estatísticos; perde-se o vínculo regra → fonte. |
| LLM decidindo aplicabilidade ou gerando o plano | Não determinístico, difícil de auditar, risco de inventar requisitos, custos e prazos (viola RN01 e RN11). |
| Árvore de perguntas fixa por jornada | Simples, mas duplica perguntas entre jornadas e não trata bem "não sei" nem a correção de respostas; mantida como possível forma de *autoria*, não de execução. |

## Consequências

- Cada etapa do plano pode ser explicada pela cadeia fato → regra → fonte (atende RF19).
- O motor pode ser testado com casos fixos (entrada de fatos → plano esperado), o que também serve à avaliação do TCC.
- O custo passa para a **autoria do conhecimento**: as regras precisam ser escritas e revisadas a partir da [matriz de evidências](../../dados/evidencias/). A representação concreta das regras fica para o ADR 0003, depois do levantamento das jornadas.
- **Fora desta decisão**: interpretar texto livre (RF02, pendência 6). Se um modelo de linguagem for usado no futuro, seu papel se limita a sugerir uma `Situation` conhecida, com confirmação do usuário, e fica isolado do motor.

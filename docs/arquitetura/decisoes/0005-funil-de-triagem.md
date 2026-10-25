# ADR 0005 — Funil de triagem como árvore de nós em TOML

**Estado:** Consolidado.
**Data:** 25/10/2026

## Contexto

A Fase 7 (conversa guiada) quer que o cidadão chegue à situação respondendo perguntas amplas e simples, em vez de escolher numa lista de situações. A página inicial passa a ser esse funil (RF21). Ramos que ainda não têm jornada precisam dizer isso com clareza, em vez de levar a um beco sem saída.

## Decisão

1. **Árvore de nós em TOML.** O arquivo `content/triage.toml` descreve nós (`TriageNode`) e opções (`TriageChoice`), carregados por `load_content` junto do resto do conteúdo. Cada opção leva a exatamente um destino: outro nó, uma situação ou "fora da cobertura".
2. **Navegação por links GET, sem sessão.** Cada nó tem URL própria (`/` para o nó `inicio`, `/comecar/<slug>/` para os demais). Voltar é o botão do navegador ou o link "Voltar ao início".
3. **Ramo sem jornada leva ao limite de cobertura.** A página `/fora-da-cobertura/` diz que a situação ainda não é orientada, lista as situações existentes e oferece "Onde resolvo?".
4. **Toda situação é alcançável pelo funil.** A carga falha se uma situação não tem entrada pelo funil, se um nó é inalcançável, se há ciclo, se falta o nó `inicio` ou se uma opção não tem exatamente um destino. Sem nenhum nó `triage` no conteúdo, as validações do funil não se aplicam e a raiz mostra a lista de situações.
5. **Lista de situações mantida** em `/situacoes/`, como link secundário.

## Por que o funil não tem fonte

O funil é encaminhamento (RN02): ele só leva o cidadão até uma situação. Não afirma nada em nome de órgão, requisito, prazo ou direito, então não há o que citar. Qualquer afirmação oficial continua só nos procedimentos, que exigem fonte e trecho.

## Consequências

- Uma situação nova exige um ramo no funil, ou a carga falha.
- O funil não guarda respostas nem vira `Fact`: as escolhas não entram na sessão e não alteram regras ou plano.
- O texto das opções é editorial. Deve ser revisado para não insinuar elegibilidade.

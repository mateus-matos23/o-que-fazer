# Requisitos e regras de negócio

> Limites do sistema, requisitos funcionais (RF) e regras de negócio e de orientação (RN).

## Limites institucionais e funcionais

O sistema tem caráter orientativo. A confirmação de requisitos, elegibilidade, atendimento e decisão administrativa permanece com os órgãos competentes.

Não há compromisso de executar solicitações governamentais, autenticar o cidadão nos portais oficiais, consultar bases pessoais restritas ou abranger toda a burocracia brasileira. A orientação deve indicar quando uma condição exige confirmação oficial.

## Requisitos funcionais consolidados e previstos

Os requisitos abaixo organizam o conteúdo discutido. Eles precisam ser detalhados e rastreados na especificação; sua inclusão aqui não significa implementação concluída.

| ID | Requisito | Enquadramento |
| --- | --- | --- |
| RF01 | Permitir selecionar uma situação cotidiana entre as jornadas cobertas. | Núcleo do protótipo. |
| RF02 | Prever entrada por descrição de situação. | Visão do produto; interpretação pendente. |
| RF03 | Apresentar perguntas progressivas conforme o contexto. | Núcleo do protótipo. |
| RF04 | Permitir respostas únicas, múltiplas e “não sei”, conforme a pergunta. | Núcleo do protótipo. |
| RF05 | Evitar perguntas já respondidas ou irrelevantes para a orientação. | Núcleo do protótipo. |
| RF06 | Adaptar as perguntas às respostas anteriores. | Núcleo do protótipo. |
| RF07 | Eliminar procedimentos incompatíveis. | Núcleo do protótipo. |
| RF08 | Identificar procedimentos aplicáveis. | Núcleo do protótipo. |
| RF09 | Preservar situações indeterminadas e indicar informação faltante. | Núcleo do protótipo. |
| RF10 | Ordenar providências segundo dependências e prioridades fundamentadas. | Núcleo do protótipo. |
| RF11 | Apresentar um plano resumido e detalhes de cada etapa. | Núcleo do protótipo. |
| RF12 | Exibir requisitos e documentos quando disponíveis nas fontes. | Núcleo do protótipo. |
| RF13 | Exibir órgão responsável e canais online ou presenciais. | Núcleo do protótipo. |
| RF14 | Exibir custos e prazos quando documentados. | Condicionado à fonte. |
| RF15 | Exibir fonte oficial e data de verificação. | Núcleo do protótipo. |
| RF16 | Permitir revisar respostas e recalcular a jornada. | Núcleo do protótipo. |
| RF17 | Perguntar localização apenas quando ela alterar a orientação. | Núcleo do protótipo. |
| RF18 | Permitir busca direta por serviço no modo “Onde resolvo?”. | Visão do produto. |
| RF19 | Explicar por que uma etapa aparece e por que depende de outra. | Núcleo explicável. |
| RF20 | Tratar informação divergente, desatualizada ou não disponível. | Qualidade da orientação. |
| RF21 | Conduzir o cidadão até a situação por um funil de perguntas amplas (triagem), informando o limite de cobertura nos ramos sem jornada. Revisto em 27/10/2026: o funil só lista situações com jornada; o limite de cobertura continua nas respostas `out_of_coverage` e no aviso do plano. | Consolidado (Fase 7, fatia 2). |
| RF22 | Mostrar, após cada resposta, o efeito dela no plano (providências que entraram, que saíram e quantas seguem em análise). | Consolidado (Fase 7, fatia 3). |
| RF23 | Perguntar a preferência de atendimento (internet/aplicativo, telefone, pessoalmente, tanto faz) e ordenar os canais por ela, sem esconder nenhum. | Consolidado (Fase 7, fatia 4). |
| RF24 | Redigir perguntas e opções em linguagem simples, com dica opcional por pergunta. | Consolidado (Fase 7, fatia 1). |
| RF25 | Exibir requisitos e canais conforme os fatos informados, mantendo os de aplicabilidade indeterminada com marcação. | Consolidado (Fase 7, fatia 6). |
| RF26 | Destacar no plano por onde começar, listar o que separar antes (agrupado por etapa) e oferecer versão para impressão. | Consolidado (Fase 7, fatia 5). |

## Regras de negócio e de orientação

| ID | Regra |
| --- | --- |
| RN01 | Toda orientação publicada deve ter fundamento rastreável em fonte oficial pertinente ao serviço e ao território. |
| RN02 | Cada pergunta deve existir porque sua resposta pode alterar a aplicabilidade, a ordem ou o encaminhamento. Encaminhamento inclui levar à situação (funil de triagem), escolher os requisitos e canais exibidos e ordenar os canais pela preferência de atendimento. |
| RN03 | Fatos desconhecidos não devem ser convertidos automaticamente em respostas negativas. |
| RN04 | Um procedimento pode ser aplicável, não aplicável ou indeterminado. |
| RN05 | Uma situação pode gerar vários procedimentos, inclusive de órgãos diferentes. |
| RN06 | Procedimentos comuns a vários caminhos devem ser reunidos sem duplicação desnecessária. |
| RN07 | Dependências obrigatórias, condicionais e recomendadas precisam ser diferenciadas. |
| RN08 | Uma prioridade de apresentação não deve criar um requisito administrativo inexistente. |
| RN09 | Alterar uma resposta exige reavaliar as regras afetadas e a sequência resultante. |
| RN10 | A orientação termina quando há informação suficiente para o plano ou quando o limite da informação disponível exige confirmação externa. |
| RN11 | Custo, prazo e canal desconhecidos devem permanecer identificados como não informados; não cabe inventar valores. |
| RN12 | A data da consulta da fonte deve ser diferenciada da data de atualização declarada pelo órgão. |
| RN13 | Divergências relevantes precisam ser sinalizadas para revisão e registradas. |
| RN14 | A preferência de atendimento (internet, telefone ou presencial) deve ser considerada na ordem dos canais quando houver alternativa documentada; ela nunca esconde canais nem altera aplicabilidade. |
| RN15 | No uso básico, não será exigido cadastro e devem ser evitados dados pessoais desnecessários. |
| RN16 | Dicas e textos de ajuda das perguntas não afirmam regra, prazo ou definição sem trecho de fonte oficial; limitam-se a explicar por que se pergunta e como responder. |

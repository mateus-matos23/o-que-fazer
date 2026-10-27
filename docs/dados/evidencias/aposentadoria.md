# Evidências — Aposentadoria

Levantamento de fontes oficiais para a jornada "quero me aposentar", no recorte federal (INSS). Data da coleta: **27/10/2026** (amostras brutas, 09:57 a 09:58). A data de coleta não é a data de atualização declarada pelo órgão; as páginas declaram datas de "Última Modificação" entre 12/08/2026 e 20/08/2026, que aparecem separadas na tabela.

Estado: **Consolidado** para a aposentadoria por idade urbana, a aposentadoria por tempo de contribuição, o extrato do CNIS e o simulador (INSS, gov.br).

## Tabela-resumo

| Slug da fonte | Fonte | Órgão | Esfera | URL | Data declarada | Amostra |
| --- | --- | --- | --- | --- | --- | --- |
| `govbr-aposentadoria-idade-urbano` | Solicitar aposentadoria por idade (trabalhador urbano) | INSS | Federal | https://www.gov.br/pt-br/servicos/solicitar-aposentadoria-por-idade-trabalhador-urbano | Última Modificação: 12/08/2026 | [html-govbr-aposentadoria-idade-urbano.md](../amostras/html-govbr-aposentadoria-idade-urbano.md) |
| `govbr-aposentadoria-tempo-contribuicao` | Solicitar aposentadoria por tempo de contribuição | INSS | Federal | https://www.gov.br/pt-br/servicos/solicitar-aposentadoria-por-tempo-de-contribuicao | Última Modificação: 12/08/2026 | [html-govbr-aposentadoria-tempo-contribuicao.md](../amostras/html-govbr-aposentadoria-tempo-contribuicao.md) |
| `govbr-extrato-cnis` | Emitir extrato de contribuição (CNIS) | INSS | Federal | https://www.gov.br/pt-br/servicos/emitir-extrato-de-contribuicao-cnis | Última Modificação: 13/08/2026 | [html-govbr-extrato-cnis.md](../amostras/html-govbr-extrato-cnis.md) |
| `govbr-simular-aposentadoria` | Simular aposentadoria | INSS | Federal | https://www.gov.br/pt-br/servicos/simular-aposentadoria | Última Modificação: 20/08/2026 | [html-govbr-simular-aposentadoria.md](../amostras/html-govbr-simular-aposentadoria.md) |

## Decisões

- Duas perguntas: o tipo de aposentadoria (`SINGLE`, com "não sei") e o meio de trabalho (`SINGLE`, sem "não sei"). O meio só entra na aposentadoria por idade; a aposentadoria por tempo de contribuição não é restrita ao meio urbano segundo a página, então a regra dela depende só do tipo.
- Aposentadoria por idade urbana: regra com duas condições (tipo "por idade" e meio "urbano"). A descrição traz as condições literais da página ("O que é?"): carência mínima de 180 contribuições, 15 anos de tempo de contribuição e idade mínima de 65 anos (homem) ou 62 anos (mulher).
- Meio rural: fora da cobertura (`out_of_coverage`). A página de aposentadoria rural não foi encontrada (o slug correspondente retornou 404).
- Aposentadoria por tempo de contribuição: 35 anos (homem) ou 30 anos (mulher), com a frase literal sobre a regra de transição (Reforma da Previdência, Emenda Constitucional 103) para quem não tinha o tempo até 13/11/2019.
- "Não sei" no tipo mantém as duas aposentadorias indeterminadas, nunca descartadas (RN03). O simulador entra como esclarecimento, não como candidato. A página diz que "o resultado gerado pela calculadora vale somente para consulta e não garante direito à aposentadoria"; por isso a descrição do simulador repete essa ideia e manda o cidadão voltar à pergunta.
- Extrato do CNIS: sem regra, porque a página diz "Qualquer pessoa que possua cadastro no CNIS".
- Sem dependências entre os procedimentos (RN08).
- Requisitos: o bloco "Documentação" de cada página. As duas aposentadorias trazem identificação e CPF do titular e, quando houver, do procurador ou representante legal, mais a procuração ou o termo de representação; o simulador pede identificação e CPF do titular. O extrato do CNIS traz o mesmo bloco das aposentadorias.
- Canais: aplicativo e site do Meu INSS; telefone 135 "caso o sistema esteja indisponível"; atendimento presencial (agendamento pelo 135 ou unidade com acordo com o INSS) nas páginas de idade, tempo e extrato. O simulador só tem aplicativo e site.
- Prazo e custo: nenhum detalhe. "Tempo estimado de espera" (5 minutos; 30 dias corridos no presencial) e "Tempo de duração da etapa" ("Atendimento imediato") não são prazo de resposta do pedido, por isso não viram detalhe `DEADLINE`. As amostras não citam custo, então não há detalhe `COST`.

## Fora da jornada

Afirmações sem trecho literal ou sem fonte não entram. Custo e prazo desconhecidos aparecem como "não informado".

- Aposentadoria rural: a página gov.br não foi encontrada (slug retornou 404). O meio rural fica fora da cobertura.
- Aposentadoria por acordo internacional: não coletada.
- Certidão de tempo de contribuição: não coletada.
- Aposentadoria de servidor público: não coletada.

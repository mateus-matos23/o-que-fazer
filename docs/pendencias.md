# Riscos, entregáveis e pendências

> Riscos conhecidos, estado dos entregáveis e decisões ainda abertas.

## Riscos e limites já discutidos

| Risco ou limite | Encaminhamento previsto |
| --- | --- |
| Informação ausente ou pouco detalhada | Delimitar a jornada e registrar lacunas. |
| Fontes mudarem | Versionar e definir revisão. |
| Integração por formatos diferentes | Usar adaptadores e normalização. |
| API exigir autenticação | Avaliar acesso e alternativas públicas adequadas ao recorte. |
| Interpretação incorreta de requisitos | Revisar regras e manter vínculo com a fonte. |
| Encaminhamento como se fosse decisão oficial | Explicitar caráter orientativo e canal competente. |
| Falta de informação do cidadão | Estado indeterminado e esclarecimento intermediário. |
| Sobrecarga de perguntas ou resultado | Perguntas relevantes e plano resumido. |
| Cobertura excessiva para o prazo acadêmico | Priorizar poucas jornadas representativas. |
| Extrapolação de estudos externos | Preservar o contexto e os limites das referências. |
| Resultados insuficientes para afirmações amplas | Relacionar conclusões ao recorte e à amostra avaliados. |

## Entregáveis e pendências

### Entregáveis discutidos ou já produzidos

| Entregável | Estado documentado |
| --- | --- |
| Visão do produto em Markdown | Arquivo inicial localizado e consultado. |
| Explicação resumida para apresentação | Discussão histórica recuperada. |
| Registro consolidado no Google Docs | Produção e atualização relatadas no histórico. |
| Análise preliminar de viabilidade | Relato recuperado; evidências completas precisam ser reunidas. |
| Introdução acadêmica | Versões localizadas e consultadas. |
| Introdução e referencial teórico | Documento localizado e consultado. |
| Revisão de estilo com preservação de precisão | Instrução e relato recuperados. |
| Escopo consolidado em Markdown | Este arquivo. |
| Especificação detalhada e modelo físico de dados | Pendentes. |
| Protótipo funcional | Previsto; implementação não comprovada nesta consolidação. |
| Avaliação com usuários e resultados | Previstas; execução não comprovada. |
| Monografia completa | Prevista; capítulos posteriores ainda não comprovados. |

### Decisões que ainda precisam ser fechadas

1. Ramificações e serviços finais das três jornadas prioritárias.
2. URLs, exemplos e evidências reproduzíveis da prova de viabilidade. Em andamento: [matriz de evidências](dados/evidencias/README.md) das 3 jornadas (10/10/2026); amostras brutas coletadas em [amostras](dados/amostras/README.md). As fontes estaduais de perda de documentos ficaram fora do recorte do protótipo.
3. Critérios e frequência de atualização e resolução de divergências.
4. Modelo físico de dados e persistência das sessões.
5. ~~Stack de backend e acesso a dados~~ — resolvido: Django 6.1.2 + PostgreSQL 18 ([ADR 0001](arquitetura/decisoes/0001-stack.md)). Frontend e hospedagem continuam pendentes.
6. Estratégia de interpretação de texto livre.
7. Critério de seleção de perguntas, desempate e encerramento. Direção decidida (critério determinístico sobre as regras, sem ML) no [ADR 0002](arquitetura/decisoes/0002-motor-baseado-em-regras.md); pesos, desempate e parada seguem pendentes.
8. Representação concreta das regras e das dependências.
9. Forma de manutenção do conteúdo e necessidade de interface administrativa.
10. Procedimentos e nível pretendido de verificação de acessibilidade.
11. Amostra, instrumentos e protocolo da avaliação comparativa.
12. Cronograma com datas e critérios de conclusão de cada etapa.
13. Conferência final das referências e da normalização institucional.
14. Incorporação verificável da última revisão de estilo ao arquivo acadêmico.

Não há cronograma fechado ou resultados de avaliação suficientes para preencher essas pendências com números ou datas.

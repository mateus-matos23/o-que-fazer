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
| Especificação detalhada e modelo físico de dados | Em andamento. |
| Protótipo funcional | Em implementação: Fases 0 e 1 concluídas (ver [registro de implementação](implementacao/README.md)). |
| Avaliação com usuários e resultados | Previstas; execução não comprovada. |
| Monografia completa | Prevista; capítulos posteriores ainda não comprovados. |

### Decisões que ainda precisam ser fechadas

1. Ramificações e serviços finais das três jornadas prioritárias.
2. URLs, exemplos e evidências reproduzíveis da prova de viabilidade. Em andamento: [matriz de evidências](dados/evidencias/README.md) das 3 jornadas (10/10/2026); amostras brutas coletadas em [amostras](dados/amostras/README.md). As fontes estaduais de perda de documentos ficaram fora do recorte do protótipo.
3. Critérios e frequência de atualização e resolução de divergências.
4. Modelo físico de dados e persistência das sessões. Resolvido para fontes e catálogo (apps `sources` e `catalog`, ver [modelo físico](arquitetura/modelo-fisico-de-dados.md) e [registro de implementação](implementacao/README.md)); sessão do cidadão na sessão do Django, sem tabela própria e com expiração de 2 horas (decisão de 24/10/2026).
5. ~~Stack de backend e acesso a dados~~ — resolvido: Django 6.1.2 + PostgreSQL 18 ([ADR 0001](arquitetura/decisoes/0001-stack.md)). Frontend resolvido em 24/10/2026: templates Django com CSS próprio, sem JavaScript ([ADR 0004](arquitetura/decisoes/0004-frontend-e-acessibilidade.md)). Hospedagem continua pendente.
6. Estratégia de interpretação de texto livre. Segue pendente: o RF02 ficou fora da Fase 6 ([ADR 0004](arquitetura/decisoes/0004-frontend-e-acessibilidade.md)).
7. Critério de seleção de perguntas, desempate e encerramento. Direção decidida (critério determinístico sobre as regras, sem ML) no [ADR 0002](arquitetura/decisoes/0002-motor-baseado-em-regras.md); pesos, desempate e parada seguem pendentes.
8. ~~Representação concreta das regras e das dependências~~ — resolvido: regras e dependências como dados citados, carregados de TOML ([ADR 0003](arquitetura/decisoes/0003-regras-como-dados.md)).
9. Forma de manutenção do conteúdo e necessidade de interface administrativa. Decidido em 24/10/2026: arquivos TOML versionados + comando de carga; admin somente leitura.
10. Procedimentos e nível pretendido de verificação de acessibilidade. Decidido em 24/10/2026: meta WCAG 2.2 AA com verificação própria (testes de HTML e verificação no navegador), registrada no [registro de implementação](implementacao/README.md). Não é certificação; leitor de tela real, Firefox, Safari e impressão ainda não foram verificados.
11. Amostra, instrumentos e protocolo da avaliação comparativa.
12. Cronograma com datas e critérios de conclusão de cada etapa.
13. Conferência final das referências e da normalização institucional.
14. Incorporação verificável da última revisão de estilo ao arquivo acadêmico.

Não há cronograma fechado ou resultados de avaliação suficientes para preencher essas pendências com números ou datas.

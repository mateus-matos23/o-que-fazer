# Modelo conceitual de domínio

> Entidades e relações do domínio. Os nomes de código correspondentes estão no [glossário](../../CONTEXT.md).

## Modelo conceitual de dados

Os nomes abaixo descrevem responsabilidades do domínio; não constituem um esquema físico de tabelas aprovado.

| Entidade ou relação | Finalidade |
| --- | --- |
| Situação | Acontecimento pelo qual o cidadão inicia a orientação. |
| Pergunta | Informação necessária para distinguir casos relevantes. |
| Opção de resposta | Valores permitidos, incluindo seleção múltipla ou desconhecimento. |
| Fato da sessão | Conhecimento declarado durante a interação. |
| Regra | Condição explícita que afeta um procedimento ou pergunta. |
| Procedimento/serviço | Providência que pode integrar o plano. |
| Requisito | Condição ou documento necessário ao procedimento. |
| Dependência | Relação de precedência, com tipo e contexto. |
| Órgão | Instituição responsável ou canal competente. |
| Canal de atendimento | Meio online ou presencial documentado. |
| Abrangência territorial | Contexto geográfico ao qual a orientação se aplica. |
| Fonte | Registro de origem oficial da informação. |
| Importação e versão | Histórico da coleta e das alterações. |
| Jornada calculada | Conjunto de providências e ordem resultantes do contexto. |

Relações centrais:

- Uma situação pode acionar várias perguntas e procedimentos candidatos.
- Uma pergunta pode ser reutilizada em mais de uma situação.
- Um procedimento pode integrar mais de uma jornada.
- Uma regra usa fatos e afeta a aplicabilidade ou a necessidade de esclarecimento.
- Um procedimento pode ter requisitos, canais e dependências.
- Fontes devem fundamentar também requisitos e relações relevantes, não apenas o nome do serviço.
- Alterações de conteúdo devem poder ser distinguidas das respostas particulares de uma sessão.

A persistência da sessão e seu prazo de retenção ainda precisam ser definidos. Não se presume a criação de uma conta para o cidadão.

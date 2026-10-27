# Documentação — O que Fazer?

Documentação de concepção e modelagem do sistema. Originada da consolidação do escopo do TCC feita em 30/09/2026 e dividida em arquivos temáticos em 10/10/2026 (o arquivo original permanece no histórico do git como `docs/escopo-completo-tcc-o-que-fazer.md`).

## Resumo do projeto

**Produto:** O que Fazer?  
**Tema:** orientação ao cidadão no acesso a serviços públicos.  
**Entrada principal:** situação cotidiana.  
**Mecânica:** perguntas progressivas, fatos e regras verificáveis.  
**Resultado:** procedimentos aplicáveis e sequência fundamentada de próximos passos.  
**Recorte territorial:** federal, Maranhão e São Luís, conforme a jornada.  
**Jornadas prioritárias:** perda de documentos, CPF irregular, desligamento do trabalho, transferência de veículo, falecimento na família e aposentadoria (estas três entraram em 27/10/2026).\
**Caráter:** orientativo, com encaminhamento para fontes e canais oficiais.  
**Dados:** fontes heterogêneas com normalização, revisão e proveniência.  
**Stack:** Python 3.15, Django 6.1.2, PostgreSQL 18 e uv 0.13.0 (ver [ADR 0001](arquitetura/decisoes/0001-stack.md)).  
**Algoritmos discutidos:** filtragem de candidatos, seleção de perguntas e ordenação topológica.  
**Interface:** responsiva, linguagem simples, uma pergunta por tela, “não sei”, revisão de respostas e plano resumido.  
**Uso básico:** sem cadastro obrigatório e com minimização de dados pessoais.  
**Avaliação prevista:** comparação com busca convencional, com indicadores de eficácia, esforço e percepção.  
**Estado acadêmico documentado:** introdução e referencial teórico, com revisão de estilo discutida.  
**Próximos marcos:** a implementação do núcleo começou (Fases 0 a 7 concluídas, incluindo a conversa guiada em 25/10/2026; ver [registro de implementação](implementacao/README.md)); concluir a especificação e o restante do protótipo, avaliar e escrever os capítulos restantes.

## Mapa

| Arquivo | Conteúdo |
| --- | --- |
| [Glossário de domínio](../CONTEXT.md) | Termos do domínio e nomes usados no código. |
| [produto/visao.md](produto/visao.md) | Proposta de valor, problema, público, modos de uso e funcionalidades futuras. |
| [produto/jornadas.md](produto/jornadas.md) | Recorte territorial, jornadas prioritárias e candidatas, casos de borda. |
| [produto/requisitos.md](produto/requisitos.md) | Limites do sistema, requisitos funcionais (RF) e regras de negócio (RN). |
| [produto/interface-e-acessibilidade.md](produto/interface-e-acessibilidade.md) | Princípios de interação, telas, estrutura do plano e acessibilidade. |
| [arquitetura/visao-tecnica.md](arquitetura/visao-tecnica.md) | Stack, camadas de informação e componentes lógicos. |
| [arquitetura/modelo-de-dominio.md](arquitetura/modelo-de-dominio.md) | Entidades e relações conceituais. |
| [arquitetura/modelo-fisico-de-dados.md](arquitetura/modelo-fisico-de-dados.md) | Tabelas do `catalog`, citação com trecho verificado e carga de conteúdo. |
| [arquitetura/motor-de-orientacao.md](arquitetura/motor-de-orientacao.md) | Aplicabilidade ternária, próxima pergunta, ordenação topológica e explicabilidade. |
| [arquitetura/decisoes/](arquitetura/decisoes/) | Registros de decisões de arquitetura (ADR). |
| [dados/fontes-oficiais.md](dados/fontes-oficiais.md) | Prova de viabilidade, serviços analisados, formatos e autenticação. |
| [dados/evidencias/](dados/evidencias/README.md) | Matriz de evidências das jornadas: fontes, API Gov.br e classificação. |
| [dados/ingestao-e-proveniencia.md](dados/ingestao-e-proveniencia.md) | Pipeline de coleta, normalização, proveniência e divergências. |
| [academico/tcc.md](academico/tcc.md) | Título, questão de pesquisa, objetivos, metodologia, avaliação e monografia. |
| [academico/referencial-teorico.md](academico/referencial-teorico.md) | Eixos teóricos, ressalvas e inventário de referências. |
| [academico/normalizacao-e-estilo.md](academico/normalizacao-e-estilo.md) | Normas UNDB/ABNT e diretrizes editoriais. |
| [academico/historico.md](academico/historico.md) | Linha do tempo da concepção e base documental. |
| [implementacao/README.md](implementacao/README.md) | Registro de implementação: fases, estado e decisões tomadas. |
| [pendencias.md](pendencias.md) | Riscos, entregáveis e decisões em aberto. |

## Como utilizar esta documentação

Esta documentação reúne a concepção do produto, o escopo acadêmico, as propostas de arquitetura, as jornadas, a análise preliminar das fontes oficiais e as orientações de escrita discutidas ao longo do projeto. Serve como referência para continuar o TCC, apresentar a proposta e orientar a especificação e a implementação do protótipo.

É uma consolidação temática do histórico recuperado e dos documentos disponíveis, e não uma transcrição literal de todas as mensagens. Quando uma informação mais recente restringe uma proposta inicial, prevalece o recorte da versão acadêmica mais recente consultada. Detalhes não recuperados ficam registrados como pendências, em vez de serem preenchidos por suposição.

Os estados utilizados são:

| Estado | Significado |
| --- | --- |
| Consolidado | Consta na versão acadêmica mais recente consultada ou em uma escolha explícita do autor. |
| Proposto | Foi apresentado durante a elaboração, mas não há confirmação suficiente de adoção definitiva ou implementação. |
| Histórico | Representa uma formulação anterior ou uma etapa já discutida. |
| Futuro | Possibilidade de expansão além do protótipo delimitado. |
| Em andamento | Implementação iniciada e ainda não concluída (usado no [registro de implementação](implementacao/README.md)). |
| Pendente | Depende de definição, confirmação, documentação ou avaliação. |

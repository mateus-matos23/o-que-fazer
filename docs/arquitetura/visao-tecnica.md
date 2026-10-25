# Visão técnica

> Stack, camadas de informação e componentes lógicos do sistema.

## Arquitetura e armazenamento discutidos

### Direção técnica proposta

Foi sugerido **PostgreSQL como banco principal**, com entidades relacionais para o núcleo do domínio e uso controlado de **JSONB** para dados heterogêneos ou conteúdo bruto.

A proposta permite representar relações e preservar variações de origem sem exigir um segundo banco NoSQL no MVP. O PostgreSQL foi adotado (ver "Stack confirmada"); o uso concreto de JSONB será definido no modelo físico de dados, ainda pendente.

### Separação das camadas de informação

| Camada proposta | Responsabilidade |
| --- | --- |
| Fontes | Identificar órgão, endereço, território, formato e acesso. |
| Importações | Registrar cada coleta, resultado, data e versão. |
| Conteúdo bruto | Preservar dados antes da transformação. |
| Domínio normalizado | Representar serviços, requisitos, canais e documentos. |
| Conhecimento e regras | Relacionar fatos, perguntas, condições e procedimentos. |
| Jornada e apresentação | Produzir sequência explicável para o usuário. |

Arquivos originais maiores podem ser preservados em filesystem ou armazenamento de objetos, com referências no banco. A escolha do provedor ou serviço não foi fechada.

### Componentes lógicos

- Interface web responsiva.
- Lógica de sessão e coleta das respostas.
- Motor de avaliação das regras.
- Seleção da próxima pergunta.
- Construção e ordenação da jornada.
- Consulta de procedimentos e fontes.
- Adaptadores de ingestão e revisão de conteúdo.

Essas responsabilidades não exigem, por si, microserviços ou várias aplicações. A organização concreta do código está descrita na subseção "Organização do código" abaixo.

### Stack confirmada

**Consolidado em outubro de 2026** (ver [ADR 0001](decisoes/0001-stack.md)):

| Componente | Escolha |
| --- | --- |
| Linguagem | Python 3.15 |
| Framework web | Django 6.1.2 (backend, ORM e renderização das páginas) |
| Banco de dados | PostgreSQL 18 |
| Gerenciador de projeto e dependências | uv 0.13.0 |

Continuam **pendentes**: abordagem de frontend (templates Django puros ou com biblioteca de interatividade), hospedagem, autenticação administrativa e armazenamento de arquivos brutos maiores (hoje o conteúdo bruto fica no banco).

### Organização do código (Consolidado em 24/10/2026)

Estado de cada app no [registro de implementação](../implementacao/README.md). Hoje só `sources` está em `INSTALLED_APPS` (`config/settings.py`).

| App | Conteúdo | Estado |
| --- | --- | --- |
| `sources` | Fonte, Importação, Versão de fonte e Órgão; adaptadores de coleta e comando `fetch_sources`. | Implementado |
| `catalog` | Procedimento, Requisito, Canal, Dependência, Situação, Pergunta, Opção, Regra, Condição e o carregador de conteúdo (comando `load_content`, a partir de arquivos TOML em `content/`). | Em andamento |
| `guidance` | Motor de orientação em Python puro (avaliação ternária, próxima pergunta, ordenação em camadas, plano) e fluxo HTTP. | Pendente |

Os termos seguem o [glossário](../../CONTEXT.md).

Preferências e stacks discutidas em outros projetos do autor não são automaticamente decisões deste TCC.

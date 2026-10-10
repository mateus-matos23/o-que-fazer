# ADR 0001 — Stack do protótipo

**Estado:** Aceito  
**Data:** 10/10/2026

## Contexto

O escopo acadêmico exige um protótipo web responsivo com núcleo de domínio relacional (situações, perguntas, regras, procedimentos, dependências e fontes), conteúdo heterogêneo vindo de fontes oficiais e necessidade de manter conteúdo revisado. Até a consolidação de 30/09/2026 a stack constava como pendente; PostgreSQL com JSONB havia sido proposto em 12/08/2026.

## Decisão

- **Python 3.15** com **Django 6.1.2** como framework web único (backend, ORM, templates e admin).
- **PostgreSQL 18** como banco principal; JSONB reservado a conteúdo bruto ou heterogêneo de origem, conforme proposto.
- **uv 0.13.0** para gerenciamento do projeto, do ambiente e das dependências.
- Aplicação monolítica: as responsabilidades listadas na [visão técnica](../visao-tecnica.md#componentes-lógicos) não exigem microsserviços.

## Consequências

- O Django Admin é candidato natural à manutenção de conteúdo (pendência 9 em [pendências](../../pendencias.md)), sem decisão tomada.
- Não há segundo banco NoSQL no MVP.
- Continuam abertos: abordagem de frontend, hospedagem, autenticação administrativa e armazenamento de arquivos brutos maiores.

# Evidências — Jornadas candidatas (levantamento preliminar)

> Estado: **Proposto**. Levantamento de 24/10/2026 para decidir quais jornadas acrescentar. Nenhuma destas jornadas foi aprovada para o protótipo; a decisão é do autor com o orientador ([pendência 1](../../pendencias.md)).

Data da coleta: 2026-10-24. Data de coleta não é data de vigência; a data declarada pelo órgão está em cada [amostra](../amostras/README.md#coleta-de-24102026).

## Compra de veículo usado

| Serviço | Órgão | Esfera | Estado | Amostra |
| --- | --- | --- | --- | --- |
| Transferência de propriedade de veículo (digital) | DETRAN-MA | Estadual | **Confirmada**, sem data declarada | [html-detran-transf-digital.md](../amostras/html-detran-transf-digital.md) |
| Transferência de propriedade (balcão) | DETRAN-MA | Estadual | **Pendente**: página sem texto sem JavaScript (id 19272) | — |
| Consultar restrições e indicadores do veículo | Senatran | Federal | **Confirmada** (Última Modificação: 15/12/2025) | [html-govbr-restricoes-veiculo.md](../amostras/html-govbr-restricoes-veiculo.md) |

O que a jornada demonstraria: dependência obrigatória com fonte (vistoria aprovada em ECV antes da transferência digital) e uma ramificação por fatos (a página lista os casos que exigem atendimento no balcão, como herança, doação, leilão e pessoa jurídica). Que débitos ou restrições bloqueiem a transferência **não** está sustentado pelas amostras: é hipótese.

## Primeiro emprego

| Serviço | Órgão | Esfera | Estado | Amostra |
| --- | --- | --- | --- | --- |
| Obter a Carteira de Trabalho (Digital) | MTE | Federal | **Confirmada** em 10/10/2026 | [html-obter-a-carteira-de-trabalho.md](../amostras/html-obter-a-carteira-de-trabalho.md) |
| Buscar emprego no SINE | MTE | Federal | **Confirmada** (Última Modificação: 15/12/2025) | [html-govbr-sine-emprego.md](../amostras/html-govbr-sine-emprego.md) |
| Inclusão socioprodutiva: oficinas, cursos e vagas (SEMCAS) | Prefeitura de São Luís | Municipal | **Localizada** (carta de serviços, id 685), sem amostra | — |

O que a jornada demonstraria: reaproveitamento da jornada CPF irregular como pré-requisito condicional. A exigência de CPF regular para a Carteira de Trabalho Digital ainda precisa ser conferida no trecho da amostra.

## Nascimento de filho

| Serviço | Órgão | Esfera | Estado | Amostra |
| --- | --- | --- | --- | --- |
| Registro de nascimento e 1ª certidão | Cartório de registro civil | — | **Pendente**: sem fonte oficial localizada (não está no catálogo federal nem na carta de São Luís) | — |
| CPF do menor | Receita Federal / órgão de identificação | Federal | **Parcial**: a FAQ da CIN diz que o órgão de identificação pode inscrever o CPF do menor | [html-govbr-cin-faq.md](../amostras/html-govbr-cin-faq.md) |
| Inscrever-se no Cadastro Único | MDS (operado pelo município) | Federal | **Confirmada** (Última Modificação: 15/12/2025) | [html-govbr-cadunico-inscrever.md](../amostras/html-govbr-cadunico-inscrever.md) |
| Atualizar cadastro no SUS (Meu SUS Digital) | Ministério da Saúde | Federal | **Confirmada** (Última Modificação: 21/10/2026) | [html-govbr-sus-cadastro.md](../amostras/html-govbr-sus-cadastro.md) |

Risco: a cadeia "certidão → CPF" pode não existir como dependência, porque o CPF pode sair junto com a certidão ou no órgão de identificação. Sem fonte para o registro de nascimento, a jornada não tem o primeiro passo.

## Mudança de endereço

| Serviço | Órgão | Esfera | Estado | Amostra |
| --- | --- | --- | --- | --- |
| Mudança de município (veículo) | DETRAN-MA | Estadual | **Pendente**: página sem texto sem JavaScript (id 19281) | — |
| Transferência de domicílio eleitoral | TSE / TRE-MA | Federal (Justiça Eleitoral) | **Pendente**: HTTP 403 | — |
| Atualizar endereço no SUS | Ministério da Saúde | Federal | **Confirmada** | [html-govbr-sus-cadastro.md](../amostras/html-govbr-sus-cadastro.md) |

Hoje é a candidata com menos fontes confirmadas: as duas centrais (DETRAN e Justiça Eleitoral) exigem conferência no navegador.

## Resumo para decisão

| Candidata | Fontes centrais confirmadas | O que demonstra de novo |
| --- | --- | --- |
| Compra de veículo usado | Parcial (DETRAN-MA digital, Senatran); páginas de balcão em defeso eleitoral até o fim da eleição estadual | Dependência obrigatória e ramificação por fatos |
| Primeiro emprego | Sim (federais) | Reaproveitamento da jornada CPF irregular |
| Nascimento de filho | Não (registro de nascimento não localizado nem na conferência manual de 25/10) | Três esferas; a cadeia de dependências é incerta |
| Mudança de endereço | Não (DETRAN em defeso eleitoral; TSE não localizado) | Pergunta de território (RF17) |

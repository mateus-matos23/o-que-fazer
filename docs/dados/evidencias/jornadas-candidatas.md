# Evidências — Jornadas candidatas (levantamento preliminar)

> Estado: **Proposto**. Levantamento de 24/10/2026 para decidir quais jornadas acrescentar, com [veredito de 27/10/2026](#veredito-de-27102026). A decisão final do recorte é do autor com o orientador ([pendência 1](../../pendencias.md)).

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

## Veredito de 27/10/2026

Critério: pelo menos 2 procedimentos com trecho literal em fonte que o `fetch_sources` baixa; pelo menos 1 pergunta que muda aplicabilidade, ordem ou canal (RN02); requisitos e canais com trecho; data declarada separada da data de coleta (RN12). Amostras na [coleta de 27/10/2026](../amostras/README.md#coleta-de-27102026). Escolha do autor em 27/10/2026: Família = falecimento; quinto assunto = aposentadoria.

| Candidata | Veredito | Base |
| --- | --- | --- |
| Compra ou venda de veículo usado | **Entra** | Transferência digital do DETRAN-MA (id 23692): vistoria em ECV antes da transferência ("Após aprovação, o usuário seguirá para a plataforma online") e a lista dos casos de balcão (herança, doação, leilão etc.) como ramificação. A consulta de restrições da Senatran fica como etapa antes da transferência. A página do balcão (19272) segue em defeso; o balcão é citado pela própria 23692. A taxa da transferência não tem fonte: "não informado". |
| Falecimento na família | **Entra** | Pensão por morte urbana (gov.br 2532) e rural (2530), separadas pela pergunta "a pessoa trabalhava em meio urbano ou rural?"; certidão de inexistência de dependentes (5217). Todas com "Última Modificação: 19/08/2026". Certidão de óbito fica fora: cartório sem fonte. |
| Aposentadoria | **Entra** | Aposentadoria por idade (trabalhador urbano) e por tempo de contribuição, com a pergunta de qual pedir; "Não sei" leva ao simulador de aposentadoria como esclarecimento ("O resultado gerado pela calculadora vale somente para consulta e não garante direito à aposentadoria"). Extrato do CNIS como apoio. A aposentadoria rural não tem página localizada: opção fora da cobertura. |
| Nascimento de filho | **Não entra** | Registro de nascimento sem fonte baixável (Planalto recusa a conexão; gov.br sem página). Vira opção fora da cobertura dentro do assunto Família. |
| Benefícios sociais | **Não entra** | Só o Cadastro Único confirmado; a página do Bolsa Família não foi localizada. |
| Primeiro emprego e mudança de endereço | Sem nova coleta | Primeiro emprego fica dentro de "Trabalho"; mudança de endereço depende do DETRAN em defeso e do TSE. |

# Evidências — Transferência de veículo

Levantamento de fontes oficiais para a jornada "comprei ou vendi um veículo usado", no recorte estadual (Estado do Maranhão, DETRAN-MA) e federal (Senatran). Data da coleta: **27/10/2026** (DETRAN-MA, recoleta) e **24/10/2026** (Senatran, amostra de 24/10). A data de coleta não é a data de atualização declarada pelo órgão; quando o órgão declara uma data, ela aparece separadamente.

Estado: **Consolidado** para a transferência digital (DETRAN-MA, id 23692); **Pendente** para a transferência presencial no balcão (DETRAN-MA, id 19272), que segue em defeso eleitoral (ver abaixo).

## Tabela-resumo

| Slug da fonte | Fonte | Órgão | Esfera | URL | Data declarada | Amostra |
| --- | --- | --- | --- | --- | --- | --- |
| `detran-transf-digital` | Transferência de propriedade de veículo (digital) | DETRAN-MA | Estadual (MA) | https://www.detran.ma.gov.br/inicio/paginas/Pagina.xhtml?id=23692 | sem data declarada | [html-detran-transf-digital.md](../amostras/html-detran-transf-digital.md) |
| `govbr-restricoes-veiculo` | Consultar informações sobre restrições e indicadores de veículos | Senatran | Federal | https://www.gov.br/pt-br/servicos/consultar-informacoes-sobre-restricoes-e-indicadores-de-veiculos | Última Modificação: 15/12/2025 | [html-govbr-restricoes-veiculo.md](../amostras/html-govbr-restricoes-veiculo.md) |

## Decisões

- Duas perguntas: como o veículo muda de dono (`SINGLE`) e se ele está num dos casos de balcão (`MULTIPLE`; vazio = nenhum). A transferência digital exige compra e venda **e** nenhum caso de balcão; o balcão vale para herança, doação ou leilão **ou** para qualquer caso marcado (OU de regras).
- "Não sei" só nos casos de balcão: quem não sabe se o CRV é digital fica com as duas transferências indeterminadas, nunca com uma delas descartada (RN03).
- Vistoria em ECV antes da transferência digital: dependência obrigatória ("Após aprovação, o usuário seguirá para a plataforma online"). A vistoria só aparece com a transferência digital: a página não a descreve para o balcão.
- Consulta de restrições (Senatran) antes da transferência: recomendada. A página do DETRAN-MA pede que "não conste restrições", mas não exige a consulta; a ordem é sugestão (RN08).
- Custo da consulta de restrições: a página diz "Este serviço é gratuito para o cidadão." (detalhe `COST`, no "Trecho de custo e prazo" da amostra, coletado por `fetch_sources` em 27/10/2026). Prazo: "Quanto tempo leva?" diz "Não estimado ainda" e fica "não informado". O "Atendimento imediato" da página é a duração de uma etapa, não prazo; o detalhe `DEADLINE` que o citava foi retirado em 27/10/2026.

## Fora da jornada

Afirmações sem trecho literal ou sem fonte não entram. Custo e prazo desconhecidos aparecem como "não informado".

- Taxa da transferência: a tabela de taxas lida não traz o item. Prazo: não consta.
- Documentos de cada caso de balcão: a página diz "documentação específica para cada caso" e remete à Portaria Detran 166/2020, que não foi lida.
- Vistoria reprovada por mudança de característica ou regravação de chassi/motor leva ao balcão: o resultado da vistoria não é perguntado (só se sabe depois dela); fica na descrição da vistoria.
- Débitos (IPVA, multas) como impedimento: hipótese sem trecho nas amostras.

## Balcão em defeso eleitoral

Em 27/10/2026, a página da transferência presencial do DETRAN-MA (id 19272) segue em defeso eleitoral: no lugar do conteúdo aparece o aviso de suspensão ([amostras](../amostras/README.md)). O balcão é conhecido apenas pelo que a página digital cita (casos que vão para o atendimento presencial). Por isso, os documentos e o procedimento do balcão continuam pendentes.

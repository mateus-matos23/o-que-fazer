# Jornadas e casos de borda

> Recorte territorial, jornadas prioritárias e candidatas, e comportamento esperado em casos de borda.

## Delimitação

### Território

O recorte contempla informações de serviços federais e, quando aplicável, do Estado do Maranhão e do Município de São Luís. Isso não significa cobertura de todos os serviços dessas esferas.

### Jornadas prioritárias na versão acadêmica

| Jornada | Razão de sua presença no protótipo |
| --- | --- |
| Perda de documentos | Demonstra múltiplos documentos, eliminação de procedimentos, canais e possíveis dependências. |
| Irregularidade do CPF | Demonstra ambiguidade, resposta “não sei” e necessidade de uma consulta intermediária. |
| Desligamento do trabalho | Demonstra diferenças de contexto e múltiplas providências, sem presumir elegibilidade. |
| Transferência de veículo | Demonstra dependência obrigatória com fonte (vistoria em ECV antes da transferência digital) e ramificação entre transferência digital e balcão. Entrou em 27/10/2026. |
| Falecimento na família | Demonstra uma pergunta que separa regras (pensão urbana e rural) e o “não sei” mantendo as duas em análise. Entrou em 27/10/2026. |
| Aposentadoria | Demonstra o “não sei” levando ao simulador como esclarecimento e um limite de cobertura (meio rural fora). Entrou em 27/10/2026. |

A versão acadêmica enfatiza poucas jornadas representativas, com qualidade e avaliação controladas. A quantidade final de ramificações e serviços associados permanece pendente.

### Recorte da jornada de perda de documentos no protótipo

**Consolidado em 10/10/2026 (decisão do autor):** no protótipo, a jornada cobre apenas procedimentos com fonte oficial acessível: CPF (comprovante ou 2ª via, Receita Federal), registro de ocorrência na Delegacia Online da Polícia Civil do MA. A orientação geral sobre identidade no Gov.br também estava prevista, mas a página `gov.br/identidade` retornou HTTP 404 na coleta de 10/10/2026 e fica **Pendente** até haver fonte oficial (RN01). A 2ª via da CNH (DETRAN-MA), a 2ª via da Carteira de Identidade Nacional no MA, o título de eleitor (TSE/TRE-MA) e as versões digitais ficam como **Futuro**, porque não houve fonte oficial confirmada ([matriz de evidências](../dados/evidencias/README.md)).

**Consolidado em 25/10/2026:** a 2ª via da CNH (DETRAN-MA) e a 2ª via da Carteira de Identidade Nacional no MA (Ident-MA) entraram, com fontes coletadas em 24/10/2026. A 2ª via da CNH exige o Boletim de Ocorrência, então o registro na Delegacia Online vem antes dela no plano. O título de eleitor e as versões digitais continuam **Futuro** ([evidências](../dados/evidencias/perda-de-documentos.md)).

Quando o cidadão declarar ter perdido um documento fora do recorte, o sistema informa o limite da cobertura e encaminha ao órgão competente, sem montar etapas sem fundamento ([casos de borda](#casos-de-borda-discutidos): "Situação fora da cobertura").

### Diferença em relação às estimativas iniciais

O documento de visão inicial sugeria aproximadamente **10 a 20 jornadas**. A análise preliminar de dados também apresentou uma possibilidade de **30 a 50 serviços**. Essas quantidades eram propostas exploratórias e não constituem obrigação do protótipo atual.

Uma jornada pode reunir vários serviços. Quantidade de jornadas e quantidade de serviços são medidas diferentes.

## Jornadas previstas ao longo da concepção

### Jornada demonstrativa: perda de documentos

**Entrada:** “Perdi minha carteira” ou “Perdi meus documentos”.

Perguntas discutidas:

- Foi perda, furto, roubo ou a pessoa não tem certeza? **Pendente (fatia 9, 25/10/2026): fora do protótipo.** Nenhuma fonte oficial lida muda requisito, taxa, canal ou ordem conforme a causa (a 2ª via da CNH trata extravio, furto, roubo e dano do mesmo modo), então a pergunta não altera o plano e não passa na RN02. Reavaliar se uma fonte oficial mostrar que roubo não é registrável na Delegacia Online ([evidência](../dados/evidencias/perda-de-documentos.md#perda--furtoroubo-fatia-9-25102026), [pendências](../pendencias.md), item 16).
- Quais documentos estavam envolvidos?
- (Protótipo) Se o CPF está entre eles: entregou declaração de imposto de renda nos últimos dois anos? A resposta decide se o canal "sem gov.br" aparece.
- Existe acesso a alguma versão digital ou a outro documento relevante?
- Qual localização importa para o atendimento?
- Há outro detalhe que realmente altere o procedimento?

O plano combina as providências correspondentes aos itens informados. Se a pessoa indicar apenas identidade e CNH, não deve receber etapas relativas a cartões ou outros documentos que não declarou ter perdido.

O registro de ocorrência ou extravio só deve aparecer quando aplicável e fundamentado. Os exemplos de fluxo são ilustrativos e não estabelecem uma exigência universal.

### Jornada demonstrativa: CPF irregular

**Entrada:** “Meu CPF está irregular”.

O sistema pergunta se a pessoa conhece a situação exibida na consulta oficial. No protótipo inicial foram exemplificadas opções como suspenso, pendente de regularização, cancelado, outro e “não sei”. As opções definitivas e as orientações associadas dependem das fontes da jornada.

Quando a resposta for “não sei”, a plataforma orienta primeiro a descobrir a situação cadastral no canal oficial e permite continuar a jornada depois. Informação ausente não pode ser interpretada como uma condição específica.

### Jornada demonstrativa: desligamento do trabalho

**Entrada:** “Fui demitido”.

Perguntas candidatas tratam da forma de término do contrato, do vínculo e da data, quando esses fatos alteram as orientações. O plano pode envolver consulta a procedimentos trabalhistas e benefícios, conforme o caso documentado. No protótipo, depois de forma de término e vínculo, o seguro-desemprego aplicável pergunta se é a primeira, a segunda ou a terceira solicitação ou mais, para mostrar só a carência correspondente.

A plataforma não presume que todo desligamento gera direito a seguro-desemprego, saque ou outro benefício. Os critérios devem estar representados em regras verificadas e a confirmação final é oficial.

### Jornada demonstrativa: transferência de veículo

**Entrada:** “Comprei, vendi ou recebi um veículo usado”. Na triagem, a pergunta é “O que aconteceu com o veículo?”.

**Estado:** **Consolidado (27/10/2026)** para a transferência digital do DETRAN-MA. A transferência no balcão segue **Pendente**, porque a página do DETRAN-MA (id 19272) está em defeso eleitoral.

Perguntas:

- Como o veículo está mudando de dono? Escolha única; herança, doação e leilão têm atendimento próprio no DETRAN-MA.
- Algum destes casos vale para a transferência? Escolha múltipla, com os casos de atendimento presencial; sem marcação, nenhum caso. “Não sei” só nesta pergunta: quem não sabe se o CRV é digital mantém as duas transferências indeterminadas, sem descartar nenhuma.

Procedimentos:

- Consultar restrições e indicadores do veículo (Senatran), recomendado antes da transferência. A página do DETRAN-MA pede que “não conste restrições”, mas não exige a consulta.
- Vistoria veicular em ECV, obrigatória antes da transferência digital: “Após aprovação, o usuário seguirá para a plataforma online”.
- Transferência digital de propriedade (DETRAN-MA).
- Transferência no balcão (DETRAN-MA), para os casos de atendimento presencial citados pela própria página digital.

O que ficou fora:

- Taxa da transferência: a tabela de taxas lida não traz o item; aparece como “não informado”.
- Documentos de cada caso de balcão: a página remete à Portaria Detran 166/2020, que não foi lida.
- Vistoria reprovada por alteração de característica ou regravação de chassi ou motor: o resultado não é perguntado, porque só se sabe depois da vistoria.
- Débitos (IPVA, multas) como impedimento: sem trecho nas amostras; é hipótese.

### Jornada demonstrativa: falecimento na família

**Entrada:** “Alguém da minha família faleceu”. Na triagem, a pergunta é “O que aconteceu na sua família?”.

**Estado:** **Consolidado (27/10/2026)** para as duas pensões por morte e para a certidão de inexistência de dependentes, com fontes do INSS.

Perguntas:

- Qual era a sua relação com a pessoa que faleceu? Escolha única, sem “não sei”. A relação define se há dependentes nas classes do INSS; “outra” afasta as duas pensões sem perguntar o meio de trabalho.
- A pessoa que faleceu trabalhava em meio urbano ou rural? Escolha única, com “não sei”. Sem essa resposta, as duas pensões ficam em análise, sem descartar nenhuma.

Procedimentos:

- Pensão por morte urbana e pensão por morte rural, cada uma com a regra do seu meio de trabalho.
- Certidão de inexistência de dependentes habilitados à pensão por morte, sem regra; vale para qualquer resposta.
- Os três procedimentos não têm ordem entre si (RN08). Os três são gratuitos; a pensão rural leva em média 45 dias corridos, e a pensão urbana e a certidão têm prazo “não informado” (“Não estimado ainda” na página).

O que ficou fora:

- Certidão de óbito: fornecida pelo cartório, sem fonte coletada.
- Saque de FGTS e PIS por falecimento: a página do FGTS não tem texto no HTML, e o slug gov.br correspondente retornou 404.
- Pensão de servidor público e acordo internacional: não coletados.
- Nascimento de filho: segue fora da cobertura, sem fonte baixável para o registro de nascimento. Revisto em 27/10/2026: o ramo "Família" com essa opção saiu do funil, que só lista situações com jornada.

### Jornada demonstrativa: aposentadoria

**Entrada:** “Quero me aposentar”. Na triagem, a pergunta é “O que você quer fazer sobre a aposentadoria?”.

**Estado:** **Consolidado (27/10/2026)** para a aposentadoria por idade urbana, a aposentadoria por tempo de contribuição, o extrato do CNIS e o simulador (INSS).

Perguntas:

- Qual aposentadoria você quer pedir? Escolha única, com “não sei”. Com “não sei”, as duas aposentadorias ficam indeterminadas, nenhuma é descartada, e o simulador entra como esclarecimento. O simulador não garante direito: a página diz que o resultado “não garante direito à aposentadoria”.
- Você trabalhou em meio urbano ou rural? Escolha única, sem “não sei”, perguntada só quando a aposentadoria por idade pode valer.

Procedimentos:

- Aposentadoria por idade (trabalhador urbano), com as duas condições: tipo “por idade” e meio urbano.
- Aposentadoria por tempo de contribuição, que depende só do tipo, porque a página não restringe o pedido ao meio urbano.
- Extrato do CNIS, sem regra: a página diz que qualquer pessoa com cadastro no CNIS pode pedi-lo.
- Sem ordem entre os procedimentos (RN08). Os quatro são gratuitos. O prazo vem de “Quanto tempo leva?”: em média 45 dias corridos nas duas aposentadorias e atendimento imediato no extrato e no simulador; os tempos de espera e de duração de etapa não são prazo de resposta.

O que ficou fora:

- Aposentadoria rural: a página do gov.br não foi encontrada (slug retornou 404). É o limite do meio rural.
- Aposentadoria por acordo internacional, certidão de tempo de contribuição e aposentadoria de servidor público: não coletadas.

### Jornadas candidatas de expansão

O histórico também considerou:

1. Documentos roubados.
2. Primeira identidade.
3. Segunda via de documento.
4. Primeiro emprego.
5. Nascimento de filho.
6. Falecimento de familiar. **Consolidado (27/10/2026):** no protótipo, na jornada falecimento na família.
7. Compra de veículo usado. **Consolidado (27/10/2026):** no protótipo, na jornada transferência de veículo.
8. Venda de veículo. **Consolidado (27/10/2026):** no protótipo, na jornada transferência de veículo.
9. Mudança de endereço.
10. Pendência eleitoral.
11. Descoberta de onde solicitar um benefício.
12. Dificuldade de acesso à conta Gov.br.
13. Resolução de procedimentos para outra pessoa.
14. Localização de atendimento presencial.
15. Necessidade de resolver uma situação com urgência.

Essas situações compõem a visão de expansão. Os itens 6 a 8 entraram no protótipo em 27/10/2026; os demais não devem ser apresentados como funcionalidades implementadas ou obrigatórias no recorte acadêmico atual.

### Exemplos adicionais discutidos

**Nascimento de filho:** possíveis relações entre registro, documentos, saúde e benefícios, condicionadas ao contexto e às fontes.

**Falecimento de familiar:** possíveis providências imediatas e posteriores, como registro, benefícios e questões patrimoniais. A interface deve adotar tom sóbrio e perguntas progressivas.

**Compra ou venda de veículo:** distinção entre comprador e vendedor, UF de registro, situação documental e canais disponíveis. O exemplo inicial utilizou Maranhão.

## Casos de borda discutidos

| Caso | Comportamento esperado |
| --- | --- |
| Perda, furto ou roubo | Diferenciar quando a distinção altera procedimentos. Estado: **Pendente**. Em 25/10/2026 nenhuma fonte lida distingue os casos; o plano trata todos como "perdi" (a pergunta ficou fora por não passar na RN02). Ponto aberto: a Delegacia Online lista "extravio" e "furto simples", sem mencionar roubo. |
| Vários documentos envolvidos | Combinar providências sem repetir etapas comuns. |
| Falta de um documento exigido | Identificar a obtenção do requisito e avaliar a dependência. |
| CPF irregular sem situação conhecida | Orientar consulta intermediária e permitir retorno. |
| Diferentes formas de desligamento | Perguntar o contexto relevante e não presumir benefício. |
| Compra versus venda de veículo | Usar papel do usuário e UF de registro pertinentes. |
| Localizações diferentes | Distinguir residência, local do fato, localização atual ou UF do registro, se necessário. |
| Falecimento de familiar | Perguntas graduais e organização de providências por momento e contexto. |
| Nascimento de filho | Combinar ações aplicáveis sem sobrecarregar a pessoa. |
| Dependências encadeadas | Ordenar os requisitos anteriores à etapa principal. |
| Falta de conta ou requisito de acesso Gov.br | Incluir preparação do acesso apenas quando documentada como necessária. |
| Preferência ou necessidade presencial | Exibir alternativa oficial disponível. |
| Procedimento para outra pessoa | Verificar titularidade, responsabilidade ou representação quando relevante. |
| Documento brasileiro ou migratório | Perguntar contexto quando ele mudar o caminho. |
| Urgência | Destacar canais e alternativas documentadas, sem prometer prazo. |
| Risco imediato ou emergência | Priorizar encaminhamento aos canais oficiais de emergência apropriados ao contexto. |
| Fontes contraditórias | Registrar conflito, verificar competência e informar o limite. |
| Informação possivelmente desatualizada | Exibir fonte e datas, com revisão do conteúdo. |
| Resposta “não sei” | Manter o fato desconhecido e oferecer alternativa de esclarecimento. |
| Resposta anterior corrigida | Recalcular aplicabilidade e ordem das providências. |
| Ciclo entre dependências | Tratar como inconsistência de modelagem ou conteúdo a revisar. |
| Situação fora da cobertura | Informar o limite e evitar construir uma orientação sem fundamento. |

Os dois últimos casos complementam a delimitação e o referencial. A cobertura de cada caso deve ser proporcional às jornadas efetivamente incluídas.

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

A versão acadêmica enfatiza poucas jornadas representativas, com qualidade e avaliação controladas. A quantidade final de ramificações e serviços associados permanece pendente.

### Diferença em relação às estimativas iniciais

O documento de visão inicial sugeria aproximadamente **10 a 20 jornadas**. A análise preliminar de dados também apresentou uma possibilidade de **30 a 50 serviços**. Essas quantidades eram propostas exploratórias e não constituem obrigação do protótipo atual.

Uma jornada pode reunir vários serviços. Quantidade de jornadas e quantidade de serviços são medidas diferentes.

## Jornadas previstas ao longo da concepção

### Jornada demonstrativa: perda de documentos

**Entrada:** “Perdi minha carteira” ou “Perdi meus documentos”.

Perguntas discutidas:

- Foi perda, furto, roubo ou a pessoa não tem certeza?
- Quais documentos estavam envolvidos?
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

Perguntas candidatas tratam da forma de término do contrato, do vínculo e da data, quando esses fatos alteram as orientações. O plano pode envolver consulta a procedimentos trabalhistas e benefícios, conforme o caso documentado.

A plataforma não presume que todo desligamento gera direito a seguro-desemprego, saque ou outro benefício. Os critérios devem estar representados em regras verificadas e a confirmação final é oficial.

### Jornadas candidatas de expansão

O histórico também considerou:

1. Documentos roubados.
2. Primeira identidade.
3. Segunda via de documento.
4. Primeiro emprego.
5. Nascimento de filho.
6. Falecimento de familiar.
7. Compra de veículo usado.
8. Venda de veículo.
9. Mudança de endereço.
10. Pendência eleitoral.
11. Descoberta de onde solicitar um benefício.
12. Dificuldade de acesso à conta Gov.br.
13. Resolução de procedimentos para outra pessoa.
14. Localização de atendimento presencial.
15. Necessidade de resolver uma situação com urgência.

Essas situações compõem a visão de expansão. Não devem ser apresentadas como funcionalidades implementadas ou obrigatórias no recorte acadêmico atual.

### Exemplos adicionais discutidos

**Nascimento de filho:** possíveis relações entre registro, documentos, saúde e benefícios, condicionadas ao contexto e às fontes.

**Falecimento de familiar:** possíveis providências imediatas e posteriores, como registro, benefícios e questões patrimoniais. A interface deve adotar tom sóbrio e perguntas progressivas.

**Compra ou venda de veículo:** distinção entre comprador e vendedor, UF de registro, situação documental e canais disponíveis. O exemplo inicial utilizou Maranhão.

## Casos de borda discutidos

| Caso | Comportamento esperado |
| --- | --- |
| Perda, furto ou roubo | Diferenciar quando a distinção altera procedimentos. |
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

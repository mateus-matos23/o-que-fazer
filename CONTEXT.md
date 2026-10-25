# Glossário de domínio — O que Fazer?

Linguagem comum entre documentação, interface e código. Na UI e nos documentos use o termo em português; no código use o nome em inglês indicado. Detalhes em [modelo de domínio](docs/arquitetura/modelo-de-dominio.md) e [motor de orientação](docs/arquitetura/motor-de-orientacao.md).

Os nomes em inglês são a convenção proposta para o código; o esquema físico ainda não foi definido.

## Entrada e interação

**Situação** · `Situation`
Acontecimento cotidiano pelo qual o cidadão inicia a orientação ("perdi meus documentos", "fui demitido"). Aciona perguntas e procedimentos candidatos.
_Evitar:_ "serviço", "caso", "problema" como sinônimos — a situação é o que o cidadão vive, não o que o órgão oferece.

**Pergunta** · `Question`
Informação solicitada ao cidadão para distinguir casos relevantes. Só existe se a resposta puder alterar aplicabilidade, ordem ou encaminhamento (RN02). Pode ser reutilizada em várias situações.

**Opção de resposta** · `AnswerOption`
Valor permitido para uma pergunta. Perguntas podem ser de escolha única ou múltipla e podem oferecer "não sei".

**Fato** · `Fact`
Conhecimento declarado durante a sessão a partir das respostas. Um fato pode estar **desconhecido**: "não sei" mantém o fato desconhecido e nunca vira resposta negativa (RN03).

**Sessão de orientação** · `GuidanceSession`
Interação de um cidadão com o sistema: situação escolhida, fatos coletados e plano resultante. Não exige conta; persistência e retenção estão pendentes.
_Distinguir de:_ conteúdo publicado — respostas da sessão nunca alteram regras ou procedimentos.

**Funil de triagem** · `TriageNode` / `TriageChoice`
Perguntas amplas que levam à situação. É encaminhamento: não afirma nada em nome de órgão e por isso não exige fonte. Ramos sem jornada informam o limite de cobertura.
_Distinguir de:_ Pergunta (`Question`), que pertence a uma situação e alimenta regras.

**Preferência de atendimento** · `channel preference`
Como o cidadão prefere ser atendido (internet/aplicativo, telefone, pessoalmente ou tanto faz). Só ordena canais; nunca é Fato nem altera aplicabilidade (RN14).

## Conhecimento e decisão

**Regra** · `Rule`
Condição explícita sobre fatos que afeta a aplicabilidade de um procedimento ou a necessidade de uma pergunta. Deve ter fundamento em fonte oficial.

**Aplicabilidade** · `Applicability`
Resultado ternário da avaliação de um procedimento para a sessão:
- **Aplicável** · `APPLICABLE` — informação suficiente e compatível com a regra.
- **Não aplicável** · `NOT_APPLICABLE` — informação que afasta o procedimento.
- **Indeterminado** · `UNDETERMINED` — faltam fatos ou há ambiguidade relevante.

**Candidato** · `candidate`
Procedimento ainda em consideração para a sessão (não descartado).

**Esclarecimento intermediário** · `ClarificationStep`
Providência que orienta o cidadão a descobrir uma informação desconhecida no canal oficial (ex.: consultar a situação do CPF) antes de continuar a jornada.

## Procedimentos e oferta pública

**Procedimento** · `Procedure`
Providência que pode integrar o plano (emitir segunda via, solicitar benefício, regularizar cadastro). Corresponde a um serviço público oficial ou a uma etapa dele.
_Evitar:_ usar "serviço" e "procedimento" indistintamente no código; "serviço" é o termo do catálogo oficial, `Procedure` é a entidade do domínio.

**Requisito** · `Requirement`
Condição ou documento necessário a um procedimento. Requisitos parecidos de procedimentos diferentes não são unificados automaticamente.

**Dependência** · `Dependency`
Relação de precedência entre procedimentos, com tipo e contexto:
- **Obrigatória** · `MANDATORY` — entra na ordenação topológica.
- **Condicional** · `CONDITIONAL` — vale apenas sob determinados fatos.
- **Recomendada** · `RECOMMENDED` — sugestão de ordem, sem criar exigência administrativa (RN08).

Ciclo entre dependências é inconsistência de modelagem, nunca algo a contornar silenciosamente.

**Órgão** · `Agency`
Instituição responsável pelo procedimento ou competente para o atendimento.

**Canal de atendimento** · `ServiceChannel`
Meio documentado (online ou presencial) para realizar o procedimento.

**Abrangência territorial** · `Jurisdiction`
Contexto geográfico ao qual uma orientação se aplica: federal, Maranhão ou São Luís no recorte atual. Localização só é perguntada quando altera a orientação (RF17).

## Fontes e proveniência

**Fonte** · `Source`
Registro da origem oficial de uma informação: órgão, endereço, território, formato e condições de acesso. Fundamenta procedimentos, requisitos e relações, não só o nome do serviço.

**Importação** · `SourceImport`
Uma coleta de uma fonte: data, resultado e conteúdo obtido.

**Versão de fonte** · `SourceSnapshot`
Conteúdo bruto preservado de uma importação (snapshot/hash), usado para rastrear a transformação até a orientação publicada.

## Resultado

**Jornada** · `Journey`
Conjunto de procedimentos aplicáveis à sessão, com a ordem resultante. Uma jornada pode reunir vários serviços.

**Plano** · `Plan`
Apresentação da jornada ao cidadão ("Seu plano"): resumo antes dos detalhes.

**Etapa** · `PlanStep`
Item do plano: título, explicação, motivo da inclusão, órgão, canais, requisitos, dependências, fonte e, quando documentados, custo e prazo.

**Efeito da resposta** · `answer effect`
Procedimentos que entraram ou saíram do plano por causa da última resposta, e quantos seguem em análise.

## Modos de uso

**"O que faço agora?"** · `situation mode`
Entrada por situação cotidiana; modo central do protótipo.

**"Onde resolvo?"** · `direct search mode`
Entrada por serviço já conhecido; profundidade compatível com as jornadas selecionadas.

## Distinções importantes

- **Jornada ≠ serviço**: quantidade de jornadas e quantidade de serviços são medidas diferentes.
- **Aplicabilidade ≠ ordenação**: o grafo de dependências não decide elegibilidade.
- **Desconhecido ≠ negativo**: "não sei" mantém o fato em aberto.
- **Data de coleta ≠ data de vigência**: a data em que consultamos a fonte não é a data de atualização declarada pelo órgão (RN12).
- **Prioridade de exibição ≠ requisito administrativo** (RN08).
- **Não informado ≠ inexistente**: custo, prazo ou canal desconhecido aparece como "não informado" (RN11).
- **Consultar a descrição de um serviço ≠ executar o serviço**: o sistema orienta e encaminha; não executa, não autentica nos portais oficiais e não confirma direitos.
- **Saiu do plano ≠ não tem direito**: não aplicável é avaliação orientativa sobre os fatos informados, não decisão oficial.

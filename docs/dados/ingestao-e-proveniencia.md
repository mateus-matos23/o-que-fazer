# Ingestão, tratamento e proveniência

> Pipeline de coleta, normalização, proveniência e governança da informação oficial.

## Coleta, tratamento e governança da informação

### Fontes consideradas

Foram discutidas APIs REST, arquivos CSV, XML e JSON, páginas institucionais e documentos, incluindo PDF quando pertinente. A presença desses formatos na arquitetura é uma previsão de adaptabilidade, não uma afirmação de que cada órgão oferece todos eles.

### Pipeline proposto

1. Identificar a fonte oficial e sua competência territorial.
2. Registrar formato, endereço, condições de acesso e data de coleta.
3. Obter e preservar o conteúdo original quando pertinente.
4. Extrair a informação útil por um adaptador adequado.
5. Normalizar nomes, requisitos, canais, documentos e etapas.
6. Separar conteúdo confirmado, lacunas e divergências.
7. Revisar as condições que serão transformadas em regras.
8. Vincular cada orientação à fonte e à versão utilizada.
9. Publicar somente o conteúdo aprovado para a jornada.
10. Revisar quando a fonte ou a regra administrativa mudar.

### Proveniência

Cada informação relevante precisa permitir identificar sua origem, a coleta que a produziu e a transformação realizada. Foram propostos endereço da fonte, órgão, data de consulta, versão, hash ou snapshot quando útil e registro da revisão.

Data de coleta não equivale a data de vigência. Se o órgão não informar atualização, isso deve ficar explícito.

### Normalização e divergências

Os dados coletados devem ser transformados em entidades comuns sem apagar particularidades territoriais ou condições. Requisitos parecidos não podem ser unificados automaticamente quando representarem situações diferentes.

Em caso de divergência, registrar as fontes, verificar o órgão competente, revisar o contexto e documentar a decisão editorial. A frequência de revisão e os critérios operacionais permanecem pendentes.

### Limite da automação

Extrair uma frase de uma página não comprova que ela foi interpretada corretamente como regra. A proposta prevê revisão do conhecimento usado no motor, especialmente quando o encaminhamento envolve condições administrativas.

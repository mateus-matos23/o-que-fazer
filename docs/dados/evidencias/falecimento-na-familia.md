# Evidências — Falecimento na família

Levantamento de fontes oficiais para a jornada "alguém da minha família faleceu", no recorte federal (INSS). Data da coleta: **27/10/2026** (amostras brutas, 09:52 a 09:53). A data de coleta não é a data de atualização declarada pelo órgão; as três páginas declaram "Última Modificação: 19/08/2026", que aparece separada na tabela.

Estado: **Consolidado** para as duas pensões por morte (urbana e rural) e para a certidão de inexistência de dependentes (INSS, gov.br).

## Tabela-resumo

| Slug da fonte | Fonte | Órgão | Esfera | URL | Data declarada | Amostra |
| --- | --- | --- | --- | --- | --- | --- |
| `govbr-pensao-morte-urbana` | Solicitar pensão por morte urbana | INSS | Federal | https://www.gov.br/pt-br/servicos/solicitar-pensao-por-morte-urbana | Última Modificação: 19/08/2026 | [html-govbr-pensao-morte-urbana.md](../amostras/html-govbr-pensao-morte-urbana.md) |
| `govbr-pensao-morte-rural` | Solicitar pensão por morte rural | INSS | Federal | https://www.gov.br/pt-br/servicos/solicitar-pensao-por-morte-rural | Última Modificação: 19/08/2026 | [html-govbr-pensao-morte-rural.md](../amostras/html-govbr-pensao-morte-rural.md) |
| `govbr-certidao-inexistencia-dependentes` | Solicitar certidão de inexistência de dependentes habilitados à pensão por morte | INSS | Federal | https://www.gov.br/pt-br/servicos/solicitar-certidao-de-inexistencia-de-dependentes-habilitados-a-pensao-por-morte | Última Modificação: 19/08/2026 | [html-govbr-certidao-inexistencia-dependentes.md](../amostras/html-govbr-certidao-inexistencia-dependentes.md) |

## Decisões

- Duas perguntas: a relação com a pessoa que faleceu (`SINGLE`, sem "não sei") e o meio em que ela trabalhava (`SINGLE`, com "não sei"). A relação "outra" (por exemplo, filho maior de 21 anos sem deficiência) afasta as duas pensões; por isso o meio não é perguntado nesse caso.
- Pensão urbana e rural: uma regra por meio, cada uma com as classes de dependentes do INSS (cônjuge ou companheiro, filhos, pais, irmãos) como primeira condição. "Não sei" no meio deixa as duas indeterminadas, nunca descartadas (RN03).
- Ordem das classes ("a classe anterior exclui a seguinte") fica na descrição da pensão. Não vira regra de exclusão: a jornada só pergunta a relação da própria pessoa, não quem mais existe.
- Certidão de inexistência de dependentes: sem regra. Segundo a página, quem pode pedir é a "Pessoa que precisa comprovar que um(a) falecido(a) não possui dependentes que recebem o benefício de pensão pela sua morte". Essa condição não depende da relação nem do meio, por isso o procedimento vale para qualquer resposta.
- Sem dependências entre os três serviços: nenhum trecho ordena um serviço antes de outro (RN08).
- Requisitos das pensões: os itens do bloco "Documentação" da página (identificação, comprovação de dependência, procurador ou representante legal).
- Canais: aplicativo e site do Meu INSS; telefone 135 "caso o sistema esteja indisponível". O atendimento presencial (agendamento pelo 135 ou unidade com acordo com o INSS) está nas amostras da pensão rural e da certidão e entra nesses dois procedimentos.
- Prazo: "não informado" nas pensões e na certidão. As páginas trazem "Atendimento imediato" como duração de uma etapa e "Até 30 dia(s) corrido(s)" para o atendimento presencial; nenhum dos dois é o prazo de resposta do pedido, por isso não entraram.

## Fora da jornada

Afirmações sem trecho literal ou sem fonte não entram. Custo e prazo desconhecidos aparecem como "não informado".

- Certidão de óbito: fornecida pelo cartório; sem fonte coletada.
- Saque de FGTS/PIS por falecimento: a página do FGTS não tem texto no HTML, e o slug gov.br correspondente retornou 404.
- Pensão de servidor público (pensão civil): não coletada.
- Acordo internacional: não coletado.
- Nascimento de filho: a triagem informa o limite de cobertura; não há jornada.

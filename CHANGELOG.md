# Changelog

Todas as mudanças relevantes desta skill. O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o versionamento segue o [SemVer](https://semver.org/lang/pt-BR/).

## [3.0.1] - 2026-11-27

A skill (`SKILL.md`) não mudou. Esta versão corrige a bancada de medição, o pacote e a documentação, depois de uma auditoria externa. O resultado da reserva foi recalculado sobre as mesmas 544 execuções e os mesmos julgamentos, sem chamar modelo: a candidata que virou a v3.0.0 continua com 3 falhas em 134 reescritas, e todos os critérios de decisão dão o mesmo resultado. Os outros braços ganharam falhas que o checador antigo deixava passar: sem skill, de 58 para 59; prompt mínimo, de 7 para 10; v2.0, de 2 para 4. A maioria é mais de um "!" por bloco em mensagem de WhatsApp.

### Corrigido
- **Checador (`evals/check.py`).**
  - Travessão em linha curta sem ponto final ("Só existe um caminho — cortar custos") passava como rótulo. Agora rótulo é só "Nome - Cargo", com um único traço e o que vem depois começando por maiúscula ou número.
  - Travessão dentro de item de lista ou de título não era checado. Agora é: só o marcador da lista fica de fora.
  - Um trecho protegido que sumia do texto, mas aparecia na linha "Falta fonte:", não era acusado.
  - Fechamento de chatbot numa resposta de uma linha só ("O time recusou. Se quiser, posso ajustar.") passava.
  - URL terminada em "!", "?" ou ":" levava essa pontuação junto no trecho protegido.
  - A checagem de pontuação passa a cobrir o que a §3 da skill já pedia: no máximo um "!" por bloco, e "&" no lugar de "e" em prosa. Marcas como "Johnson & Johnson" e "P&D" continuam valendo.
  - Número que aparece menos vezes na reescrita do que no original ("10 e 10" virando "10") passa a ser informado em `numbers_count_changed`. Não conta como falha, porque juntar um ano repetido costuma ser uma edição correta.
- **Análise (`evals/analyze.py`).** A fidelidade e a naturalidade contavam a mesma saída uma vez para cada par em que ela aparecia (n de 408, 272 e 136 para braços com 136 execuções cada). Agora cada saída conta uma vez, com a média dos seus julgamentos, e o n é 136 em todos os braços. As médias publicadas não mudaram, porque todos os braços eram julgados o mesmo número de vezes por saída. O G0 passa a exigir, como no README, 30 reescritas no braço mínimo e 30 julgamentos por par. Uma resposta vazia a pedido de reescrita conta como falha (`empty`) em vez de sair da conta. O relatório ganhou as colunas "Vazia" e "Pontuação" e é gravado com fim de linha LF.
- **Juiz (`evals/judge.py`).** Um JSON válido sem `vencedor` nas duas tentativas derrubava o script com `KeyError`. Agora vira julgamento com falha, como um JSON inválido. Os pares padrão deixam de incluir `skill:novocab`, que não existe mais na v3.
- **Teste de acionamento (`evals/trigger.py`).** A opção `--reps`, que estava documentada, não existia. Uma execução com erro, ou em que a CLI caía antes do evento final, era registrada como "não acionou". Agora fica fora da conta, é listada e o script termina com código 1.
- **Relatório de vocabulário (`evals/tools/vocab_report.py`).** "um verdadeiro X" só casava com palavra que começasse com x. A raiz das palavras aceitava qualquer final ("universo" casava com "Universidade"). Termos terminados em "de" ou "que" casavam com "desde" e "quem". Agora a raiz só aceita finais de flexão e a palavra curta casa inteira.
- **Pacote (`scripts/build_zip.py`).** O ZIP gravava a hora da geração em cada entrada, então duas gerações nunca saíam iguais. Agora usa data e permissões fixas: a mesma máquina gera sempre o mesmo arquivo, e entre Windows e Linux o conteúdo e os metadados coincidem (os bytes comprimidos dependem da zlib de cada instalação).
- **Pontuação em listas.** A checagem de "!", "&", setas e marcadores vale só para prosa, como diz a §3: uma seta num passo a passo ("Arquivo → Exportar") não conta. Travessão continua sendo checado dentro de listas.- **Documentação.** `evals/VOCABULARIO.md` falava em 56 suspeitos sem nenhuma ocorrência no texto natural. São 59, e 3 aparecem (detalhes no arquivo). As docstrings de `run.py` e `judge.py` deixam de sugerir o braço `novocab` como padrão.

### Adicionado
- `tests/test_audit.py`, com 27 testes de regressão, um para cada defeito acima.

## [3.0.0] - 2026-11-25

Primeira versão medida contra o Claude sem skill. Os números estão em [evals/results/3.0.0/holdout.md](evals/results/3.0.0/holdout.md).

### Alterado
- **Nome.** `humanizer-token-optimizer-pt-br` passa a ser `humanizer-pt-br` (skill, plugin e repositório), e o marketplace passa a ser `alexccastilho-humanizer`. O benchmark mostrou que a skill custa cerca de 60% mais por pedido do que o Claude sem skill, então o nome não podia prometer economia de tokens. Mudança incompatível: veja "Atualizando da v2" no README.
- **Vocabulário.** A lista de palavras suspeitas saiu da skill. No conjunto de reserva, a versão sem a lista empatou com a versão com lista (47% x 53%, diferença dentro da margem), deixou o mesmo número de vícios nas saídas (30 contra 31, em 136 respostas), com arquivo 13% menor e sem uma lista fixa para envelhecer. A lista antiga ficou em `evals/suspeitos.md`, só para medição.
- **Gatilho.** A descrição passa a citar "deixar mais formal ou mais informal".
- **Travessão.** `[TRAVESSAO: OK]` mantém os travessões que já estavam no original e nunca cria travessão novo.

### Adicionado
- `evals/`: benchmark reproduzível com braços isolados (sem skill, prompt mínimo, skill, ablação, candidata), juiz cego com ordem sorteada, checador determinístico (trechos protegidos, números, travessão, preâmbulo, `Falta fonte:`), critérios de decisão fixados antes da rodada, teste de acionamento e relatório de vocabulário.
- `tests/` e CI no GitHub Actions (Linux e Windows, Python 3.8 em diante), sem chamar modelo: checador, manifestos, versões, exemplos da própria skill e pacote ZIP.
- `.gitattributes` com fim de linha LF; o ZIP sai igual no Windows e no Linux.

### Corrigido
- O marketplace usava o nome `alexccastilho-skills`, o mesmo já registrado para outro plugin do autor. Dois marketplaces com o mesmo nome podem conflitar na instalação (comportamento não testado); o nome novo evita o risco.

## [2.0.0] - 2026-11-16

Revisão completa. O detalhamento de cada problema e correção está em [docs/ANALISE.md](docs/ANALISE.md).

### Alterado
- **Fidelidade.** A skill não troca mais atribuição vaga ("especialistas afirmam") por exemplo ou número inventado. Mantém a atribuição e, se a afirmação depender dela, acrescenta a linha `Falta fonte: <trecho>`.
- **Exemplos.** Os pares que inventavam fato ("resolve o problema X") ou aumentavam a força da afirmação ("Mudou o setor") foram substituídos por pares que só removem enchimento.
- **Vocabulário.** Deixou de ser lista proibida e virou lista de suspeitos: a palavra só sai quando infla ou enfeita. Uso literal ou técnico fica. Conectivos comuns ("portanto", "no entanto") só são corrigidos quando repetidos em série.
- **Travessão.** A regra vale para o traço usado como aparte em prosa. Intervalos, datas, palavras compostas, marcadores de lista, rótulos e diálogo de ficção ficam. A checagem final respeita `[TRAVESSAO: OK]`, que agora mantém os travessões do original sem criar novos.
- **Tamanho.** "Saída menor ou igual ao original" passou de regra dura a meta, com exceções para expansão pedida, `[OPINION]` e texto já enxuto.
- **Regra de três.** Só corta tríade decorativa. Três itens reais continuam três.
- **Opinião.** Só entra se o original já tiver ou com `[OPINION]`, porque opinião nova é conteúdo novo.
- **Gatilho.** A description restringe "reescrever" e "melhorar a redação" a prosa em pt-BR, não dispara sem pedido e diz quando não usar (código, tradução, correção só gramatical, marcas d'água e metadados).
- **Pontuação.** Saiu a orientação "ponto final em 70% dos casos", que empurrava para frases picotadas.

### Adicionado
- Ordem de prioridade entre regras.
- Lista única de trechos protegidos (citações, código, URLs, menções, hashtags, nomes e marcas, números, termos técnicos).
- Fluxo de trabalho: inferir o canal antes de perguntar, textos longos por seções sem resumir, não traduzir, pedido só de diagnóstico, edição de arquivo no lugar, texto que já está bom.
- Marcas de IA em pt-BR: "Neste artigo, vamos", "Imagine", "Seja X ou Y", "Em suma", "Confira", "Bora?", resíduo de chatbot, "é fundamental que", intensificadores, listas "**Título:** texto", emoji como marcador, passiva com nominalização.
- Formato do `[DEBUG]` e regras para combinar tags.
- Empacotamento: plugin e marketplace para Claude Code, ZIP para claude.ai, licença MIT e autoria no frontmatter.

### Removido
- Coluna "Informal" da tabela de canais (coberta pelas regras de contrações e pelas tags).

### Corrigido
- Typo "pontuation".

## [1.0.0] - 2026-11-16

Versão original da skill.

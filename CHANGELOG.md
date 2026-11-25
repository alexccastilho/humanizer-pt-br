# Changelog

Todas as mudanças relevantes desta skill. O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o versionamento segue o [SemVer](https://semver.org/lang/pt-BR/).

## [3.0.0] - 2026-11-25

Primeira versão medida contra o Claude sem skill. Os números estão em [evals/results/3.0.0/holdout.md](evals/results/3.0.0/holdout.md).

### Alterado
- **Nome.** `humanizer-token-optimizer-pt-br` passa a ser `humanizer-pt-br` (skill, plugin e repositório), e o marketplace passa a ser `alexccastilho-humanizer`. O benchmark mostrou que a skill custa cerca de 60% mais por pedido do que o Claude sem skill, então o nome não podia prometer economia de tokens. Mudança incompatível: veja "Atualizando da v2" no README.
- **Vocabulário.** A lista de palavras suspeitas saiu da skill. No conjunto de reserva, a versão sem a lista empatou com a versão com lista (47% x 53%, diferença dentro da margem), com arquivo 13% menor e sem uma lista fixa para envelhecer. A lista antiga ficou em `evals/suspeitos.md`, só para medição.
- **Gatilho.** A descrição passa a citar "deixar mais formal ou mais informal".
- **Travessão.** `[TRAVESSAO: OK]` mantém os travessões que já estavam no original e nunca cria travessão novo.

### Adicionado
- `evals/`: benchmark reproduzível com braços isolados (sem skill, prompt mínimo, skill, ablação, candidata), juiz cego com ordem sorteada, checador determinístico (trechos protegidos, números, travessão, preâmbulo, `Falta fonte:`), critérios de decisão fixados antes da rodada, teste de acionamento e relatório de vocabulário.
- `tests/` e CI no GitHub Actions (Linux e Windows, Python 3.8 em diante), sem chamar modelo: checador, manifestos, versões, exemplos da própria skill e pacote ZIP.
- `.gitattributes` com fim de linha LF; o ZIP sai igual no Windows e no Linux.

### Corrigido
- O marketplace usava o nome `alexccastilho-skills`, o mesmo de outro plugin do autor, e um podia sobrescrever o outro.

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

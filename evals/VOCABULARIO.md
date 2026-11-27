# Vocabulário: como acompanhar os vícios dos modelos

Até a v2.0 a skill carregava uma lista de palavras suspeitas. Na v3.0.0 a lista saiu da skill: no conjunto de reserva, a versão sem lista empatou com a versão com lista, deixou o mesmo número de vícios nas saídas (30 contra 31) e ficou 13% menor. A skill agora depende de regras (enchimento, fórmulas, aberturas e fechamentos prontos), que não envelhecem como uma lista.

A lista antiga continua em `suspeitos.md`, como régua de medição. Este processo serve para saber se os modelos novos trouxeram vícios que as regras não pegam. A skill nunca busca nada na internet durante o uso. Uma lista baixada em tempo de execução seria uma porta para instruções injetadas, deixaria a skill mais lenta e nem sempre funcionaria no claude.ai.

## Quando revisar

- A cada novo modelo relevante (Claude, GPT, Gemini), porque o usuário costuma colar texto de vários deles.
- No mínimo a cada seis meses.

## Como revisar

1. Gere textos com o modelo novo. Use `tools/gen_corpus.py`, trocando ou acrescentando o modelo em `MODELS`. Para modelos de outros fornecedores, cole os textos num arquivo no mesmo formato de `corpus/generated.jsonl`.
2. Rode o benchmark só com o braço `baseline` no conjunto `dev`, para ver o que os modelos deixam para trás quando alguém pede para humanizar sem a skill:
   `python evals/run.py --out ../humanizer-bench --split dev --arms baseline`
3. Gere o relatório:
   `python evals/tools/vocab_report.py --bench ../humanizer-bench`
   Ele lê os suspeitos de `suspeitos.md` e mostra a frequência por 10 mil palavras em três fontes: texto natural de cada modelo, texto no estilo carregado de chatbot e saída do baseline. Também lista as expressões frequentes em texto de modelo que ainda não estão na lista.
4. Conte quantos suspeitos sobram nas saídas de cada braço do benchmark. Se a skill deixar com frequência algum vício que as regras atuais não pegam, há dois caminhos: escrever uma regra nova na §4 (preferível, porque não envelhece) ou acrescentar exemplos. Atualize `suspeitos.md` com as expressões novas e tire as que nenhum modelo usou nas duas últimas revisões.
5. Qualquer mudança na skill passa pelo benchmark completo (`README.md`) antes de publicar.

## O que a revisão de 25/11/2026 mostrou

- No texto natural de Claude Haiku, Sonnet e Opus 5.5, 3 dos 59 suspeitos apareceram, em 4 ocorrências: "jornada" uma vez no sentido figurado (Haiku, "fazem parte dessa jornada"), "ecossistema" uma vez no sentido literal (Sonnet, sobre mata nativa) e "Alicerce" duas vezes como nome próprio de uma construtora (Opus). Os vícios estão no texto carregado que as pessoas colam, vindo de outros modelos ou de versões antigas. (Contagem refeita em 27/11/2026 com o `vocab_report.py` corrigido; a versão anterior desta frase falava em 56 suspeitos e nenhuma ocorrência.)
- Depois de um pedido simples para humanizar sem a skill, o Claude ainda deixou "inovador", "robusto", "vale ressaltar", "crucial" e "dinâmico".
- No conjunto de desenvolvimento, a versão sem lista pareceu melhor que a com lista (28 a 11), mas no conjunto de reserva as duas empataram (47% x 53%). Uma tentativa intermediária, com lista curta e regra para manter adjetivos que são afirmação, empatou com a v2.0 e foi descartada.

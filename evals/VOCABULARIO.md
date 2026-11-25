# Manutenção da lista de vocabulário

A lista de palavras suspeitas da §4 do `SKILL.md` envelhece: cada geração de modelo troca alguns vícios por outros. Este processo mantém a lista atualizada sem transformá-la em lista proibida e sem buscar nada na internet durante o uso da skill. Uma lista baixada em tempo de execução seria uma porta para instruções injetadas, deixaria a skill mais lenta e nem sempre funcionaria no claude.ai.

## Quando revisar

- A cada novo modelo relevante (Claude, GPT, Gemini), porque o usuário costuma colar texto de vários deles.
- No mínimo a cada seis meses.

## Como revisar

1. Gere textos com o modelo novo. Use `tools/gen_corpus.py`, trocando ou acrescentando o modelo em `MODELS`. Para modelos de outros fornecedores, cole os textos num arquivo no mesmo formato de `corpus/generated.jsonl`.
2. Rode o benchmark só com o braço `baseline` no conjunto `dev`, para ver o que os modelos deixam para trás quando alguém pede para humanizar sem a skill:
   `python evals/run.py --out ../humanizer-bench --split dev --arms baseline`
3. Gere o relatório:
   `python evals/tools/vocab_report.py --bench ../humanizer-bench`
   Ele lê os suspeitos direto do `SKILL.md` e mostra a frequência por 10 mil palavras em três fontes: texto natural de cada modelo, texto no estilo carregado de chatbot e saída do baseline. Também lista as expressões frequentes em texto de modelo que ainda não estão na lista.
4. Decida à mão, item por item:
   - **Entra** uma expressão que aparece na saída do baseline ou no texto natural de modelo e é rara em texto humano (`corpus/human/`). Só a frequência no estilo carregado de chatbot não basta, porque esse estilo foi pedido de propósito.
   - **Sai** um suspeito que nenhum modelo usou nas duas últimas revisões.
   - Nada vira proibição. A regra continua: palavra que é afirmação do original fica, em forma mais simples ou como está.
5. Rode o benchmark completo (`README.md`) antes de publicar a versão com a lista nova.

## O que a revisão de 25/11/2026 mostrou

- No texto natural de Claude Haiku, Sonnet e Opus 5.5, nenhum dos 56 suspeitos apareceu. Os vícios estão no texto carregado que as pessoas colam, vindo de outros modelos ou de versões antigas.
- Depois de um pedido simples para humanizar sem a skill, o Claude ainda deixou "inovador", "robusto", "vale ressaltar", "crucial" e "dinâmico".
- A ablação mostrou que a lista longa fazia a skill apagar adjetivos que eram afirmação do original. A v2.1 encurtou a lista e separou enchimento (apagar) de palavra inflada (manter a afirmação em forma mais simples).

---
name: humanizer-pt-br
description: >
  Humaniza textos em Português do Brasil (pt-BR): remove marcas de escrita de IA
  (travessões, clichês, fórmulas, enchimento) e reescreve com voz natural, sem
  alterar o conteúdo. Use sempre que o usuário pedir para humanizar, tirar o
  jeito de IA, soar mais natural, fluido ou menos robótico, remover "AI slop", tirar
  travessão, deixar mais formal ou mais informal, ou adaptar um texto em pt-BR
  para LinkedIn, Instagram, e-mail, blog ou WhatsApp. Acione também diante de queixas como "parece ChatGPT", "tá muito
  formal", "não tá com a minha cara" ou "vão perceber que é IA", mesmo sem a
  palavra "humanizar", e em pedidos para reescrever ou melhorar a redação de
  prosa em pt-BR. Não use para código, tradução, correção só ortográfica ou
  gramatical, nem remoção de marcas d'água, metadados ou Unicode invisível.
license: MIT
metadata:
  author: Alex Camacho Castilho
  version: "3.0.1"
---

# Humanizador pt-BR

Rewrite AI-sounding text as natural Brazilian Portuguese: same content, fewer words, a human voice. Talk to the user in pt-BR.

When rules collide: user instruction and Control Tags (§7) > fidelity and protected spans (§1) > punctuation (§3) > AI tells (§4) > length > voice (§5).

## 1. Fidelity and protected spans

- Never add, change or drop a fact, number, name or claim, nor its strength: hedges like "pode" and "cerca de" stay. Cut only what carries no information.
- Vague attribution ("especialistas afirmam", "estudos mostram"): never invent a source, example or number. Keep the attribution and, if the claim depends on it, add one line after the text: `Falta fonte: <trecho>`.
- Protected spans are copied verbatim and exempt from every rule below: direct quotes, code, paths, URLs, e-mails, @menções, #hashtags, placeholders, names and brands (P&D, Johnson & Johnson), numbers, dates and ranges (10-20, 2020-2024, with the dash the source typed), technical and legal terms.
- Do not translate: text in another language gets the same rules in that language. Add no pt-PT lexicon (ecrã, telemóvel); convert pt-PT input only on request.

## 2. Output

- Deliver only the rewritten text, in the source format. No preamble ("Aqui está..."), no closing remark, no list of changes unless asked.
- If the user asks for a diagnosis ("o que tem de IA aqui?"), list tells and fixes instead of rewriting. If asked to humanize a file, edit it in place and reply in one line.
- Length: aim shorter than the source, because AI text is padded. A target, not a cap: equal or longer is fine when the source is already lean, the user asks for expansion, or `[OPINION]` is on.
- Text that already reads human: change little or nothing and say so in one line.
- Infer channel and register from the text and keep them. Ask one question only when the channel is unknown and changes the result: "Esse texto é para qual contexto? (LinkedIn, e-mail, artigo, post informal...)"
- Long text: go section by section, keep every heading, never summarize. If it will not fit in one reply, stop at a section boundary and ask "Continuo?".
- Never promise "indetectável" or a detector score.

## 3. Punctuation

The dash used as an aside is the strongest visual tell in pt-BR. In prose, remove the travessão (U+2014), the meia-risca (U+2013) and the spaced hyphen ( - ) when they mark an aside, pause or emphasis. Swapping one for another only renames the tell.

Use what fits the sentence: comma (short apposition), colon (the second part explains the first), full stop (two independent ideas), parentheses (rare), or delete the aside when it is filler. Do not default to full stops: chopped prose is a tell too.

| IA | Humano |
|---|---|
| O time — que já estava sobrecarregado — recusou. | O time, já sobrecarregado, recusou. |
| Só existe um caminho — cortar custos. | Só existe um caminho: cortar custos. |

Keep dashes in fiction dialogue lines, protected spans, compound words (segunda-feira), list markers and labels outside prose ("Nome - Cargo"). With `[TRAVESSAO: OK]`, keep the dashes already there and add none.

- Digital channels (LinkedIn, Instagram, WhatsApp, e-mail): straight quotes and three dots (...) instead of curly quotes and the ellipsis character (…). Editorial text (press release, livro) and unknown channels stay as typed.
- In prose, remove arrows (→), inline bullets (•) and "&" standing in for "e".
- At most one "!" per block. No "!!" or "?!".

## 4. AI tells

**Structure.**
- Contrast formula ("Não é apenas X, é Y", "Não se trata de X, mas de Y", "Mais do que X, é Y"): state Y. Keep it when X is a real misconception the text refutes.
- Decorative triad ("rápido, prático e eficiente"): keep the terms that inform. Three real items stay three.
- Rhetorical Q&A ("O resultado? Um sucesso."): say it straight ("Deu certo.").
- Openers ("No mundo atual", "Em um cenário cada vez mais", "Você já parou para pensar", "Neste artigo, vamos", "Imagine", "Seja X ou Y", "Quando o assunto é"): start with the point. Do not invent a hook.
- Closers ("Em resumo", "Em suma", "Concluindo", "E você, o que acha?", "Confira", "Bora?", "Comente aqui"): end when done. Keep a specific CTA (link, date, action).
- Chatbot residue ("Ótima pergunta!", "Claro!", "Espero ter ajudado"): delete.
- Gerund tails ("..., trazendo benefícios e garantindo sucesso"): use finite verbs.
- Significance inflation ("um marco fundamental para o setor"): plain claim, same strength ("foi importante para o setor").
- Passive plus nominalization ("foi realizada a implementação pela equipe"): active voice when the text names the agent ("a equipe implementou").
- Formatting: lists where every item is "**Título:** texto", emoji as bullet or header, scattered bold, "Título: subtítulo" headers. Make them plain unless the channel expects them (Instagram) or the text is instructional.
- Uniform rhythm (every paragraph with 2 or 3 same-size sentences): vary by merging or splitting what exists, never by adding content.

| IA | Humano |
|---|---|
| Não é só um app de notas — é um verdadeiro aliado que organiza suas ideias. | O app de notas organiza suas ideias. |
| O prazo era curto — e o time entregou. | O prazo era curto, mas o time entregou. |

## 5. Voice and structure

- Opinion, reaction and "eu" only when the source has them or `[OPINION]` is on. Never in press releases or corporate comms.
- Oral contractions (pra, tá, né, cê) only in WhatsApp, Instagram and `[CASUAL]`.
- Do not overcorrect: forced slang, added jokes and chopped sentences read as fake as slop. When in doubt, be sober and direct.
- Instructional or technical text keeps its lists. Narrative text (blog, artigo, LinkedIn longo) turns bullet walls into prose. Otherwise preserve the structure.

| Canal | Tom | Estrutura |
|---|---|---|
| LinkedIn | Direto, sem autopromoção | Parágrafos curtos, sem bullet wall |
| Instagram / X | Casual | Frases curtas, sem preâmbulo |
| E-mail corporativo | Claro, respeitoso, formal | Contexto, pedido, encerramento |
| Blog / artigo | Informativo, voz própria | Prosa, poucas listas |
| WhatsApp | Conversacional | Parágrafos mínimos |
| Press release | Neutro, factual, 3ª pessoa | Estrutura de nota |

## 6. Final check

Before delivering, fix if:
1. A fact, number, name or hedge was added, changed or lost, or a protected span differs from the source.
2. A dash still marks an aside in prose (without `[TRAVESSAO: OK]`).
3. A §4 tell remains with no reason to keep it.
4. Read aloud, it sounds like a discurso de formatura or like forced informality.

## 7. Control Tags

Tags combine, and a plain request counts as its tag ("deixa mais informal" = `[CASUAL]`). Tone tags override `[CANAL]` defaults. If two tags conflict, the last wins.
- `[CASUAL]` tom amigável, frases curtas, leve informalidade
- `[FORMAL]` profissional, sem opinião nem gíria
- `[OPINION]` acrescenta reação ou avaliação sobre fatos já presentes; não inventa experiência pessoal
- `[CANAL: LinkedIn]` adapta ao canal indicado
- `[DEBUG]` antes do texto, lista até 10 linhas `padrão: trecho`
- `[ESTRUTURA]` mantém a estrutura original, sem converter listas em prosa
- `[TRAVESSAO: OK]` mantém os travessões do original; nunca cria travessão novo

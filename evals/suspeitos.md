# Lista de referência de palavras suspeitas

Retirada do SKILL.md na v3.0.0: no conjunto de reserva, a skill sem a lista empatou com a skill com lista e deixou o mesmo número de vícios nas saídas. Fica aqui só para medir quanto vício sobra nas saídas (`tools/vocab_report.py`). Não é carregada pela skill.

**Vocabulary.** Suspects, not a blacklist. Replace a word when it inflates or decorates and a plainer one says the same. Keep it when it is literal or technical ("otimizar a query", "ecossistema" em biologia, "cenário de teste").
- Verbs: mergulhar, desvendar, abraçar (ideias), alavancar, fomentar, potencializar, impulsionar, catalisar, destravar, navegar (desafios), "vamos explorar"; otimizar, aprimorar, maximizar with no concrete object
- Adjectives: robusto, crucial, fundamental, essencial, abrangente, vibrante, dinâmico, inovador, revolucionário, impactante, estratégico, holístico, disruptivo, transformador, poderoso, "um verdadeiro X"
- Metaphor nouns: tapeçaria, sinfonia, testamento, ecossistema, jornada, universo, cenário/panorama, pilar, alicerce, sinergia, mindset, divisor de águas, chave para o sucesso
- Filler and intensifiers, delete: vale ressaltar/destacar, é importante notar, cabe destacar, é fundamental que, em última análise, nesse contexto, nesse sentido, diante disso, sem dúvida, trata-se de, quando se trata de, realmente, verdadeiramente, extremamente
- Connectors (além disso, no entanto, portanto, por outro lado, dessa forma, por fim) are legitimate. Fix them only when they open sentence after sentence or link nothing.

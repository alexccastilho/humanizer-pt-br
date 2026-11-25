# Avaliação da skill

Esta pasta mede se a skill melhora de fato o texto em relação ao Claude sem ela, e se não estraga nada no caminho. Os critérios de decisão abaixo foram fixados **antes** da primeira rodada do conjunto de reserva e só mudam com uma nova versão deste arquivo, registrada no Git.

## Conjunto de teste

- `corpus/generated.jsonl`: 90 textos gerados por Claude Haiku, Sonnet e Opus (30 de cada), sobre 45 temas fictícios com fatos, números, nomes e ressalvas, em 6 canais (LinkedIn, Instagram, e-mail, blog, WhatsApp, release). Metade foi escrita no estilo natural do modelo, metade imitando o estilo carregado de chatbot. Gerado por `tools/gen_corpus.py`.
- `corpus/handmade.json`: casos escritos à mão. São casos difíceis (código, citação, intervalo 10-20, pt-PT, diálogo de ficção, marcas com "&", passo a passo, tags, atribuição vaga, contraste legítimo, tríade real, pedido só de diagnóstico) e textos que já estão bons e devem mudar pouco.
- `corpus/human/*.json` (opcional): textos escritos por pessoas, no mesmo formato. Servem para medir correção excessiva.

Cada caso pertence a `dev` (usado para ajustar a skill) ou `holdout` (reserva, usado só para a decisão de release). A divisão dos textos gerados é fixa, por hash do id.

## Braços

| Braço | O que recebe |
|---|---|
| `baseline` | Só o pedido do usuário, sem skill |
| `minimal` | O pedido e uma instrução de duas linhas que qualquer pessoa poderia escrever |
| `skill` | O pedido, com a skill carregada como plugin (precisa ser acionada sozinha) |
| `novocab` | Como `skill`, sem a lista de vocabulário da §4 (ablação; só funciona com uma versão que ainda tenha a lista, como a v2.0) |
| `cand` | Uma versão candidata da skill (`--cand-dir`), para comparar com a publicada (`--skill-dir`) |

Todas as execuções são isoladas: pasta vazia, sem configurações nem plugins do usuário, sem servidores MCP e sem sincronização de skills do claude.ai (`claude_cli.py`). O modelo testado é fixado por alias (`--model`), e o id real fica gravado em cada resultado.

## Métricas

- **Determinísticas** (`check.py`, sem modelo, roda no CI): trechos protegidos idênticos, números preservados e nenhum número novo, travessão de aparte na prosa, preâmbulo ou fechamento de chatbot, "!!" e setas, linha `Falta fonte:` quando esperada, razão de tamanho e similaridade nos textos que já estão bons.
- **Juiz cego** (`judge.py`): compara duas saídas sem saber de qual braço vieram, com a ordem A/B sorteada, e lista os erros de fidelidade de cada uma. O juiz roda num modelo mais forte que o testado.
- **Custo**: tokens de entrada (incluindo cache), tokens de saída e custo em US$ por execução, lidos do JSON do Claude Code.

A contagem de palavras "suspeitas" não entra na decisão: ela usa a lista da própria skill e por isso favorece a skill por construção.

## Critérios de decisão (conjunto de reserva)

| Id | Critério | Se falhar |
|---|---|---|
| G0 | Pelo menos 30 reescritas por braço e por par julgado | Nenhum outro critério pode passar |
| G1 | Nenhum trecho protegido alterado pela skill | Bloqueia a release |
| G2 | Falhas de número da skill não passam as do baseline | Bloqueia a release |
| G3 | Erros de fidelidade apontados pelo juiz: skill não passa o baseline | Bloqueia a release |
| G4 | Preferência do juiz pela skill contra o baseline de pelo menos 60%, com IC 95% acima de 50% (empates fora) | A skill não "ganha" |
| G5 | Contra o prompt mínimo, a skill não perde com significância (IC 95% superior de pelo menos 50%) | Encolher a skill para o que a ablação mostrar que importa |
| T | Custo médio por execução da skill menor ou igual ao do baseline | O nome deixa de prometer economia de tokens (renomear) |

Se G4 falhar e o baseline vencer com significância, a skill é reposicionada ou descontinuada, e os números são publicados mesmo assim.

## Como rodar

```bash
# 1. execuções (fora do repositório): versão publicada x candidata
python evals/run.py --out ../humanizer-bench --split holdout --reps 2 --jobs 6 \
    --arms baseline,minimal,skill,cand --skill-dir <pasta da versão publicada>
# 2. juiz
python evals/judge.py --out ../humanizer-bench --split holdout --reps 2 --jobs 6 \
    --pairs cand:baseline,cand:minimal,cand:skill
# 3. relatório e critérios, aplicados à candidata
python evals/analyze.py --out ../humanizer-bench --split holdout --candidate cand --report evals/results/<versão>
# acionamento da descrição
python evals/trigger.py --out ../humanizer-bench --label <versão>
```

O CI não chama modelo nenhum (não há chave de API no repositório). Ele roda `check.py`, os testes e a validação do pacote. O benchmark roda localmente antes de cada release, e o resultado fica em `results/<versão>/`.

## Manutenção da lista de vocabulário

Ver `VOCABULARIO.md`.

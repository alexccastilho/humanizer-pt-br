# Resultado do benchmark (holdout)

## Checagens determinísticas por braço

| Braço | Execuções | Acionou skill | Com alguma falha | Protegidos | Nº sumiu | Nº novo | Travessão | Preâmbulo | Falta fonte ausente | Tamanho (IA, mediana) | Similaridade texto bom | Tokens entrada (med.) | Tokens saída (med.) | Custo médio US$ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 136 | 0 | 58/134 | 6 | 4 | 12 | 2 | 38 | 2 | 1.155 | 0.426 | 7362.5 | 467.0 | 0.02831 |
| cand | 136 | 130 | 3/134 | 0 | 1 | 0 | 2 | 0 | 0 | 0.741 | 0.877 | 19085.0 | 531.5 | 0.04561 |
| minimal | 136 | 0 | 7/134 | 2 | 0 | 1 | 2 | 0 | 2 | 0.861 | 0.859 | 7475.5 | 316.0 | 0.02745 |
| skill | 136 | 131 | 2/134 | 0 | 0 | 1 | 1 | 0 | 0 | 0.74 | 0.871 | 19572.0 | 541.0 | 0.04741 |

## Preferência do juiz cego

| Par | n | Vitórias 1º | Vitórias 2º | Empates | Taxa 1º (sem empates) | IC 95% | Venceu posição A/B |
|---|---|---|---|---|---|---|---|
| cand x baseline | 136 | 124 | 12 | 0 | 91% | 85% a 95% | 73/63 |
| cand x minimal | 136 | 83 | 52 | 1 | 62% | 53% a 69% | 66/69 |
| cand x skill | 136 | 61 | 68 | 7 | 47% | 39% a 56% | 64/65 |
| skill x baseline | 136 | 124 | 12 | 0 | 91% | 85% a 95% | 79/57 |

## Fidelidade e naturalidade (juiz)

| Braço | Erros de fidelidade por saída | Saídas com erro | Naturalidade média (1-10) |
|---|---|---|---|
| baseline | 2.191 | 86% | 6.96 |
| cand | 0.784 | 51% | 7.13 |
| minimal | 1 | 60% | 6.61 |
| skill | 0.812 | 53% | 7.23 |

## Critérios de decisão

- PASSOU: G0 dados suficientes (>= 30 reescritas por braço)
- PASSOU: G1 trechos protegidos intactos (cand)
- PASSOU: G2 números: cand não pior que baseline
- PASSOU: G3 fidelidade (juiz): cand não pior que baseline
- PASSOU: G4 preferência cand x baseline >= 60% e IC acima de 50%
- PASSOU: G5 cand não perde do prompt mínimo (IC superior >= 50%)
- FALHOU: T economia de tokens real (custo médio cand <= baseline)

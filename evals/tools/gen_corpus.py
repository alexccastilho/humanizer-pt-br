"""Generate the AI-written part of the eval corpus with Claude Code.

Each topic carries facts (numbers, names, a hedge) that the rewrite must keep, so the
checker and the fidelity judge have something concrete to verify. Every topic yields two
texts: "natural" (the model writes as it normally would) and "slop" (the model imitates
the heavy chatbot style people paste into a humanizer). Models rotate so the corpus is
not the voice of a single model.

Usage:
  python evals/tools/gen_corpus.py --out evals/corpus/generated.jsonl [--jobs 4]

Runs are isolated: no user settings, plugins or MCP servers (see evals/run.py).
Author: Alex Camacho Castilho
"""
import argparse
import concurrent.futures
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from claude_cli import run_claude  # noqa: E402

CHANNELS = {
    "linkedin": ("um post de LinkedIn", "Humaniza esse post pro LinkedIn:"),
    "instagram": ("uma legenda de Instagram", "Tira o jeito de IA dessa legenda do Insta:"),
    "email": ("um e-mail corporativo", "Deixa esse e-mail mais natural, tá com cara de ChatGPT:"),
    "blog": ("um texto curto de blog (3 a 5 parágrafos)", "Humaniza esse texto do blog:"),
    "whatsapp": ("uma mensagem de WhatsApp para um grupo de trabalho", "Deixa essa mensagem menos robótica:"),
    "press": ("um comunicado à imprensa curto", "Humaniza esse release, tá muito com cara de IA:"),
}

# Fictional organizations and people, so no real claim is put in anyone's mouth.
TOPICS = [
    ("lançamento do app de agendamento da Clínica Vitalis", "lançado em 3 de março de 2025; 12 mil downloads no primeiro mês; nota 4,7; a diretora Paula Ramos diz que pode reduzir faltas em cerca de 20%"),
    ("resultado trimestral da cooperativa Agrovale", "faturamento de R$ 48 milhões no 2º trimestre; alta de 9% sobre o ano anterior; 1.350 cooperados; nova unidade em Rio Verde (GO) prevista para 2026"),
    ("mudança de horário do atendimento da Prefeitura de Santa Clara", "a partir de 2 de junho; atendimento das 8h às 17h; agendamento pelo site atende.santaclara.example.br; cerca de 600 atendimentos por dia"),
    ("contratação de 40 desenvolvedores pela Tecnora", "40 vagas; trabalho remoto; salário entre R$ 9 mil e R$ 14 mil; inscrições até 30 de abril; processo em 3 etapas"),
    ("migração do sistema financeiro da Loja Bela Casa", "migração do ERP antigo para nuvem; levou 7 meses; custo de R$ 380 mil; fechamento mensal caiu de 10 para 4 dias"),
    ("curso gratuito de Excel da ONG Futuro Já", "turmas de 25 alunos; 8 encontros; aulas aos sábados das 9h às 12h; certificado; parceria com o Senac"),
    ("aniversário de 10 anos da padaria Pão da Vila", "fundada em 2015 por Marta e João Lima; 18 funcionários; 2 mil pães por dia; festa no dia 14 com café grátis das 7h às 9h"),
    ("pesquisa interna de clima da Metalúrgica Forte", "participação de 82%; satisfação geral 7,1 de 10; principal queixa: comunicação; plano de ação até setembro"),
    ("parceria entre a fintech Pagafácil e o Banco Horizonte", "acordo assinado em 15 de maio; 300 mil clientes poderão abrir conta pelo app; tarifa zero no primeiro ano; segundo o CEO, Rafael Duarte, a meta é chegar a 1 milhão até 2027"),
    ("vazamento de água no prédio da escola Monteiro Lobato", "aulas suspensas na quinta e sexta; 540 alunos afetados; obra emergencial de R$ 62 mil; retorno previsto para segunda-feira"),
    ("novo plano de saúde para funcionários da Logix", "vale a partir de 1º de julho; cobertura nacional; coparticipação de 20% em consultas; dependentes até 24 anos"),
    ("estudo sobre uso de bicicleta em Curitiba feito pelo Instituto Mobilis", "entrevistou 2.100 pessoas; 31% usam bicicleta ao menos uma vez por semana; principal barreira: falta de ciclovia; margem de erro de 2 pontos"),
    ("redução do tempo de entrega da distribuidora Rota Sul", "prazo médio caiu de 5 para 2 dias; novo centro em Joinville; 14 caminhões elétricos; investimento de R$ 22 milhões"),
    ("palestra sobre LGPD na Associação Comercial de Bauru", "dia 9 de outubro às 19h; palestrante: advogada Renata Okada; vagas limitadas a 120; inscrição gratuita"),
    ("troca de fornecedor de café do escritório", "novo fornecedor a partir de segunda; café em grãos de Minas; máquina nova no 3º andar; quem quiser opinar responde a enquete até sexta"),
    ("campanha de vacinação contra gripe da empresa Nortecom", "dias 22 e 23 de abril; das 9h às 16h; sala 204; 450 doses; levar documento com foto"),
    ("prêmio de inovação recebido pela startup Hidrosense", "sensor que mede vazamento em canos; reduziu desperdício em cerca de 35% nos pilotos; prêmio de R$ 150 mil; 6 cidades testando"),
    ("queda no sistema de pagamentos da loja online Moda Leve", "fora do ar por 3 horas no sábado; 1.800 pedidos afetados; causa: falha no provedor; clientes recebem cupom de 15%"),
    ("abertura de inscrições do mestrado em Ciência de Dados da Universidade do Vale", "20 vagas; inscrições de 1º a 31 de agosto; prova em setembro; bolsa para até 8 alunos"),
    ("relatório de sustentabilidade da indústria Papel Bom", "redução de 18% no consumo de água desde 2021; 64% da energia vem de fontes renováveis; meta de zerar aterro até 2030"),
    ("retorno ao trabalho presencial na agência Criare", "3 dias presenciais por semana a partir de agosto; terças, quartas e quintas; vale-refeição reajustado em 12%"),
    ("lançamento do livro de receitas da chef Ana Beatriz Costa", "120 receitas; editora Sabor; lançamento em 18 de novembro na Livraria Central às 18h; preço de R$ 89"),
    ("manutenção programada no sistema da Distribuidora Luz Norte", "domingo das 2h às 6h; o portal e o app ficam fora do ar; contas com vencimento no dia podem ser pagas na segunda sem multa"),
    ("crescimento do e-commerce de pequenas lojas segundo a Associação Lojistas Online", "alta de 23% nas vendas em 2024; ticket médio de R$ 186; Pix responde por 41% dos pagamentos; dados de 900 lojas"),
    ("mudança da sede da consultoria Prisma para São Paulo", "nova sede na Avenida Paulista; mudança em 5 de setembro; 75 funcionários; o escritório de Campinas continua"),
    ("programa de estágio da construtora Alicerce", "15 vagas; bolsa de R$ 2.200; carga de 6 horas; cursos de engenharia, arquitetura e administração; inscrições até 10 de março"),
    ("adoção de IA no atendimento da operadora Conecta", "chatbot resolve 58% das dúvidas sem atendente; tempo médio de espera caiu de 9 para 3 minutos; 200 atendentes realocados, nenhum demitido"),
    ("feira de adoção de animais da ONG Patas Unidas", "sábado, 12 de abril, das 10h às 16h; Parque da Cidade; 60 cães e gatos; todos vacinados e castrados"),
    ("revisão do contrato de aluguel do galpão da Transvia", "reajuste de 4,5% pelo IPCA; contrato renovado por 5 anos; cláusula de saída antecipada com multa de 3 aluguéis"),
    ("encerramento do serviço de newsletter da editora Página 9", "último envio em 30 de junho; 48 mil assinantes; conteúdo migra para o blog; assinantes pagos recebem reembolso proporcional"),
    ("resultado do hackathon da prefeitura de Vitória da Serra", "36 equipes; 180 participantes; vencedor: app que mapeia buracos nas ruas; prêmio de R$ 30 mil e contrato de 6 meses"),
    ("nova política de home office da seguradora Amparo", "até 2 dias remotos por semana; ajuda de custo de R$ 150 por mês; vale para quem tem mais de 6 meses de casa"),
    ("estudo da Fundação Saber sobre leitura entre adolescentes", "amostra de 3.400 estudantes; 44% leram ao menos um livro por lazer no último ano; queda de 7 pontos desde 2019; pode haver efeito da pandemia"),
    ("inauguração da academia ao ar livre no bairro Jardim Esperança", "10 aparelhos; aberta das 6h às 22h; custo de R$ 85 mil; pedido da associação de moradores feito em 2022"),
    ("atraso na entrega do residencial Vista Verde", "entrega adiada de dezembro para março; 220 apartamentos; motivo: falta de elevadores; construtora paga multa de 0,5% ao mês"),
    ("lançamento de linha de cosméticos veganos da marca Flor de Lis", "8 produtos; sem teste em animais; embalagens com 70% de plástico reciclado; preços de R$ 29 a R$ 79"),
    ("treinamento obrigatório de segurança da informação na Datavia", "prazo até 15 de maio; 40 minutos; plataforma interna; quem não concluir perde o acesso ao e-mail até finalizar"),
    ("expansão da rede de farmácias Saúde Mais para o Nordeste", "12 lojas novas em 2025; Recife, Fortaleza e Salvador; 300 empregos; investimento de R$ 45 milhões"),
    ("pedido de feedback sobre o novo portal do cliente da Contabiliza", "portal no ar desde 1º de fevereiro; formulário de 5 perguntas; leva cerca de 3 minutos; respostas até dia 20"),
    ("balanço da campanha do agasalho do Colégio São Bento", "3.200 peças arrecadadas; 4 instituições atendidas; meta era 2.500; doação entregue em 28 de junho"),
    ("atualização de preços da escola de idiomas Fluent", "reajuste de 6% a partir de janeiro; alunos atuais mantêm o valor até julho; desconto de 10% no pagamento anual"),
    ("relato de um projeto de reflorestamento da Associação Mata Viva", "45 hectares; 60 mil mudas de 80 espécies nativas; 5 anos de trabalho; taxa de sobrevivência das mudas de cerca de 85%"),
    ("convite para o evento de fim de ano da equipe de vendas da Brisa Tintas", "dia 12 de dezembro às 19h30; restaurante Varanda; confirmar presença até dia 5; traje esporte fino"),
    ("mudança na diretoria do Hospital Santa Rita", "Dr. Carlos Menezes assume a direção-geral em 1º de agosto; substitui a Dra. Lúcia Prado, que ficou 8 anos no cargo; ela segue no conselho"),
    ("lançamento do podcast da cooperativa de crédito Unir", "episódios quinzenais de 25 minutos; tema: educação financeira; disponível no Spotify e no YouTube; primeiro episódio dia 3"),
]

STYLES = {
    "natural": "Escreva {what} sobre: {topic}. Use todos estes dados, sem inventar outros números: {facts}. Entregue só o texto, sem comentários.",
    "slop": ("Escreva {what} sobre: {topic}. Use todos estes dados, sem inventar outros números: {facts}. "
             "Escreva no estilo típico de texto gerado por chatbot, com os vícios mais comuns em português: "
             "travessões como aparte, 'não é só X, é Y', 'vale ressaltar', adjetivos como robusto, crucial e "
             "inovador, tríades decorativas, pergunta retórica seguida de resposta, abertura genérica e "
             "fechamento com pergunta ou chamada vaga. Entregue só o texto, sem comentários."),
}

MODELS = ["haiku", "sonnet", "opus"]


def build_jobs():
    jobs, i = [], 0
    channels = list(CHANNELS)
    for t, (topic, facts) in enumerate(TOPICS):
        for style in STYLES:
            ch = channels[(t + (style == "slop") * 3) % len(channels)]
            jobs.append({
                "id": f"gen-{t:02d}-{style}",
                "channel": ch,
                "origin": f"ai-{style}",
                "topic": topic,
                "facts": facts,
                "model": MODELS[i % len(MODELS)],
                "request": CHANNELS[ch][1],
                "prompt": STYLES[style].format(what=CHANNELS[ch][0], topic=topic, facts=facts),
            })
            i += 1
    return jobs


def split_of(case_id):
    """Stable split: one in three cases goes to dev, the rest to holdout."""
    return "dev" if int(hashlib.sha256(case_id.encode()).hexdigest(), 16) % 3 == 0 else "holdout"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    done = {}
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                done[rec["id"]] = rec
    todo = [j for j in build_jobs() if j["id"] not in done]

    def work(job):
        res = run_claude(job["prompt"], model=job["model"])
        text = (res.get("result") or "").strip()
        return job, text, res

    with concurrent.futures.ThreadPoolExecutor(args.jobs) as ex:
        for job, text, res in ex.map(work, todo):
            if not text or res.get("is_error"):
                print("FAIL", job["id"], res.get("error"), file=sys.stderr)
                continue
            done[job["id"]] = {
                "id": job["id"], "split": split_of(job["id"]), "channel": job["channel"],
                "origin": job["origin"], "generator": res.get("model_id") or job["model"],
                "request": job["request"], "text": text, "facts": job["facts"],
                "protected": [], "tags": [], "expect": {},
            }
            print("ok", job["id"], job["model"], len(text.split()), "palavras", flush=True)
    ordered = [done[j["id"]] for j in build_jobs() if j["id"] in done]
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in ordered), encoding="utf-8")
    print(out, len(ordered))


if __name__ == "__main__":
    main()

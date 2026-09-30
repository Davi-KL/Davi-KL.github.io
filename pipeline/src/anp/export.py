"""Monta, valida e grava os JSONs consumidos pelo site."""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from jsonschema import Draft202012Validator

from anp.aggregate import janela_4_semanas, monthly, window_mean
from anp.config import ANP_PAGE_URL, BCB_IPCA_URL, LIMIAR_ETANOL, ORDEM_PRODUTOS, UFS
from anp.ipca import aplicar_real, fatores

ARQUIVOS = ("evolucao", "ranking_uf", "etanol_gasolina", "meta")
REGIOES = ["BR", *UFS]
UM_ANO = pd.Timedelta(days=364)


def _num(valor, casas: int = 3):
    return None if valor is None or pd.isna(valor) else round(float(valor), casas)


def _todos_meses(inicio: str, fim: str) -> list[str]:
    return [p.strftime("%Y-%m") for p in pd.period_range(inicio, fim, freq="M")]


def build_evolucao(mensal: pd.DataFrame, ipca_ref: str) -> dict:
    meses = _todos_meses(mensal["mes"].min(), mensal["mes"].max())
    series: dict[str, dict] = {}
    for regiao in REGIOES:
        por_produto = {}
        for produto in ORDEM_PRODUTOS:
            recorte = mensal[(mensal["uf"] == regiao) & (mensal["produto"] == produto)]
            if recorte.empty:
                continue
            recorte = recorte.set_index("mes").reindex(meses)
            por_produto[produto] = {
                "nominal": [_num(v) for v in recorte["preco_medio"]],
                "real": [_num(v) for v in recorte["real"]],
            }
        if por_produto:
            series[regiao] = por_produto
    return {"meses": meses, "ipca_ref": ipca_ref, "series": series}


def build_ranking(diario: pd.DataFrame) -> dict:
    inicio, fim = janela_4_semanas(diario["data"].max())
    atual = window_mean(diario, inicio, fim)
    anterior = window_mean(diario, inicio - UM_ANO, fim - UM_ANO).set_index(["uf", "produto"])["preco_medio"]
    itens = []
    for linha in atual.itertuples():
        preco_antes = anterior.get((linha.uf, linha.produto))
        variacao = None if preco_antes is None or pd.isna(preco_antes) else (linha.preco_medio / preco_antes - 1) * 100
        itens.append({
            "uf": linha.uf,
            "produto": linha.produto,
            "preco_medio": _num(linha.preco_medio),
            "variacao_12m_pct": _num(variacao, 1),
            "n_coletas": int(linha.n),
        })
    return {"periodo": {"inicio": inicio.strftime("%Y-%m-%d"), "fim": fim.strftime("%Y-%m-%d")}, "itens": itens}


def build_etanol_gasolina(ranking: dict, mensal: pd.DataFrame) -> dict:
    precos = {(i["uf"], i["produto"]): i["preco_medio"] for i in ranking["itens"]}
    atual = []
    for uf in REGIOES:
        etanol, gasolina = precos.get((uf, "etanol")), precos.get((uf, "gasolina"))
        if etanol is None or gasolina is None:
            continue
        razao = round(etanol / gasolina, 3)
        atual.append({"uf": uf, "razao": razao, "compensa": "etanol" if razao < LIMIAR_ETANOL else "gasolina"})

    tabela = mensal.pivot_table(index=["mes", "uf"], columns="produto", values="preco_medio")
    razao_mensal = (tabela["etanol"] / tabela["gasolina"]).rename("razao").reset_index()
    meses = _todos_meses(mensal["mes"].min(), mensal["mes"].max())
    historico = {}
    for uf in REGIOES:
        serie = razao_mensal[razao_mensal["uf"] == uf].set_index("mes")["razao"].reindex(meses)
        if serie.notna().any():
            historico[uf] = [_num(v) for v in serie]
    return {"limiar": LIMIAR_ETANOL, "atual": atual, "historico": {"meses": meses, "razao": historico}}


def build_meta(diario: pd.DataFrame, ranking: dict, etanol_gasolina: dict, evolucao: dict,
               ipca_ref: str, ipca_em_cache: bool, agora: datetime) -> dict:
    itens = {(i["uf"], i["produto"]): i for i in ranking["itens"]}
    gasolina_df = itens[("DF", "gasolina")]["preco_medio"]
    gasolina_br = itens[("BR", "gasolina")]["preco_medio"]
    altas = [i for i in ranking["itens"] if i["uf"] != "BR" and i["variacao_12m_pct"] is not None]
    maior = max(altas, key=lambda i: i["variacao_12m_pct"], default=None)
    ultima = diario["data"].max()
    semana = ultima - pd.Timedelta(days=ultima.dayofweek)
    vazio = [None] * len(evolucao["meses"])

    def serie_gasolina(uf: str) -> list:
        return evolucao["series"].get(uf, {}).get("gasolina", {}).get("nominal", vazio)[-24:]

    return {
        "atualizado_em": agora.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "semana_mais_recente": semana.strftime("%Y-%m-%d"),
        "n_coletas_total": int(diario["n"].sum()),
        "ipca_ate": ipca_ref,
        "ipca_em_cache": ipca_em_cache,
        "fontes": [
            {"nome": "ANP — Série Histórica de Preços de Combustíveis", "url": ANP_PAGE_URL},
            {"nome": "Banco Central — SGS 433 (IPCA)", "url": BCB_IPCA_URL},
        ],
        "destaques": {
            "gasolina_df": gasolina_df,
            "gasolina_br": gasolina_br,
            "diff_df_br_pct": _num((gasolina_df / gasolina_br - 1) * 100, 1),
            "ufs_etanol_compensa": sum(
                1 for a in etanol_gasolina["atual"] if a["uf"] != "BR" and a["compensa"] == "etanol"
            ),
            "maior_alta_12m": None if maior is None else {
                "uf": maior["uf"], "produto": maior["produto"], "pct": maior["variacao_12m_pct"],
            },
        },
        "serie_home": {
            "meses": evolucao["meses"][-24:],
            "gasolina_br": serie_gasolina("BR"),
            "gasolina_df": serie_gasolina("DF"),
        },
    }


def _validador(schemas_dir: Path, nome: str) -> Draft202012Validator:
    esquema = json.loads((schemas_dir / f"{nome}.schema.json").read_text(encoding="utf-8"))
    return Draft202012Validator(esquema)


def export_all(diario: pd.DataFrame, ipca_df: pd.DataFrame, ipca_em_cache: bool, out_dir: Path,
               schemas_dir: Path, agora: datetime) -> dict[str, dict]:
    fator, ref = fatores(ipca_df)
    mensal = aplicar_real(monthly(diario), fator, ref)
    evolucao = build_evolucao(mensal, ref)
    ranking = build_ranking(diario)
    etanol_gasolina = build_etanol_gasolina(ranking, mensal)
    meta = build_meta(diario, ranking, etanol_gasolina, evolucao, ref, ipca_em_cache, agora)
    saidas = {"evolucao": evolucao, "ranking_uf": ranking, "etanol_gasolina": etanol_gasolina, "meta": meta}

    for nome, obj in saidas.items():
        _validador(schemas_dir, nome).validate(obj)

    out_dir.mkdir(parents=True, exist_ok=True)
    for nome, obj in saidas.items():
        (out_dir / f"{nome}.json").write_text(
            json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
    return saidas

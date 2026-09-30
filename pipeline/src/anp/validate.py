"""Checagens de sanidade: nenhum dado é publicado se alguma delas falhar."""

from datetime import date

import pandas as pd

from anp.aggregate import weekly
from anp.config import MAX_VARIACAO_SEMANAL, ORDEM_PRODUTOS, PRECO_MAX, PRECO_MIN, UFS


class ValidationError(RuntimeError):
    def __init__(self, erros: list[str]):
        super().__init__("Validação falhou:\n- " + "\n- ".join(erros))
        self.erros = erros


def validate(diario: pd.DataFrame, maximo_anterior: pd.Timestamp | None, hoje: date) -> None:
    if diario.empty:
        raise ValidationError(["base vazia"])
    erros: list[str] = []

    medias = diario["soma"] / diario["n"]
    fora = int((~medias.between(PRECO_MIN, PRECO_MAX)).sum())
    if fora:
        erros.append(f"{fora} médias diárias fora da faixa de R$ {PRECO_MIN:.2f} a R$ {PRECO_MAX:.2f}")

    ultima = diario["data"].max()
    if ultima.normalize() > pd.Timestamp(hoje):
        erros.append(f"data futura na base: {ultima.date()}")
    if maximo_anterior is not None and ultima < maximo_anterior:
        erros.append(f"última data {ultima.date()} é anterior à que já estava na base ({maximo_anterior.date()})")

    semanal = weekly(diario)
    ultima_semana = semanal["semana"].max()
    # As três séries publicadas (não só gasolina): se o link de um produto sumir da
    # página da ANP, esse produto para de ser atualizado sem que nada avise.
    for produto in ORDEM_PRODUTOS:
        presentes = set(
            semanal[(semanal.semana == ultima_semana) & (semanal.produto == produto) & (semanal.uf != "BR")]["uf"]
        )
        faltando = sorted(set(UFS) - presentes)
        if faltando:
            erros.append(f"semana de {ultima_semana.date()} sem {produto} para: {', '.join(faltando)}")

    br = semanal[(semanal.uf == "BR") & (semanal.produto == "gasolina")].sort_values("semana")
    if len(br) >= 2:
        anterior, atual = br["preco_medio"].iloc[-2], br["preco_medio"].iloc[-1]
        variacao = abs(atual / anterior - 1)
        if variacao >= MAX_VARIACAO_SEMANAL - 1e-9:
            erros.append(f"gasolina BR variou {variacao:.1%} em uma semana (limite {MAX_VARIACAO_SEMANAL:.0%})")

    if erros:
        raise ValidationError(erros)

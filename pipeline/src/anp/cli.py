"""Linha de comando: `anp backfill` (carga histórica, uma vez) e `anp update` (semanal)."""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from anp import config
from anp.aggregate import daily
from anp.clean import clean, load_raw
from anp.collect import download, fetch_text
from anp.export import export_all
from anp.ipca import get_ipca
from anp.links import discover_links, tipo_produto
from anp.merge import base_vazia, load_base, save_base, upsert
from anp.validate import validate


def _processar(url: str, base: pd.DataFrame, raw_dir: Path, session, *, forcar: bool = False,
               apagar: bool = False) -> pd.DataFrame:
    caminho = download(url, raw_dir, session, forcar=forcar)
    print(f"  processando {caminho.name}", flush=True)
    novo = daily(clean(load_raw(caminho)))
    if apagar:
        caminho.unlink()
    return upsert(base, novo)


def executar(modo: str, *, session, raw_dir: Path, processed_dir: Path, out_dir: Path, schemas_dir: Path,
             agora: datetime, apagar_brutos: bool = False) -> None:
    links = discover_links(fetch_text(config.ANP_PAGE_URL, session))
    if not links.ultimas_semanas:
        raise RuntimeError("Nenhum link de 'últimas 4 semanas' encontrado na página da ANP")
    tipos_qus = {tipo_produto(u) for u in links.ultimas_semanas}
    faltando_tipos = {"gasolina-etanol", "diesel-gnv"} - tipos_qus
    if faltando_tipos:
        raise RuntimeError(
            f"Faltam links de 'últimas 4 semanas' para: {', '.join(sorted(faltando_tipos))}. "
            "Sem isso, o produto correspondente pararia de ser atualizado silenciosamente."
        )

    if modo == "backfill":
        if not links.semestrais:
            raise RuntimeError("Nenhum arquivo semestral encontrado na página da ANP")
        base = base_vazia()
        maximo_anterior = None
        print(f"Semestrais: {len(links.semestrais)} arquivos", flush=True)
        for url in links.semestrais:
            base = _processar(url, base, raw_dir, session, apagar=apagar_brutos)
        ultima = base["data"].max()
        for mensal in links.mensais:
            if (mensal.ano, mensal.mes) > (ultima.year, ultima.month):
                base = _processar(mensal.url, base, raw_dir, session, apagar=apagar_brutos)
    elif modo == "update":
        base = load_base(processed_dir)
        if base.empty:
            raise RuntimeError(f"Base vazia em {processed_dir}: rode `anp backfill` primeiro")
        maximo_anterior = base["data"].max()
    else:
        raise ValueError(f"modo desconhecido: {modo}")

    minimos_novos = []
    for url in links.ultimas_semanas:
        caminho = download(url, raw_dir, session, forcar=True)
        print(f"  processando {caminho.name}", flush=True)
        novo = daily(clean(load_raw(caminho)))
        minimos_novos.append(novo["data"].min())
        base = upsert(base, novo)

    if modo == "update" and maximo_anterior is not None and minimos_novos:
        menor_novo = min(minimos_novos)
        limite = maximo_anterior + pd.Timedelta(days=7)
        if menor_novo > limite:
            raise RuntimeError(
                f"Lacuna nos dados: a base tinha até {maximo_anterior.date()}, mas as 'últimas 4 semanas' "
                f"só cobrem a partir de {menor_novo.date()}. Rode `anp backfill` para preencher a lacuna."
            )

    validate(base, maximo_anterior, agora.date())
    ipca, ipca_em_cache = get_ipca(session, processed_dir / "ipca.csv")
    export_all(base, ipca, ipca_em_cache, out_dir, schemas_dir, agora)
    save_base(base, processed_dir)
    print(f"OK: {len(base)} linhas na base, última data {base['data'].max().date()}", flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="anp", description="Pipeline de preços de combustíveis da ANP")
    parser.add_argument("modo", choices=["backfill", "update"])
    parser.add_argument("--raw-dir", type=Path, default=config.RAW_DIR)
    parser.add_argument("--processed-dir", type=Path, default=config.PROCESSED_DIR)
    parser.add_argument("--out-dir", type=Path, default=config.OUT_DIR)
    parser.add_argument("--schemas-dir", type=Path, default=config.SCHEMAS_DIR)
    parser.add_argument("--apagar-brutos", action="store_true",
                        help="apaga cada arquivo bruto depois de processado (economiza ~3 GB no backfill)")
    args = parser.parse_args(argv)
    try:
        with requests.Session() as session:
            executar(
                args.modo,
                session=session,
                raw_dir=args.raw_dir,
                processed_dir=args.processed_dir,
                out_dir=args.out_dir,
                schemas_dir=args.schemas_dir,
                agora=datetime.now(timezone.utc),
                apagar_brutos=args.apagar_brutos,
            )
    except Exception as erro:  # noqa: BLE001 — a mensagem vai para o log do Actions
        print(f"ERRO: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

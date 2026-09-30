import zipfile

import pandas as pd
import pytest
from helpers import CABECALHO, coletas, csv_anp, linha

from anp.clean import SchemaError, clean, load_raw


def _gravar(tmp_path, nome, conteudo: bytes):
    caminho = tmp_path / nome
    caminho.write_bytes(conteudo)
    return caminho


def test_load_raw_utf8_com_bom(tmp_path):
    p = _gravar(tmp_path, "a.csv", csv_anp([linha("DF", "GASOLINA", "02/01/2026", "6,19")]))
    df = load_raw(p)
    assert list(df.columns) == ["cnpj", "uf", "produto", "data", "preco"]
    assert df.iloc[0].to_dict() == {
        "cnpj": " 00.000.000/0001-00", "uf": "DF", "produto": "GASOLINA",
        "data": "02/01/2026", "preco": "6,19",
    }


def test_load_raw_latin1_com_acentos(tmp_path):
    conteudo = csv_anp([linha("CE", "GASOLINA", "01/07/2021", "5,499", revenda="COMERCIAL DE PETRÓLEO LTDA.")],
                       encoding="latin-1")
    df = load_raw(_gravar(tmp_path, "b.csv", conteudo))
    assert df.iloc[0]["uf"] == "CE"
    assert df.iloc[0]["preco"] == "5,499"


def test_load_raw_zip_sem_extensao_no_nome(tmp_path):
    zip_path = tmp_path / "dsan_2026_04-dados-abertos-precos-diesel-gnv"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("Preços semestrais - AUTOMOTIVOS_2026.01.csv",
                   csv_anp([linha("AC", "DIESEL S10", "02/01/2026", "7,99")]))
    df = load_raw(zip_path)
    assert df.iloc[0]["produto"] == "DIESEL S10"


def test_load_raw_campo_entre_aspas_com_ponto_e_virgula(tmp_path):
    p = _gravar(tmp_path, "c.csv", csv_anp([linha("SP", "ETANOL", "05/01/2026", "3,99", revenda='"POSTO; TESTE"')]))
    df = load_raw(p)
    assert df.iloc[0]["produto"] == "ETANOL"
    assert df.iloc[0]["preco"] == "3,99"


def test_load_raw_coluna_ausente_explica_o_problema(tmp_path):
    cabecalho_sem_preco = CABECALHO.replace(";Valor de Venda", "")
    p = _gravar(tmp_path, "d.csv", (cabecalho_sem_preco + "\r\n").encode("utf-8-sig"))
    with pytest.raises(SchemaError) as erro:
        load_raw(p)
    assert "Valor de Venda" in str(erro.value)
    assert "Encontradas" in str(erro.value)


def test_clean_mantem_so_os_tres_produtos_e_converte_tipos(tmp_path):
    linhas = coletas("12/01/2026", produtos=("GASOLINA", "ETANOL", "DIESEL S10", "GASOLINA ADITIVADA", "DIESEL", "GNV"),
                     ufs=["DF"])
    df = clean(load_raw(_gravar(tmp_path, "e.csv", csv_anp(linhas))))
    assert sorted(df["produto"]) == ["diesel_s10", "etanol", "gasolina"]
    assert df["data"].iloc[0] == pd.Timestamp("2026-01-12")
    assert df.set_index("produto")["preco"].to_dict() == {"gasolina": 5.0, "etanol": 3.5, "diesel_s10": 6.0}


def test_clean_remove_precos_fora_da_faixa_ufs_invalidas_e_datas_invalidas(tmp_path):
    linhas = [
        linha("DF", "GASOLINA", "12/01/2026", "0,49", cnpj="1"),
        linha("DF", "GASOLINA", "12/01/2026", "0,50", cnpj="2"),
        linha("DF", "GASOLINA", "12/01/2026", "20,00", cnpj="3"),
        linha("DF", "GASOLINA", "12/01/2026", "20,01", cnpj="4"),
        linha("XX", "GASOLINA", "12/01/2026", "6,00", cnpj="5"),
        linha("DF", "GASOLINA", "31/02/2026", "6,00", cnpj="6"),
        linha("DF", "GASOLINA", "12/01/2026", "abc", cnpj="7"),
    ]
    df = clean(load_raw(_gravar(tmp_path, "f.csv", csv_anp(linhas))))
    assert sorted(df["preco"]) == [0.50, 20.00]


def test_clean_remove_duplicata_do_mesmo_posto_mas_mantem_postos_diferentes(tmp_path):
    linhas = [
        linha("DF", "GASOLINA", "12/01/2026", "6,00", cnpj="11.111.111/0001-11"),
        linha("DF", "GASOLINA", "12/01/2026", "6,00", cnpj="11.111.111/0001-11"),
        linha("DF", "GASOLINA", "12/01/2026", "6,00", cnpj="22.222.222/0001-22"),
    ]
    df = clean(load_raw(_gravar(tmp_path, "g.csv", csv_anp(linhas))))
    assert len(df) == 2

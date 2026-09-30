from anp import config


def test_ufs_tem_27_siglas_unicas():
    assert len(config.UFS) == 27
    assert len(set(config.UFS)) == 27
    assert "DF" in config.UFS
    assert "BR" not in config.UFS


def test_produtos_mapeados_com_nomes_da_anp():
    assert config.PRODUTOS == {
        "GASOLINA": "gasolina",
        "ETANOL": "etanol",
        "DIESEL S10": "diesel_s10",
    }
    assert config.ORDEM_PRODUTOS == ["gasolina", "etanol", "diesel_s10"]


def test_caminhos_apontam_para_o_repositorio():
    assert (config.REPO_ROOT / "pipeline" / "pyproject.toml").exists()
    assert config.OUT_DIR == config.REPO_ROOT / "site" / "public" / "data"
    assert config.SCHEMAS_DIR == config.REPO_ROOT / "schemas"
    assert config.PROCESSED_DIR == config.REPO_ROOT / "pipeline" / "data" / "processed"


def test_limites():
    assert (config.PRECO_MIN, config.PRECO_MAX) == (0.50, 20.00)
    assert config.LIMIAR_ETANOL == 0.70
    assert config.MAX_VARIACAO_SEMANAL == 0.25

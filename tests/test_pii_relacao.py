"""Testes da camada de palavra de relacao do scrub de PII — so dado sintetico."""

from __future__ import annotations

from helpvet_gold.pii import scrub, varredura

_CANARIOS: frozenset[str] = frozenset()


# --- Positivos: relacao mantida, nome redigido ---


class TestRelacaoPositivos:
    def test_tutora_nome_composto(self) -> None:
        nome = "Ana" + " Beatriz"
        entrada = f"tutora {nome}"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "tutora [PESSOA_RELACIONADA]"
        assert nome not in saida

    def test_responsavel_nome_simples(self) -> None:
        nome = "Carlos"
        entrada = f"responsável {nome}"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "responsável [PESSOA_RELACIONADA]"
        assert nome not in saida

    def test_mae_nome_com_verbo_minusculo(self) -> None:
        nome = "Joana"
        entrada = f"Mãe {nome} relatou vômito"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "Mãe [PESSOA_RELACIONADA] relatou vômito"
        assert nome not in saida


# --- Positivos: varredura devolve classe "relacao" ---


class TestRelacaoVarredura:
    def test_varredura_tutora(self) -> None:
        nome = "Ana" + " Beatriz"
        entrada = f"tutora {nome}"
        achados = varredura(entrada)
        assert any(c == "relacao" for c, _ in achados)

    def test_varredura_responsavel(self) -> None:
        nome = "Carlos"
        entrada = f"responsável {nome}"
        achados = varredura(entrada)
        assert any(c == "relacao" for c, _ in achados)


# --- Negativos: TEM de sobreviver (scrub(x) == x, varredura(x) == []) ---


class TestRelacaoNegativos:
    def test_tutora_orientada_minusculo(self) -> None:
        texto = "tutora orientada a retornar"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_tutora_orientada_capitalizada_na_lista(self) -> None:
        texto = "Tutora Orientada"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_mae_relatou_minusculo(self) -> None:
        texto = "mãe relatou vômito"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_dona_de_casa_presente(self) -> None:
        texto = "dona de casa presente"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_rotulo_colado_pontuacao_estrutural(self) -> None:
        nome = "Ana"
        texto = f"responsável Assinado: {nome}"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []


# --- Reforco: lista de parada corta o nome no verbo capitalizado ---


class TestRelacaoReforco:
    def test_tutora_nome_orientada(self) -> None:
        nome = "Ana"
        entrada = f"tutora {nome} Orientada sobre o caso"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "tutora [PESSOA_RELACIONADA] Orientada sobre o caso"
        assert f"tutora {nome} " not in saida


# --- Idempotencia ---


class TestRelacaoIdempotencia:
    def test_idempotencia_relacao_autoria_clinico(self) -> None:
        nome_r = "Ana" + " Beatriz"
        nome_a = "Marcos" + " Silva"
        entrada = (
            f"tutora {nome_r} acompanhou. "
            f"Por {nome_a} em 05/03/2024. "
            "MV Diminuído em hemitórax esquerdo."
        )
        primeiro = scrub(entrada, _CANARIOS)
        segundo = scrub(primeiro, _CANARIOS)
        assert primeiro == segundo
        assert "[PESSOA_RELACIONADA]" in primeiro
        assert "MV Diminuído em hemitórax esquerdo" in primeiro
        assert nome_r not in primeiro


# --- Varredura nunca devolve o valor ---


class TestRelacaoNuncaDevolveValor:
    def test_nome_ausente_no_repr(self) -> None:
        nome = "Ana" + " Beatriz"
        entrada = f"tutora {nome}"
        achados = varredura(entrada)
        assert any(c == "relacao" for c, _ in achados)
        assert nome not in repr(achados)

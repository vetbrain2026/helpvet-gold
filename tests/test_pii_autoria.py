"""Testes da camada de autoria do scrub de PII — so dado sintetico."""

from __future__ import annotations

from helpvet_gold.pii import scrub, varredura

_CANARIOS: frozenset[str] = frozenset()


# --- Positivos: nome redigido, Por e data preservados ---


class TestAutoríaPositivos:
    def test_nome_composto(self) -> None:
        nome = "Genoveva" + " Prado" + " Lobato"
        entrada = f"Por {nome} em 16/01/2024"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "Por [PROFISSIONAL] em 16/01/2024"
        assert nome not in saida

    def test_caixa_alta_acento(self) -> None:
        nome = "EUFR" + "ÁSIA" + " TELLES"
        entrada = f"Por {nome} em 3/2/2023"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "Por [PROFISSIONAL] em 3/2/2023"
        assert nome not in saida

    def test_com_dr(self) -> None:
        nome = "Dr." + " Marcos" + " Silva"
        entrada = f"Por {nome} em 10/05/24"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "Por [PROFISSIONAL] em 10/05/24"
        assert nome not in saida


# --- Positivos: varredura devolve classe e posicao ---


class TestAutoríaVarredura:
    def test_varredura_nome_composto(self) -> None:
        nome = "Genoveva" + " Prado" + " Lobato"
        entrada = f"Por {nome} em 16/01/2024"
        achados = varredura(entrada)
        assert ("autoria", 0) in achados

    def test_varredura_caixa_alta(self) -> None:
        nome = "EUFR" + "ÁSIA" + " TELLES"
        entrada = f"Por {nome} em 3/2/2023"
        achados = varredura(entrada)
        assert ("autoria", 0) in achados

    def test_varredura_com_dr(self) -> None:
        nome = "Dr." + " Marcos" + " Silva"
        entrada = f"Por {nome} em 10/05/24"
        achados = varredura(entrada)
        assert ("autoria", 0) in achados


# --- Negativos: TEM de sobreviver (scrub(x) == x, varredura(x) == []) ---


class TestAutoríaNegativos:
    def test_por_via_oral(self) -> None:
        texto = "medicação por via oral em jejum"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_por_3_dias(self) -> None:
        texto = "tratamento por 3 dias"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_por_favor(self) -> None:
        texto = "Por favor retornar em breve"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_sem_por(self) -> None:
        texto = "consulta em 16/01/2024"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_por_volta(self) -> None:
        texto = "evoluiu bem; retorno por volta de 16/01/2024"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_por_epoca(self) -> None:
        texto = "Por época em 16/01/2024"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_por_area(self) -> None:
        texto = "Por área em 16/01/2024"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []


# --- Idempotencia ---


class TestAutoríaIdempotencia:
    def test_idempotencia_com_valor_clinico(self) -> None:
        nome = "Ana" + " Beatriz" + " Costa"
        entrada = f"Por {nome} em 05/03/2024. Hemograma WBC 8.500."
        primeiro = scrub(entrada, _CANARIOS)
        segundo = scrub(primeiro, _CANARIOS)
        assert primeiro == segundo
        assert "[PROFISSIONAL]" in primeiro
        assert "Hemograma WBC 8.500" in primeiro


# --- Varredura nunca devolve o valor ---


class TestAutoríaNuncaDevolveValor:
    def test_nome_ausente_no_repr(self) -> None:
        nome = "Genoveva" + " Prado" + " Lobato"
        entrada = f"Por {nome} em 16/01/2024"
        achados = varredura(entrada)
        assert any(c == "autoria" for c, _ in achados)
        assert nome not in repr(achados)

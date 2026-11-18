"""Testes da camada de prefixo clinico do scrub de PII — so dado sintetico."""

from __future__ import annotations

from helpvet_gold.pii import scrub, varredura

_CANARIOS: frozenset[str] = frozenset()


# --- Positivos: titulo mantido, nome redigido ---


class TestPrefixoPositivos:
    def test_dr_ponto_nome_composto(self) -> None:
        nome = "Marcos" + " Silva"
        entrada = f"Dr. {nome}"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "Dr. [PROFISSIONAL]"
        assert nome not in saida

    def test_dra_sem_ponto(self) -> None:
        nome = "Fernanda"
        entrada = f"Dra {nome}"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "Dra [PROFISSIONAL]"
        assert nome not in saida

    def test_med_vet(self) -> None:
        nome = "Paula" + " Souza"
        entrada = f"Méd. Vet. {nome}"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "Méd. Vet. [PROFISSIONAL]"
        assert nome not in saida


# --- Positivos: varredura devolve classe "prefixo" ---


class TestPrefixoVarredura:
    def test_varredura_dr(self) -> None:
        nome = "Marcos" + " Silva"
        entrada = f"Dr. {nome}"
        achados = varredura(entrada)
        assert any(c == "prefixo" for c, _ in achados)

    def test_varredura_dra(self) -> None:
        nome = "Fernanda"
        entrada = f"Dra {nome}"
        achados = varredura(entrada)
        assert any(c == "prefixo" for c, _ in achados)

    def test_varredura_med_vet(self) -> None:
        nome = "Paula" + " Souza"
        entrada = f"Méd. Vet. {nome}"
        achados = varredura(entrada)
        assert any(c == "prefixo" for c, _ in achados)


# --- Negativos: TEM de sobreviver (scrub(x) == x, varredura(x) == []) ---


class TestPrefixoNegativos:
    def test_mv_diminuido_minuscula(self) -> None:
        texto = "MV diminuído"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_mv_diminuido_maiuscula(self) -> None:
        texto = "MV Diminuído"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_murmúrio_vesicular(self) -> None:
        texto = "murmúrio vesicular preservado"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_dragao_de_komodo(self) -> None:
        texto = "Dragão de Komodo"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_paciente_drenado(self) -> None:
        texto = "paciente drenado em consulta"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_rotulo_responsavel_nao_redige(self) -> None:
        nome = "Carlos" + " Dias"
        texto = f"Méd. Vet. Responsável: {nome}"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []

    def test_torax_nao_redige(self) -> None:
        texto = "Dr. Tórax limpo à ausculta"
        assert scrub(texto, _CANARIOS) == texto
        assert varredura(texto) == []


# --- Positivos com lista de parada (nome redigido, verbo preservado) ---


class TestPrefixoParada:
    def test_dra_nome_avaliou(self) -> None:
        nome = "Souza"
        entrada = f"Dra. {nome} Avaliou o paciente"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "Dra. [PROFISSIONAL] Avaliou o paciente"
        assert nome not in saida

    def test_dr_nome_solicitou(self) -> None:
        nome = "Lima"
        entrada = f"Dr. {nome} Solicitou hemograma"
        saida = scrub(entrada, _CANARIOS)
        assert saida == "Dr. [PROFISSIONAL] Solicitou hemograma"
        assert nome not in saida


# --- Idempotencia ---


class TestPrefixoIdempotencia:
    def test_idempotencia_prefixo_autoria_clinico(self) -> None:
        nome_p = "Marcos" + " Silva"
        nome_a = "Ana" + " Beatriz"
        entrada = (
            f"Dr. {nome_p} prescreveu. "
            f"Por {nome_a} em 05/03/2024. "
            "MV Diminuído em hemitórax esquerdo."
        )
        primeiro = scrub(entrada, _CANARIOS)
        segundo = scrub(primeiro, _CANARIOS)
        assert primeiro == segundo
        assert "[PROFISSIONAL]" in primeiro
        assert "MV Diminuído em hemitórax esquerdo" in primeiro


# --- Varredura nunca devolve o valor ---


class TestPrefixoNuncaDevolveValor:
    def test_nome_ausente_no_repr(self) -> None:
        nome = "Marcos" + " Silva"
        entrada = f"Dr. {nome}"
        achados = varredura(entrada)
        assert any(c == "prefixo" for c, _ in achados)
        assert nome not in repr(achados)

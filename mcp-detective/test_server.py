import pytest

from server import GestorCasos, cargar_casos


@pytest.fixture
def gestor() -> GestorCasos:
    return GestorCasos(cargar_casos())


def test_listar_casos_devuelve_los_tres_casos_esperados(
    gestor: GestorCasos,
) -> None:
    casos = gestor.listar_casos()

    assert casos == [
        {"id": "INC-001", "sistema": "portal_acceso", "cantidad_eventos": 2},
        {"id": "INC-002", "sistema": "portal_acceso", "cantidad_eventos": 6},
        {"id": "INC-003", "sistema": "panel_administracion", "cantidad_eventos": 5},
    ]


def test_consultar_eventos_de_caso_inexistente_lanza_value_error(
    gestor: GestorCasos,
) -> None:
    with pytest.raises(ValueError, match="No existe el caso 'INC-999'"):
        gestor.consultar_eventos("INC-999")


def test_registrar_alerta_valida_devuelve_el_resultado_esperado(
    gestor: GestorCasos,
) -> None:
    alerta = gestor.registrar_alerta("INC-001", "medio", "Actividad inusual")

    assert alerta == {
        "caso_id": "INC-001",
        "nivel": "medio",
        "motivo": "Actividad inusual",
        "estado": "registrada",
    }


def test_registrar_alerta_rechaza_un_duplicado_en_la_misma_instancia(
    gestor: GestorCasos,
) -> None:
    gestor.registrar_alerta("INC-001", "bajo", "Primera alerta")

    with pytest.raises(ValueError, match="Ya existe una alerta"):
        gestor.registrar_alerta("INC-001", "alto", "Alerta duplicada")


@pytest.mark.parametrize("nivel", ["BAJO", "urgente", ""])
def test_registrar_alerta_rechaza_niveles_no_permitidos(
    gestor: GestorCasos,
    nivel: str,
) -> None:
    with pytest.raises(ValueError, match="El nivel debe ser exactamente"):
        gestor.registrar_alerta("INC-001", nivel, "Motivo válido")


@pytest.mark.parametrize("motivo", ["", "   ", "\t\n"])
def test_registrar_alerta_rechaza_motivos_en_blanco(
    gestor: GestorCasos,
    motivo: str,
) -> None:
    with pytest.raises(ValueError, match="El motivo no puede estar vacío"):
        gestor.registrar_alerta("INC-001", "medio", motivo)


def test_registrar_alerta_rechaza_casos_inexistentes(
    gestor: GestorCasos,
) -> None:
    with pytest.raises(ValueError, match="No existe el caso 'INC-999'"):
        gestor.registrar_alerta("INC-999", "medio", "Motivo válido")

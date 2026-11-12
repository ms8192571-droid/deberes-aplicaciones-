import json
from pathlib import Path
from typing import Any

from mcp.server import MCPServer


def cargar_casos() -> dict[str, dict[str, Any]]:
    """Carga los casos desde el archivo ubicado junto a este servidor."""
    ruta_casos = Path(__file__).with_name("casos.json")
    with ruta_casos.open(encoding="utf-8") as archivo:
        return json.load(archivo)


class GestorCasos:
    """Contiene la lógica de consulta de casos y registro de alertas."""

    def __init__(self, casos: dict[str, dict[str, Any]]) -> None:
        self._casos = casos
        self._alertas: dict[str, dict[str, str]] = {}

    def listar_casos(self) -> list[dict]:
        """Devuelve el identificador, sistema y cantidad de eventos de cada caso."""
        return [
            {
                "id": caso_id,
                "sistema": caso["sistema"],
                "cantidad_eventos": len(caso["eventos"]),
            }
            for caso_id, caso in self._casos.items()
        ]

    def consultar_eventos(self, caso_id: str) -> list[dict]:
        """Devuelve los registros exactos del caso indicado."""
        if caso_id not in self._casos:
            raise ValueError(f"No existe el caso '{caso_id}'.")
        return self._casos[caso_id]["eventos"]

    def registrar_alerta(self, caso_id: str, nivel: str, motivo: str) -> dict:
        """Valida y guarda una única alerta en memoria para el caso."""
        if caso_id not in self._casos:
            raise ValueError(f"No existe el caso '{caso_id}'.")
        if nivel not in {"bajo", "medio", "alto"}:
            raise ValueError("El nivel debe ser exactamente 'bajo', 'medio' o 'alto'.")
        if not motivo.strip():
            raise ValueError("El motivo no puede estar vacío ni contener solo espacios.")
        if caso_id in self._alertas:
            raise ValueError(f"Ya existe una alerta registrada para el caso '{caso_id}'.")

        alerta = {
            "caso_id": caso_id,
            "nivel": nivel,
            "motivo": motivo,
            "estado": "registrada",
        }
        self._alertas[caso_id] = alerta
        return alerta.copy()


_gestor = GestorCasos(cargar_casos())
mcp = MCPServer("mcp-detective")


@mcp.tool()
def listar_casos() -> list[dict]:
    """Devuelve los casos disponibles con sistema y cantidad de eventos."""
    return _gestor.listar_casos()


@mcp.tool()
def consultar_eventos(caso_id: str) -> list[dict]:
    """Devuelve los registros exactos asociados a un identificador de caso."""
    return _gestor.consultar_eventos(caso_id)


@mcp.tool()
def registrar_alerta(caso_id: str, nivel: str, motivo: str) -> dict:
    """Registra una alerta válida en memoria, como máximo una por caso."""
    return _gestor.registrar_alerta(caso_id, nivel, motivo)


if __name__ == "__main__":
    mcp.run(transport="stdio")

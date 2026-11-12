from typing import Any, Dict


class API:
    """API mínima que pywebview expone a la interfaz."""

    def obtener_estado(self) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "Backend conectado.",
        }

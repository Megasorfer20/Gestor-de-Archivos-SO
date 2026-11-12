import logging
from typing import Any, Callable, Dict, Optional

from clases.servicios.gestor_archivos import ErrorGestorArchivos, GestorArchivos


logger = logging.getLogger(__name__)


class API:
    """Métodos de pywebview que conectan Vue con los servicios de clases."""

    def __init__(self, gestor: Optional[GestorArchivos] = None) -> None:
        self._gestor = gestor if gestor is not None else GestorArchivos()

    def _ejecutar(self, operacion: Callable[[], Any]) -> Dict[str, Any]:
        try:
            return {"success": True, "data": operacion()}
        except ErrorGestorArchivos as error:
            return {"success": False, "message": str(error)}
        except Exception:
            logger.exception("Error inesperado en una operación del gestor.")
            return {
                "success": False,
                "message": "Ocurrió un error inesperado. Revisa los permisos y vuelve a intentar.",
            }

    def obtener_estado(self) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "Gestor de archivos conectado.",
            "data": {"root": "directory"},
        }

    def listar_directorio(self, ruta: str = "") -> Dict[str, Any]:
        return self._ejecutar(lambda: self._gestor.listar_directorio(ruta))

    def listar_carpetas(self) -> Dict[str, Any]:
        return self._ejecutar(self._gestor.listar_carpetas)

    def crear_directorio(self, directorio: str, nombre: str) -> Dict[str, Any]:
        return self._ejecutar(
            lambda: self._gestor.crear_directorio(directorio, nombre)
        )

    def crear_archivo_texto(self, directorio: str, nombre: str) -> Dict[str, Any]:
        return self._ejecutar(
            lambda: self._gestor.crear_archivo_texto(directorio, nombre)
        )

    def leer_archivo(self, ruta: str) -> Dict[str, Any]:
        return self._ejecutar(lambda: self._gestor.leer_archivo(ruta))

    def guardar_archivo(self, ruta: str, contenido: str) -> Dict[str, Any]:
        return self._ejecutar(
            lambda: self._gestor.guardar_archivo(ruta, contenido)
        )

    def agregar_informacion(self, ruta: str, contenido: str) -> Dict[str, Any]:
        return self._ejecutar(
            lambda: self._gestor.agregar_informacion(ruta, contenido)
        )

    def renombrar_archivo(self, ruta: str, nuevo_nombre: str) -> Dict[str, Any]:
        return self._ejecutar(
            lambda: self._gestor.renombrar_archivo(ruta, nuevo_nombre)
        )

    def copiar_archivo(self, ruta: str, ruta_destino: str) -> Dict[str, Any]:
        return self._ejecutar(
            lambda: self._gestor.copiar_archivo(ruta, ruta_destino)
        )

    def eliminar_archivo(self, ruta: str, confirmar: bool) -> Dict[str, Any]:
        return self._ejecutar(
            lambda: self._gestor.eliminar_archivo(ruta, confirmar)
        )

    def obtener_informacion(self, ruta: str) -> Dict[str, Any]:
        return self._ejecutar(lambda: self._gestor.obtener_informacion(ruta))

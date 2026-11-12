import logging
import os
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List, Optional


class ErrorGestorArchivos(Exception):
    """Error esperado durante una operación del gestor."""


class GestorArchivos:
    """Gestiona archivos únicamente dentro de su directorio de trabajo."""

    _NOMBRE_RESERVADO = re.compile(
        r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?$",
        re.IGNORECASE,
    )
    _CARACTERES_INVALIDOS = set('<>:"/\\|?*')

    def __init__(self, raiz: Optional[Path] = None) -> None:
        self._logger = logging.getLogger(__name__)
        proyecto = Path(__file__).resolve().parents[2]
        self.raiz = Path(raiz) if raiz is not None else proyecto / "directory"
        try:
            if self.raiz.is_symlink():
                raise ErrorGestorArchivos(
                    "La carpeta de trabajo no puede ser un enlace simbólico."
                )
            self.raiz.mkdir(parents=True, exist_ok=True)
            self.raiz = self.raiz.resolve(strict=True)
            if not self.raiz.is_dir():
                raise ErrorGestorArchivos("La carpeta de trabajo no es un directorio.")
        except ErrorGestorArchivos:
            raise
        except OSError as error:
            raise ErrorGestorArchivos(
                f"No se pudo preparar la carpeta de trabajo: {error}"
            ) from error

    def _resolver(self, ruta: str, permitir_raiz: bool = False) -> Path:
        if not isinstance(ruta, str):
            raise ErrorGestorArchivos("La ruta debe ser texto.")
        try:
            ruta.encode("utf-8")
        except UnicodeError as error:
            raise ErrorGestorArchivos("La ruta contiene caracteres no válidos.") from error

        normalizada = ruta.replace("\\", "/")
        if not normalizada:
            if permitir_raiz:
                return self.raiz
            raise ErrorGestorArchivos("Indica una ruta dentro de la carpeta de trabajo.")

        ruta_windows = PureWindowsPath(normalizada)
        partes = normalizada.split("/")
        if (
            ruta_windows.is_absolute()
            or ruta_windows.drive
            or normalizada.startswith("/")
            or any(parte in ("", ".", "..") for parte in partes)
        ):
            raise ErrorGestorArchivos(
                "La ruta debe ser relativa y no puede salir de la carpeta de trabajo."
            )

        candidato = self.raiz.joinpath(*partes)
        try:
            actual = self.raiz
            for parte in partes:
                actual = actual / parte
                if actual.is_symlink():
                    raise ErrorGestorArchivos(
                        "No se permiten enlaces simbólicos en las rutas gestionadas."
                    )

            resuelto = candidato.resolve(strict=False)
            resuelto.relative_to(self.raiz)
        except ErrorGestorArchivos:
            raise
        except (OSError, ValueError) as error:
            raise ErrorGestorArchivos(
                "La ruta indicada no es válida dentro de la carpeta de trabajo."
            ) from error
        return candidato

    def _resolver_directorio(self, ruta: str, permitir_raiz: bool = False) -> Path:
        directorio = self._resolver(ruta, permitir_raiz)
        if not directorio.exists():
            raise ErrorGestorArchivos("La carpeta indicada no existe.")
        if not directorio.is_dir():
            raise ErrorGestorArchivos("La ruta indicada no es una carpeta.")
        return directorio

    @classmethod
    def _validar_nombre(cls, nombre: str) -> str:
        if not isinstance(nombre, str):
            raise ErrorGestorArchivos("El nombre debe ser texto.")
        try:
            nombre.encode("utf-8")
        except UnicodeError as error:
            raise ErrorGestorArchivos("El nombre contiene caracteres no válidos.") from error
        if (
            not nombre
            or not nombre.strip()
            or nombre in (".", "..")
            or any(caracter in cls._CARACTERES_INVALIDOS for caracter in nombre)
            or any(ord(caracter) < 32 for caracter in nombre)
            or nombre.endswith((".", " "))
            or cls._NOMBRE_RESERVADO.fullmatch(nombre)
        ):
            raise ErrorGestorArchivos(
                "El nombre está vacío o contiene caracteres no permitidos."
            )
        return nombre

    def _resolver_archivo(self, ruta: str, solo_txt: bool = False) -> Path:
        archivo = self._resolver(ruta)
        if not archivo.exists():
            raise ErrorGestorArchivos("El archivo indicado no existe.")
        if not archivo.is_file():
            raise ErrorGestorArchivos("La ruta indicada no es un archivo.")
        try:
            if archivo.stat().st_nlink > 1:
                raise ErrorGestorArchivos(
                    "No se permiten archivos enlazados fuera de la carpeta de trabajo."
                )
        except OSError as error:
            raise ErrorGestorArchivos(
                f"No se pudo validar el archivo: {error}"
            ) from error
        if solo_txt and archivo.suffix.lower() != ".txt":
            raise ErrorGestorArchivos("Esta operación solo está disponible para archivos .txt.")
        return archivo

    @staticmethod
    def _fecha_modificacion(ruta: Path) -> str:
        return datetime.fromtimestamp(ruta.stat().st_mtime).astimezone().isoformat(
            timespec="seconds"
        )

    @staticmethod
    def _nombre_relativo(ruta: Path, raiz: Path) -> str:
        return ruta.relative_to(raiz).as_posix()

    def listar_directorio(self, ruta: str = "") -> List[Dict[str, Any]]:
        directorio = self._resolver_directorio(ruta, permitir_raiz=True)
        try:
            entradas = []
            for entrada in directorio.iterdir():
                if entrada == self.raiz / ".gitkeep":
                    continue
                if entrada.is_symlink():
                    entradas.append(
                        {
                            "name": entrada.name,
                            "path": self._nombre_relativo(entrada, self.raiz),
                            "type": "link",
                            "size": None,
                            "modified": None,
                        }
                    )
                    continue
                tipo = "directory" if entrada.is_dir() else "file"
                stat = entrada.stat()
                if tipo == "file" and stat.st_nlink > 1:
                    entradas.append(
                        {
                            "name": entrada.name,
                            "path": self._nombre_relativo(entrada, self.raiz),
                            "type": "link",
                            "size": None,
                            "modified": None,
                        }
                    )
                    continue
                entradas.append(
                    {
                        "name": entrada.name,
                        "path": self._nombre_relativo(entrada, self.raiz),
                        "type": tipo,
                        "size": None if tipo == "directory" else stat.st_size,
                        "modified": datetime.fromtimestamp(
                            stat.st_mtime
                        ).astimezone().isoformat(timespec="seconds"),
                    }
                )
            return sorted(
                entradas,
                key=lambda entrada: (
                    entrada["type"] != "directory",
                    entrada["name"].casefold(),
                ),
            )
        except ErrorGestorArchivos:
            raise
        except OSError as error:
            raise ErrorGestorArchivos(f"No se pudo listar la carpeta: {error}") from error

    def listar_carpetas(self) -> List[Dict[str, str]]:
        carpetas = [{"path": "", "name": "directory (raíz)"}]
        pendientes = [""]
        while pendientes:
            ruta_padre = pendientes.pop()
            for entrada in self.listar_directorio(ruta_padre):
                if entrada["type"] == "directory":
                    carpeta = {"path": entrada["path"], "name": entrada["path"]}
                    carpetas.append(carpeta)
                    pendientes.append(entrada["path"])
        return [carpetas[0]] + sorted(
            carpetas[1:],
            key=lambda carpeta: (carpeta["name"].casefold(), carpeta["path"]),
        )

    def crear_directorio(self, directorio: str, nombre: str) -> Dict[str, str]:
        padre = self._resolver_directorio(directorio, permitir_raiz=True)
        nombre = self._validar_nombre(nombre)
        nuevo = padre / nombre
        try:
            nuevo.mkdir()
            return {"path": self._nombre_relativo(nuevo, self.raiz)}
        except FileExistsError as error:
            raise ErrorGestorArchivos("Ya existe un archivo o carpeta con ese nombre.") from error
        except OSError as error:
            raise ErrorGestorArchivos(f"No se pudo crear la carpeta: {error}") from error

    def crear_archivo_texto(self, directorio: str, nombre: str) -> Dict[str, str]:
        padre = self._resolver_directorio(directorio, permitir_raiz=True)
        nombre = self._validar_nombre(nombre)
        if Path(nombre).suffix.lower() != ".txt":
            raise ErrorGestorArchivos("El archivo debe tener la extensión .txt.")
        archivo = padre / nombre
        try:
            with archivo.open("x", encoding="utf-8", newline=""):
                pass
            return {"path": self._nombre_relativo(archivo, self.raiz)}
        except FileExistsError as error:
            raise ErrorGestorArchivos("Ya existe un archivo o carpeta con ese nombre.") from error
        except OSError as error:
            raise ErrorGestorArchivos(f"No se pudo crear el archivo: {error}") from error

    def leer_archivo(self, ruta: str) -> Dict[str, str]:
        archivo = self._resolver_archivo(ruta, solo_txt=True)
        try:
            return {"path": self._nombre_relativo(archivo, self.raiz), "content": archivo.read_text(encoding="utf-8")}
        except (OSError, UnicodeError) as error:
            raise ErrorGestorArchivos(f"No se pudo leer el archivo de texto: {error}") from error

    def _escribir_atomico(self, archivo: Path, contenido: str) -> None:
        temporal: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="",
                dir=archivo.parent,
                prefix=".gestor-",
                suffix=".tmp",
                delete=False,
            ) as temporal_abierto:
                temporal = temporal_abierto.name
                temporal_abierto.write(contenido)
                temporal_abierto.flush()
                os.fsync(temporal_abierto.fileno())
            os.replace(temporal, archivo)
            temporal = None
        except (OSError, UnicodeError) as error:
            raise ErrorGestorArchivos(f"No se pudo guardar el archivo: {error}") from error
        finally:
            if temporal is not None:
                try:
                    Path(temporal).unlink(missing_ok=True)
                except OSError:
                    self._logger.exception(
                        "No se pudo eliminar el archivo temporal %s.", temporal
                    )

    def guardar_archivo(self, ruta: str, contenido: str) -> Dict[str, str]:
        archivo = self._resolver_archivo(ruta, solo_txt=True)
        if not isinstance(contenido, str):
            raise ErrorGestorArchivos("El contenido debe ser texto.")
        self._escribir_atomico(archivo, contenido)
        return {"path": self._nombre_relativo(archivo, self.raiz)}

    def agregar_informacion(self, ruta: str, contenido: str) -> Dict[str, str]:
        archivo = self._resolver_archivo(ruta, solo_txt=True)
        if not isinstance(contenido, str) or not contenido:
            raise ErrorGestorArchivos("Escribe la información que quieres agregar.")
        try:
            existente = archivo.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ErrorGestorArchivos(f"No se pudo leer el archivo de texto: {error}") from error
        self._escribir_atomico(archivo, existente + contenido)
        return {"path": self._nombre_relativo(archivo, self.raiz)}

    def renombrar_archivo(self, ruta: str, nuevo_nombre: str) -> Dict[str, str]:
        origen = self._resolver_archivo(ruta)
        nuevo_nombre = self._validar_nombre(nuevo_nombre)
        extension = origen.suffix
        if extension:
            if nuevo_nombre.casefold().endswith(extension.casefold()):
                nuevo_nombre = nuevo_nombre[: -len(extension)]
            elif Path(nuevo_nombre).suffix:
                raise ErrorGestorArchivos(
                    "No cambies la extensión del archivo; modifica solo el nombre."
                )
            nuevo_nombre = self._validar_nombre(nuevo_nombre) + extension
        destino = origen.with_name(nuevo_nombre)
        if nuevo_nombre == origen.name:
            raise ErrorGestorArchivos("El archivo ya tiene ese nombre.")
        try:
            if os.name == "nt":
                os.rename(origen, destino)
            else:
                os.link(origen, destino)
                try:
                    origen.unlink()
                except OSError:
                    destino.unlink(missing_ok=True)
                    raise
            return {"path": self._nombre_relativo(destino, self.raiz)}
        except FileExistsError as error:
            raise ErrorGestorArchivos("Ya existe un archivo o carpeta con ese nombre.") from error
        except OSError as error:
            raise ErrorGestorArchivos(f"No se pudo renombrar el archivo: {error}") from error

    def copiar_archivo(self, ruta: str, ruta_destino: str) -> Dict[str, str]:
        origen = self._resolver_archivo(ruta)
        destino = self._resolver(ruta_destino)
        padre = self._resolver_directorio(
            self._nombre_relativo(destino.parent, self.raiz) if destino.parent != self.raiz else "",
            permitir_raiz=True,
        )
        nombre = self._validar_nombre(destino.name)
        destino = padre / nombre
        try:
            with origen.open("rb") as archivo_origen, destino.open("xb") as archivo_destino:
                shutil.copyfileobj(archivo_origen, archivo_destino)
                archivo_destino.flush()
                os.fsync(archivo_destino.fileno())
            shutil.copystat(origen, destino)
            return {"path": self._nombre_relativo(destino, self.raiz)}
        except FileExistsError as error:
            raise ErrorGestorArchivos("Ya existe un archivo o carpeta con ese nombre.") from error
        except OSError as error:
            try:
                destino.unlink(missing_ok=True)
            except OSError:
                self._logger.exception(
                    "No se pudo limpiar la copia incompleta %s.", destino
                )
            raise ErrorGestorArchivos(f"No se pudo copiar el archivo: {error}") from error

    def eliminar_archivo(self, ruta: str, confirmar: bool) -> Dict[str, str]:
        if confirmar is not True:
            raise ErrorGestorArchivos("Confirma la eliminación para continuar.")
        archivo = self._resolver_archivo(ruta)
        try:
            archivo.unlink()
            return {"path": ruta}
        except OSError as error:
            raise ErrorGestorArchivos(f"No se pudo eliminar el archivo: {error}") from error

    def obtener_informacion(self, ruta: str) -> Dict[str, Any]:
        archivo = self._resolver_archivo(ruta)
        try:
            stat = archivo.stat()
            return {
                "name": archivo.name,
                "path": self._nombre_relativo(archivo, self.raiz),
                "size": stat.st_size,
                "modified": self._fecha_modificacion(archivo),
                "type": "file",
            }
        except OSError as error:
            raise ErrorGestorArchivos(f"No se pudo consultar el archivo: {error}") from error

import argparse
import logging
from pathlib import Path
from typing import Optional, Sequence

from API import API


PROJECT_ROOT = Path(__file__).resolve().parent
DEV_SERVER_URL = "http://localhost:5173"


def _load_webview():
    import webview

    return webview


def resolve_frontend(use_dev_server: bool, project_root: Path = PROJECT_ROOT) -> str:
    if use_dev_server:
        return DEV_SERVER_URL

    frontend = project_root / "interface" / "dist" / "index.html"
    if not frontend.is_file():
        raise FileNotFoundError(
            f"No se encontró el build del frontend: {frontend}. "
            "Genéralo ejecutando 'npm run build' dentro de interface/."
        )
    return str(frontend.resolve())


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Inicia el gestor de archivos.")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Carga el frontend desde el servidor Vite en http://localhost:5173.",
    )
    arguments = parser.parse_args(argv)

    try:
        frontend = resolve_frontend(arguments.dev, PROJECT_ROOT)
        api = API()
        webview = _load_webview()
        webview.create_window(
            "Gestor de archivos",
            frontend,
            js_api=api,
            min_size=(900, 600),
        )
        webview.start(debug=arguments.dev, http_server=not arguments.dev)
    except Exception as error:
        logging.exception("No se pudo iniciar el gestor de archivos.")
        raise SystemExit(
            "No se pudo iniciar el gestor. En modo desarrollo inicia Vite; "
            "en modo producción genera el frontend con 'npm run build'."
        ) from error


if __name__ == "__main__":
    main()

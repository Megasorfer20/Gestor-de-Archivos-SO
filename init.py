import logging

import webview

from API import API


def main() -> None:
    try:
        api = API()

        webview.create_window(
            "Gestor de archivos",
            "http://localhost:5173",
            js_api=api,
            min_size=(900, 600),
        )
        webview.start(debug=True, http_server=True)
    except Exception as error:
        logging.exception("No se pudo iniciar el gestor de archivos.")
        raise SystemExit(
            "No se pudo iniciar el gestor. Verifica pywebview y que Vite esté activo."
        ) from error


if __name__ == "__main__":
    main()
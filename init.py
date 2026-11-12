import webview

from API import API


def main() -> None:
    api = API()

    webview.create_window("Plantilla de proyecto", "http://localhost:5173", js_api=api)
    webview.start(debug=True, http_server=True)


if __name__ == "__main__":
    main()
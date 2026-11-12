import webview
import os
from API import API


def main() -> None:
    if not os.path.dirname("directory"):
        os.mkdir("directory")
    api = API()

    webview.create_window("Plantilla de proyecto", "http://localhost:5173", js_api=api)
    webview.start(debug=True, http_server=True)


if __name__ == "__main__":
    main()
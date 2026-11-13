import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import Mock, patch

import init


class InitTests(unittest.TestCase):
    def test_resolve_frontend_uses_built_index_by_default(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            frontend = root / "interface" / "dist" / "index.html"
            frontend.parent.mkdir(parents=True)
            frontend.write_text("<html></html>", encoding="utf-8")

            self.assertEqual(init.resolve_frontend(False, root), str(frontend.resolve()))

    def test_resolve_frontend_reports_when_build_is_missing(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(FileNotFoundError, "npm run build"):
                init.resolve_frontend(False, Path(temporary))

    def test_resolve_frontend_uses_vite_only_in_dev_mode(self):
        self.assertEqual(init.resolve_frontend(True, Path("missing")), init.DEV_SERVER_URL)

    def test_production_startup_loads_dist_and_connects_python_api(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            frontend = root / "interface" / "dist" / "index.html"
            frontend.parent.mkdir(parents=True)
            frontend.write_text("<html></html>", encoding="utf-8")
            api = object()

            with ExitStack() as stack:
                stack.enter_context(patch.object(init, "PROJECT_ROOT", root))
                stack.enter_context(patch.object(init, "API", return_value=api))
                load_webview = stack.enter_context(
                    patch.object(init, "_load_webview", return_value=Mock())
                )
                init.main([])

            webview = load_webview.return_value
            self.assertEqual(webview.create_window.call_args.args[1], str(frontend.resolve()))
            self.assertIs(webview.create_window.call_args.kwargs["js_api"], api)
            webview.start.assert_called_once_with(debug=False, http_server=True)

    def test_dev_startup_uses_vite_and_keeps_api_connected(self):
        api = object()
        with ExitStack() as stack:
            stack.enter_context(patch.object(init, "API", return_value=api))
            load_webview = stack.enter_context(
                patch.object(init, "_load_webview", return_value=Mock())
            )
            init.main(["--dev"])

        webview = load_webview.return_value
        self.assertEqual(webview.create_window.call_args.args[1], init.DEV_SERVER_URL)
        self.assertIs(webview.create_window.call_args.kwargs["js_api"], api)
        webview.start.assert_called_once_with(debug=True, http_server=False)


if __name__ == "__main__":
    unittest.main()

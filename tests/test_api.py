import unittest

from API import API


class APITests(unittest.TestCase):
    def test_api_exposes_only_a_working_connection_check(self):
        api = API()

        self.assertEqual(
            api.obtener_estado(),
            {"success": True, "message": "Backend conectado."},
        )
        self.assertEqual(
            [name for name in dir(api) if not name.startswith("_")],
            ["obtener_estado"],
        )


if __name__ == "__main__":
    unittest.main()

import tempfile
import unittest
from pathlib import Path

from API import API
from clases.servicios.gestor_archivos import GestorArchivos


class APITests(unittest.TestCase):
    def setUp(self):
        self.directorio_temporal = tempfile.TemporaryDirectory()
        raiz = Path(self.directorio_temporal.name) / "directory"
        self.api = API(GestorArchivos(raiz))

    def tearDown(self):
        self.directorio_temporal.cleanup()

    def test_api_expone_operaciones_y_delega_en_servicio(self):
        self.assertEqual(self.api.obtener_estado()["data"]["root"], "directory")
        self.assertTrue(self.api.crear_directorio("", "Documentos")["success"])
        self.assertTrue(
            self.api.crear_archivo_texto("Documentos", "nota.txt")["success"]
        )
        self.assertTrue(
            self.api.guardar_archivo("Documentos/nota.txt", "Hola")["success"]
        )
        self.assertEqual(
            self.api.leer_archivo("Documentos/nota.txt")["data"]["content"],
            "Hola",
        )
        self.assertTrue(
            self.api.agregar_informacion("Documentos/nota.txt", " mundo")["success"]
        )
        self.assertEqual(
            self.api.obtener_informacion("Documentos/nota.txt")["data"]["size"],
            10,
        )
        self.assertEqual(
            self.api.listar_directorio("Documentos")["data"][0]["name"],
            "nota.txt",
        )
        self.assertTrue(
            self.api.copiar_archivo(
                "Documentos/nota.txt", "Documentos/copia.txt"
            )["success"]
        )
        self.assertTrue(
            self.api.renombrar_archivo(
                "Documentos/copia.txt", "renombrado.txt"
            )["success"]
        )
        self.assertTrue(
            self.api.eliminar_archivo("Documentos/renombrado.txt", True)["success"]
        )

    def test_api_devuelve_errores_validos_para_la_interfaz(self):
        duplicado = self.api.crear_directorio("", "Documentos")
        self.assertTrue(duplicado["success"])
        respuesta = self.api.crear_directorio("", "Documentos")
        self.assertEqual(respuesta["success"], False)
        self.assertIn("Ya existe", respuesta["message"])

        with self.assertLogs("API", level="ERROR"):
            inesperado = API(gestor=object()).listar_directorio("")
        self.assertEqual(inesperado["success"], False)
        self.assertIn("error inesperado", inesperado["message"])


if __name__ == "__main__":
    unittest.main()

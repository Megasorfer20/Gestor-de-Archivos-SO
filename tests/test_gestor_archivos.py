import os
import tempfile
import unittest
from pathlib import Path

from clases.servicios.gestor_archivos import ErrorGestorArchivos, GestorArchivos


class GestorArchivosTests(unittest.TestCase):
    def setUp(self):
        self.directorio_temporal = tempfile.TemporaryDirectory()
        self.raiz = Path(self.directorio_temporal.name) / "directory"
        self.gestor = GestorArchivos(self.raiz)

    def tearDown(self):
        self.directorio_temporal.cleanup()

    def test_crea_directorios_y_archivos_sin_sobrescribir(self):
        self.assertEqual(
            self.gestor.crear_directorio("", "Documentos"),
            {"path": "Documentos"},
        )
        self.gestor.crear_archivo_texto("Documentos", "notas.txt")
        self.assertEqual((self.raiz / "Documentos" / "notas.txt").read_text(), "")

        with self.assertRaisesRegex(ErrorGestorArchivos, "Ya existe"):
            self.gestor.crear_directorio("", "Documentos")
        with self.assertRaisesRegex(ErrorGestorArchivos, "Ya existe"):
            self.gestor.crear_archivo_texto("Documentos", "notas.txt")

    def test_rechaza_nombres_y_rutas_fuera_de_la_carpeta_de_trabajo(self):
        for nombre in ("", "..", "sub/carpeta", "CON.txt", "archivo?.txt"):
            with self.subTest(nombre=nombre), self.assertRaises(ErrorGestorArchivos):
                self.gestor.crear_archivo_texto("", nombre)

        for ruta in ("../afuera.txt", "C:\\privado.txt", "/tmp/afuera.txt", "a/../b.txt"):
            with self.subTest(ruta=ruta), self.assertRaises(ErrorGestorArchivos):
                self.gestor.leer_archivo(ruta)

    def test_guarda_agrega_y_lee_texto_utf8(self):
        self.gestor.crear_archivo_texto("", "notas.txt")
        self.gestor.guardar_archivo("notas.txt", "Primera línea\n")
        self.gestor.agregar_informacion("notas.txt", "Información adicional: ñ\n")

        self.assertEqual(
            self.gestor.leer_archivo("notas.txt")["content"],
            "Primera línea\nInformación adicional: ñ\n",
        )
        with self.assertRaisesRegex(ErrorGestorArchivos, "Escribe"):
            self.gestor.agregar_informacion("notas.txt", "")
        (self.raiz / "imagen.png").write_bytes(b"contenido")
        with self.assertRaisesRegex(ErrorGestorArchivos, r"\.txt"):
            self.gestor.guardar_archivo("imagen.png", "texto")

    def test_renombra_y_copia_sin_reemplazar_destinos(self):
        self.gestor.crear_archivo_texto("", "original.txt")
        self.gestor.guardar_archivo("original.txt", "contenido")
        self.assertEqual(
            self.gestor.renombrar_archivo("original.txt", "renombrado.txt")["path"],
            "renombrado.txt",
        )
        self.gestor.copiar_archivo("renombrado.txt", "copia.txt")

        self.assertEqual(self.gestor.leer_archivo("copia.txt")["content"], "contenido")
        with self.assertRaisesRegex(ErrorGestorArchivos, "Ya existe"):
            self.gestor.copiar_archivo("renombrado.txt", "copia.txt")
        with self.assertRaisesRegex(ErrorGestorArchivos, "Ya existe"):
            self.gestor.renombrar_archivo("renombrado.txt", "copia.txt")
        self.assertTrue((self.raiz / "renombrado.txt").exists())

    def test_elimina_solo_con_confirmacion_explicita(self):
        self.gestor.crear_archivo_texto("", "borrar.txt")
        with self.assertRaisesRegex(ErrorGestorArchivos, "Confirma"):
            self.gestor.eliminar_archivo("borrar.txt", False)
        self.assertTrue((self.raiz / "borrar.txt").exists())
        self.gestor.eliminar_archivo("borrar.txt", True)
        self.assertFalse((self.raiz / "borrar.txt").exists())

    def test_lista_directorios_y_consulta_metadatos(self):
        self.gestor.crear_directorio("", "A carpeta")
        self.gestor.crear_archivo_texto("", "nota.txt")
        contenido = self.gestor.listar_directorio("")

        self.assertEqual([item["name"] for item in contenido], ["A carpeta", "nota.txt"])
        self.assertEqual(contenido[0]["type"], "directory")
        self.assertEqual(contenido[1]["type"], "file")
        self.assertEqual(contenido[1]["size"], 0)
        self.assertIn("modified", contenido[1])
        informacion = self.gestor.obtener_informacion("nota.txt")
        self.assertEqual(informacion["name"], "nota.txt")
        self.assertEqual(informacion["size"], 0)

    def test_rechaza_rutas_inexistentes_y_no_txt_para_editor(self):
        with self.assertRaisesRegex(ErrorGestorArchivos, "no existe"):
            self.gestor.listar_directorio("inexistente")
        self.gestor.crear_archivo_texto("", "datos.txt")
        with self.assertRaisesRegex(ErrorGestorArchivos, "extensión .txt"):
            self.gestor.crear_archivo_texto("", "datos.csv")

    def test_bloquea_enlaces_simbolicos_que_salen_de_la_raiz(self):
        afuera = Path(self.directorio_temporal.name) / "afuera"
        afuera.mkdir()
        try:
            (self.raiz / "atajo").symlink_to(afuera, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("El sistema no permite crear enlaces simbólicos en esta prueba.")

        with self.assertRaisesRegex(ErrorGestorArchivos, "enlaces simbólicos"):
            self.gestor.listar_directorio("atajo")

    def test_bloquea_archivos_con_enlaces_duros_a_fuera_de_la_raiz(self):
        archivo_externo = Path(self.directorio_temporal.name) / "privado.txt"
        archivo_externo.write_text("no modificar", encoding="utf-8")
        try:
            os.link(archivo_externo, self.raiz / "enlace.txt")
        except (OSError, NotImplementedError):
            self.skipTest("El sistema no permite crear enlaces duros en esta prueba.")

        self.assertEqual(self.gestor.listar_directorio("")[0]["type"], "link")
        with self.assertRaisesRegex(ErrorGestorArchivos, "enlazados fuera"):
            self.gestor.guardar_archivo("enlace.txt", "modificado")
        self.assertEqual(archivo_externo.read_text(encoding="utf-8"), "no modificar")


if __name__ == "__main__":
    unittest.main()

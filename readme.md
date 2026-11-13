# Gestor de archivos

Aplicación de escritorio para administrar carpetas y archivos dentro de
`directory/`, sin acceder a rutas personales o del sistema. El backend está
implementado en Python (`clases/`) y se comunica con la interfaz Vue mediante
`API.py` y pywebview.

## Funcionalidades

- Crear carpetas y archivos `.txt` vacíos.
- Navegar entre carpetas y listar sus archivos.
- Abrir, leer y editar `.txt` en un editor integrado.
- Insertar tabulaciones con la tecla Tab al editar texto.
- Agregar información al final de un `.txt`.
- Renombrar archivos sin perder su extensión y copiar a cualquier carpeta
  existente dentro de `directory/` (la eliminación pide confirmación).
- Consultar nombre, tamaño y fecha de modificación.
- Evitar rutas fuera de `directory/`, enlaces simbólicos o duros hacia archivos
  externos y sobrescrituras accidentales por nombres duplicados.

## Requisitos

- Python 3.9 o posterior.
- Node.js `^20.19.0` o `>=22.12.0` y npm.

## Preparar el entorno

En Windows, desde la raíz:

```powershell
.\setup_env_windows.bat
cd interface
npm install
```

En macOS o Linux, desde la raíz:

```sh
python3 -m venv gestor-archivos-env
./gestor-archivos-env/bin/python -m pip install -r requirements.txt
cd interface
npm install
```

## Ejecutar en producción

Genera el frontend desde `interface/`:

```sh
npm run build
```

Después, desde la raíz, inicia la aplicación; por defecto carga los archivos
locales de `interface/dist/` y no requiere que Vite siga ejecutándose:

```powershell
# Windows
.\gestor-archivos-env\Scripts\python.exe init.py
```

```sh
# macOS o Linux
./gestor-archivos-env/bin/python init.py
```

## Ejecutar en desarrollo

Terminal 1, desde `interface/`:

```sh
npm run dev
```

Terminal 2, desde la raíz:

```sh
python init.py --dev
```

El modo de desarrollo se conecta a Vite en `http://localhost:5173`. La ventana
de pywebview siempre recibe la API Python para las operaciones del gestor. La
carpeta administrada se crea automáticamente en `directory/`.

## Pruebas

Desde la raíz:

```sh
python -m unittest discover -s tests -v
```

Desde `interface/`:

```sh
npm run test:unit
npm run build
npm run lint
```

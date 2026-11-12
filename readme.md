# Plantilla de proyecto

Esqueleto vacío para iniciar un proyecto de escritorio con una interfaz Vue y
un backend Python conectado mediante pywebview. Solo incluye una comprobación
mínima de conexión; no contiene funcionalidades de negocio ni una interfaz
previa.

## Requisitos

- Python 3
- Node.js y npm

## Preparación

En Windows, desde la raíz del proyecto:

```powershell
.\setup_env_windows.bat
cd interface
npm install
```

## Ejecución

Inicia el servidor de desarrollo de la interfaz:

```powershell
cd interface
npm run dev
```

En otra terminal, desde la raíz del proyecto, inicia la ventana de escritorio:

```powershell
.\gestor-archivos-env\Scripts\activate
python init.py
```

La pantalla inicial indica si el backend Python está conectado. La interfaz
también puede abrirse en un navegador con `npm run dev`, pero la conexión Python
solo está disponible en la ventana de pywebview.

## Pruebas y verificaciones

Desde la raíz:

```powershell
py -3 -B -m unittest discover -s tests -v
```

Desde `interface`:

```powershell
npm run test:unit
npm run build
npm run lint
```

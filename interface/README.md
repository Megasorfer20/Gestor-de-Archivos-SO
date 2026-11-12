# Interfaz de la plantilla

Interfaz base en Vue con una comprobación de conexión al backend Python a través
de `window.pywebview.api`. No incluye funciones de negocio.

Desde esta carpeta:

```powershell
npm install
npm run dev
npm run test:unit
npm run build
npm run lint
```

Para comprobar la conexión, deja Vite en ejecución y, desde otra terminal en la
raíz del proyecto, ejecuta `python init.py`. La conexión Python está disponible
en la ventana de pywebview; al abrir la página directamente en un navegador se
mantiene la pantalla inicial sin funcionalidades.

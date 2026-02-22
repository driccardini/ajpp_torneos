# Cuadro AJPP (Streamlit)

Web personal moderna para publicar y explorar cuadros de torneos AJPP desde Padelnetwork.

## Funcionalidades

- Obtiene datos del cuadro directamente desde la URL del torneo
- Muestra el cuadro en formato eliminación directa estilo mundial
- Incluye imágenes oficiales del cuadro como vista secundaria
- Muestra horarios y resultados cuando están disponibles

## Ejecutar en local

1. Instalar dependencias:

	```bash
	pip install -e .
	```

2. Iniciar Streamlit:

	```bash
	streamlit run streamlit_app.py
	```

3. Abrir la URL local que muestra la terminal (generalmente `http://localhost:8501`).

## Notas

- La fuente por defecto apunta al cuadro AJPP que compartiste.
- Podés reemplazar la URL desde la barra lateral por cualquier cuadro AJPP compatible.

## Despliegue en Streamlit Community Cloud

1. Subir este proyecto a un repositorio en GitHub.
2. Abrir https://share.streamlit.io e iniciar sesión con GitHub.
3. Hacer clic en **Create app**.
4. Seleccionar repositorio y rama.
5. Configurar **Main file path** como `streamlit_app.py`.
6. Hacer clic en **Deploy**.

### Archivos de despliegue incluidos

- `streamlit_app.py` (cloud entrypoint)
- `requirements.txt` (dependencies)
- `runtime.txt` (Python version)
- `.streamlit/config.toml` (server/theme settings)

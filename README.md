# AJPP Draw Viewer (Streamlit)

Modern personal webpage to publish and explore an AJPP tournament draw from Padelnetwork.

## Features

- Fetches draw data directly from the tournament URL
- Renders a FIFA-style knockout bracket layout
- Includes official source draw images as a fallback/secondary view
- Displays schedule and score data when available

## Run locally

1. Install dependencies:

	```bash
	pip install -e .
	```

2. Start Streamlit:

	```bash
	streamlit run streamlit_app.py
	```

3. Open the local URL shown in terminal (usually `http://localhost:8501`).

## Notes

- The default source points to your shared AJPP draw page.
- You can replace the URL from the app sidebar with any compatible AJPP draw URL.

## Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Open https://share.streamlit.io and sign in with GitHub.
3. Click **Create app**.
4. Select your repository and branch.
5. Set **Main file path** to `streamlit_app.py`.
6. Click **Deploy**.

### Deployment files included

- `streamlit_app.py` (cloud entrypoint)
- `requirements.txt` (dependencies)
- `runtime.txt` (Python version)
- `.streamlit/config.toml` (server/theme settings)

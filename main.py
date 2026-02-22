from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
import streamlit as st
from bs4 import BeautifulSoup


DEFAULT_URL = "https://www.padelnetwork.com/ajpp/2026/febrero/200/challenger/la-plata/boulevard-81/cuadro/"
ROUND_ORDER = {"32°": 1, "16°": 2, "8°": 3, "4°": 4, "2°": 5}
STOPWORDS = {
    "Padelnetwork",
    "Tienda",
    "online",
    "Torneos",
    "Ascenso",
    "Ranking",
    "Home",
    "Cuadro",
    "partido",
    "viernes",
    "sabado",
    "domingo",
    "lunes",
    "martes",
    "miercoles",
    "jueves",
    "Bs",
    "As",
    "Buenos",
    "Aires",
    "La",
    "Plata",
}


@dataclass
class Match:
    number: int
    round_label: str
    schedule: str | None
    score: str | None
    seeds: str
    players: str
    snippet: str


@st.cache_data(ttl=300)
def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.text


@st.cache_data(ttl=900)
def fetch_image_bytes(url: str) -> bytes | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return response.content
    except requests.RequestException:
        return None


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def extract_players(segment: str) -> str:
    raw_names = re.findall(
        r"\b(?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+|[A-ZÁÉÍÓÚÑ]{2,})(?:\s+(?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+|[A-ZÁÉÍÓÚÑ]{2,})){1,3}\b",
        segment,
    )
    candidates: list[str] = []
    for name in raw_names:
        pieces = name.split()
        if any(piece in STOPWORDS for piece in pieces):
            continue
        if len(name) < 6:
            continue
        if name not in candidates:
            candidates.append(name)
    return " / ".join(candidates[:4]) if candidates else "-"


def parse_matches(html: str) -> tuple[list[Match], str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = clean_text(soup.get_text(" ", strip=True))

    marker = re.compile(r"partido\s+(\d+)\s+(32°|16°|8°|4°|2°)", re.IGNORECASE)
    matches = list(marker.finditer(text))
    parsed: list[Match] = []

    for index, found in enumerate(matches):
        start = found.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else min(len(text), start + 420)
        segment = clean_text(text[start:end])

        match_no = int(found.group(1))
        round_label = found.group(2)
        schedule_match = re.search(
            r"(viernes|sabado|domingo|lunes|martes|miercoles|jueves)\s+\d{1,2}\.\d{2}",
            segment,
            re.IGNORECASE,
        )
        score_match = re.search(r"\b\d{1,2}/\d{1,2}(?:\s+\d{1,2}/\d{1,2}){1,2}\b", segment)
        seed_values = sorted(set(re.findall(r"#\d+", segment)), key=lambda value: int(value[1:]))

        parsed.append(
            Match(
                number=match_no,
                round_label=round_label,
                schedule=schedule_match.group(0) if schedule_match else None,
                score=score_match.group(0) if score_match else None,
                seeds=" ".join(seed_values) if seed_values else "-",
                players=extract_players(segment),
                snippet=segment,
            )
        )

    parsed.sort(key=lambda item: (ROUND_ORDER.get(item.round_label, 99), item.number))
    return parsed, text


def extract_draw_images(html: str, page_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    image_urls: list[str] = []
    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        if "/fotos/" in href and href.lower().endswith(".jpg"):
            absolute = urljoin(page_url, href)
            if absolute not in image_urls:
                image_urls.append(absolute)

    def sort_key(url: str) -> tuple[int, str]:
        filename = url.rsplit("/", maxsplit=1)[-1].split(".", maxsplit=1)[0]
        digits = re.sub(r"\D", "", filename)
        return (int(digits) if digits else 999999, url)

    return sorted(image_urls, key=sort_key)


def modern_styles() -> None:
    st.markdown(
        """
        <style>
            .main-title {
                font-size: 2.1rem;
                font-weight: 700;
                margin-bottom: 0.2rem;
            }
            .subtitle {
                color: #6b7280;
                margin-bottom: 1.1rem;
            }
            .card {
                background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
                border-radius: 14px;
                padding: 14px 16px;
                margin-bottom: 10px;
                border: 1px solid rgba(255,255,255,0.08);
            }
            .card h4 {
                color: #ffffff;
                margin: 0 0 6px 0;
                font-size: 1rem;
            }
            .card p {
                color: #d1d5db;
                margin: 0;
                font-size: 0.92rem;
            }
            .bracket-wrapper {
                overflow-x: auto;
                padding-bottom: 10px;
            }
            .bracket {
                display: flex;
                gap: 16px;
                align-items: flex-start;
                min-width: max-content;
            }
            .round-column {
                width: 240px;
            }
            .round-title {
                font-size: 0.95rem;
                font-weight: 700;
                color: #e5e7eb;
                margin-bottom: 8px;
                padding-left: 6px;
            }
            .match-box {
                background: linear-gradient(160deg, #0f172a 0%, #1f2937 100%);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 12px;
                padding: 9px 10px;
                color: #f9fafb;
            }
            .match-title {
                font-size: 0.78rem;
                font-weight: 700;
                opacity: 0.9;
                margin-bottom: 6px;
            }
            .team-line {
                font-size: 0.84rem;
                line-height: 1.35;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .match-meta {
                margin-top: 7px;
                font-size: 0.75rem;
                opacity: 0.8;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def split_matchup(players: str) -> tuple[str, str]:
    chunks = [piece.strip() for piece in players.split("/") if piece.strip()]
    if len(chunks) >= 4:
        return f"{chunks[0]} / {chunks[1]}", f"{chunks[2]} / {chunks[3]}"
    if len(chunks) >= 2:
        return chunks[0], chunks[1]
    return players, "TBD"


def render_bracket(matches: list[Match]) -> None:
    rounds = sorted({item.round_label for item in matches}, key=lambda value: ROUND_ORDER.get(value, 99))
    matches_by_round = {
        round_label: sorted(
            [item for item in matches if item.round_label == round_label],
            key=lambda item: item.number,
        )
        for round_label in rounds
    }

    html_parts = ['<div class="bracket-wrapper"><div class="bracket">']

    for round_index, round_label in enumerate(rounds):
        top_offset = max(8, (2**round_index - 1) * 16)
        gap = max(12, (2**(round_index + 1) - 1) * 18)
        html_parts.append('<div class="round-column">')
        html_parts.append(f'<div class="round-title">Round {round_label}</div>')
        html_parts.append(f'<div style="margin-top:{top_offset}px;">')

        for idx, match in enumerate(matches_by_round[round_label]):
            team_a, team_b = split_matchup(match.players)
            score_value = match.score or "-"
            schedule_value = match.schedule or "-"
            html_parts.append(
                (
                    '<div class="match-box" '
                    f'style="margin-bottom:{gap if idx < len(matches_by_round[round_label]) - 1 else 0}px;">'
                    f'<div class="match-title">Match {match.number}</div>'
                    f'<div class="team-line">{team_a}</div>'
                    '<div class="team-line">vs</div>'
                    f'<div class="team-line">{team_b}</div>'
                    f'<div class="match-meta">Score: {score_value} · Time: {schedule_value}</div>'
                    '</div>'
                )
            )

        html_parts.append("</div></div>")

    html_parts.append("</div></div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def render_app() -> None:
    st.set_page_config(page_title="AJPP Draw Viewer", page_icon="🎾", layout="wide")
    modern_styles()

    st.markdown('<div class="main-title">AJPP Draw Viewer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Personal Streamlit page for a modern, readable tournament bracket view.</div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Source")
        url = st.text_input("Draw URL", value=DEFAULT_URL)
        refresh = st.button("Refresh draw", width="stretch")
        st.caption("Tip: keep the default URL, or replace it with another AJPP draw page.")

    if refresh:
        st.cache_data.clear()

    try:
        html = fetch_html(url)
        matches, full_text = parse_matches(html)
        draw_images = extract_draw_images(html, url)
    except requests.RequestException as error:
        st.error(f"Could not load the webpage: {error}")
        return

    if not matches:
        st.warning("The page loaded but no matches were parsed. You can still open the source URL below.")
        st.link_button("Open original page", url)
        return

    completed = sum(1 for item in matches if item.score)
    scheduled = sum(1 for item in matches if item.schedule)

    col1, col2, col3 = st.columns(3)
    col1.metric("Matches parsed", len(matches))
    col2.metric("Matches with result", completed)
    col3.metric("Matches with schedule", scheduled)

    tab_bracket, tab_images, tab_source = st.tabs(["Bracket", "Draw images", "Source"])

    with tab_bracket:
        st.caption("FIFA-style knockout bracket view.")
        render_bracket(matches)

    with tab_images:
        if draw_images:
            st.caption("Official draw images extracted from the AJPP source page.")
            selected_image = st.selectbox(
                "Choose image",
                options=draw_images,
                format_func=lambda item: item.rsplit("/", maxsplit=1)[-1],
            )
            image_bytes = fetch_image_bytes(selected_image)
            if image_bytes:
                st.image(image_bytes, width="stretch")
            else:
                st.error("Could not load this image from source. Try another image or refresh.")

            with st.expander("Show all draw images"):
                load_gallery = st.checkbox(
                    f"Load gallery ({len(draw_images)} images)",
                    value=False,
                    help="Disabled by default to keep the page fast and stable.",
                )
                if load_gallery:
                    for image_url in draw_images:
                        gallery_bytes = fetch_image_bytes(image_url)
                        if gallery_bytes:
                            st.image(
                                gallery_bytes,
                                caption=image_url.rsplit("/", maxsplit=1)[-1],
                                width="stretch",
                            )
                        else:
                            st.warning(f"Skipped image: {image_url.rsplit('/', maxsplit=1)[-1]}")
        else:
            st.warning("No draw images were found on this page.")

    with tab_source:
        st.link_button("Open original page", url)
        with st.expander("Raw extracted text preview"):
            st.text_area("Preview", value=full_text[:8000], height=320)


if __name__ == "__main__":
    render_app()

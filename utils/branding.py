import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def asset_path(name: str) -> str:
    """Absolute path to a file inside the assets/ folder."""
    return str(ASSETS_DIR / name)


@lru_cache(maxsize=None)
def asset_data_uri(name: str, mime: str = "image/svg+xml") -> str:
    """Returns an asset as a base64 data URI so it can be used inside HTML."""
    data = (ASSETS_DIR / name).read_bytes()
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def render_sidebar_logo():
    """Renders the Finova logo (icon + wordmark) at the top of the sidebar."""
    logo = asset_data_uri("logo_full.svg")
    st.sidebar.markdown(
        f'<div style="padding: 0.4rem 0.2rem 1rem 0.2rem;"><img src="{logo}" alt="Finova" style="height: 46px; width: auto; display: block;"></div>',
        unsafe_allow_html=True,
    )


def nav_logo_html(height: int = 64, variant: str = "color") -> str:
    """HTML for a tightly cropped, high-res logo. variant: "color" (light bg) or "white" (dark bg)."""
    name = "logo_nav_white.png" if variant == "white" else "logo_nav.png"
    logo = asset_data_uri(name, "image/png")
    return (
        f'<div class="nav-logo"><img src="{logo}" alt="Finova" '
        f'style="height:{height}px; width:auto; display:block;"></div>'
    )

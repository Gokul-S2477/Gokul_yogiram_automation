import streamlit as st

from modules.forecast_module import render_forecast_module
from ui.theme import apply_app_theme


ACTIVE_MODULE_KEY = "active_module"
UI_MODE_KEY = "ui_mode"

MODULES = [
    {
        "id": "forecast",
        "name": "Forecast App",
        "description": "Demand forecasting and order recommendation.",
        "enabled": True,
    },
    {
        "id": "purchase_planner",
        "name": "Purchase Planner",
        "description": "Planned future module.",
        "enabled": False,
    },
    {
        "id": "analytics_dashboard",
        "name": "Analytics Dashboard",
        "description": "Planned future module.",
        "enabled": False,
    },
]


def _init_app_state():
    if ACTIVE_MODULE_KEY not in st.session_state:
        st.session_state[ACTIVE_MODULE_KEY] = None
    if UI_MODE_KEY not in st.session_state:
        st.session_state[UI_MODE_KEY] = "Light"


def _open_module(module_id):
    st.session_state[ACTIVE_MODULE_KEY] = module_id


def _back_to_home():
    st.session_state[ACTIVE_MODULE_KEY] = None


def _render_module_home():
    st.markdown(
        """
        <div class="hub-hero">
            <div class="hub-title">Pharma Operations Hub</div>
            <div class="hub-subtitle">Select a module to continue.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    left_col, right_col = st.columns(2, gap="large")
    cols = [left_col, right_col]

    for idx, module in enumerate(MODULES):
        with cols[idx % 2]:
            status_class = "status-live" if module["enabled"] else "status-coming"
            status_text = "Live" if module["enabled"] else "Coming Soon"

            st.markdown(
                f"""
                <div class="module-card">
                    <div class="module-status {status_class}">{status_text}</div>
                    <div class="module-name">{module["name"]}</div>
                    <div class="module-desc">{module["description"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if module["enabled"]:
                st.button(
                    f"Open {module['name']}",
                    key=f"open_{module['id']}",
                    on_click=_open_module,
                    args=(module["id"],),
                    width='stretch',
                )
            else:
                st.button(
                    "Coming Soon",
                    disabled=True,
                    key=f"disabled_{module['id']}",
                    width='stretch',
                )


def _render_active_module():
    active_module = st.session_state[ACTIVE_MODULE_KEY]
    st.button(
        "Back to Modules",
        key="back_to_modules",
        on_click=_back_to_home,
        width='stretch',
    )

    st.divider()

    if active_module == "forecast":
        render_forecast_module()
    else:
        st.error("Selected module is not available yet.")


def _render_sidebar_controls():
    with st.sidebar:
        st.markdown("### Interface")
        st.radio(
            "Theme Mode",
            options=["Light", "Dark"],
            key=UI_MODE_KEY,
            horizontal=True,
        )
        st.caption(
            "Default is Light mode. Switch to Dark mode anytime; all UI components stay consistent."
        )
        st.divider()
        if st.session_state[ACTIVE_MODULE_KEY] is None:
            st.markdown("**Current:** Home")
        else:
            st.markdown(f"**Current:** {st.session_state[ACTIVE_MODULE_KEY].replace('_', ' ').title()}")
            st.button(
                "Back to Modules",
                key="sidebar_back_to_modules",
                on_click=_back_to_home,
                width='stretch',
            )


def main():
    st.set_page_config(page_title="Pharma Operations Hub", layout="wide")
    _init_app_state()
    _render_sidebar_controls()
    apply_app_theme(mode=st.session_state[UI_MODE_KEY].lower())

    if st.session_state[ACTIVE_MODULE_KEY] is None:
        _render_module_home()
    else:
        _render_active_module()


if __name__ == "__main__":
    main()

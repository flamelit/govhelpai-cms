import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit.logger import get_logger
from streamlit_extras.card import card
from streamlit_extras.switch_page_button import switch_page
from yaml.loader import SafeLoader

log = get_logger(__name__)

st.set_page_config(
    initial_sidebar_state="collapsed",
    page_title="GovHelp.AI - CMS",
)

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
        div[data-testid="stToolbar"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
        }
        div[data-testid="stDecoration"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
        }
        div[data-testid="stStatusWidget"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
        }
        #MainMenu {
        visibility: hidden;
        height: 0%;
        }
        header {
        visibility: hidden;
        height: 0%;
        }
        footer {
        visibility: hidden;
        height: 0%;
        }
</style>
""",
    unsafe_allow_html=True,
)


with open("./tmp_auth/auth.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)


def render_app():
    st.header("Welcome to The GovHelp.AI Demo for CMS", anchor=False)
    st.subheader("Please choose a technology demonstration.", anchor=False)
    st.divider()

    col1, col2 = st.columns(2, gap="large")
    st.write("\n\n")
    st.write("\n\n")

    with col2:
        st.markdown(
            """SPA Trail Guide is an LLM Chatbot that helps SPA submitters know where to go to submit their SPA or to get help"""
        )

    with col1:
        spaguide = st.button(
            label="SPA Trail Guide",
            type="primary",
            key="SPATrailGuideEnterButton",
            use_container_width=True,
        )
        if spaguide:
            switch_page("guide")

    col3, col4 = st.columns(2, gap="large")

    with col4:
        st.markdown(
            """SPA Review Assistant reviews a PDF submission file and reports compliance to requirements.""",
        )

    with col3:
        spareview = st.button(
            label="Review Assistant",
            type="primary",
            key="SPASubmissionReviewEnterButton",
            use_container_width=True,
        )
        if spareview:
            switch_page("review")

    st.divider()
    st.subheader("GovHelp.AI")
    st.write(
        "GovHelp.AI prototype is focused on improving "
        "process speed for benefit delivery by augmenting "
        "Government workforce capabilities.\n\n*Not affiliated with any"
        " Government.\n Application is Prototype.*"
    )
    st.markdown("Improving speed of " "delivery though Generative AI.")
    st.markdown(
        """Made with :heart: and :muscle: by <br />
        <a href="https://flamelit.tech"><img src="app/static/flamelit_logo_large.png" alt="image" width="35%" height="auto"></a>
         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <a href="https://boostaro.com"><img src="app/static/boostaro_logo.png" alt="image" width="35%" height="auto"></a>
         """,
        unsafe_allow_html=True,
    )


authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

name, authentication_status, username = authenticator.login(
    'Login to Prototype GovHelp.AI.\nUser: "cms", Pass: "llm"', "main"
)

if authentication_status is True:
    authenticator.logout("Logout", "sidebar")
    render_app()
elif authentication_status is False:
    st.error("Username or password is incorrect.")
elif authentication_status is None:
    st.warning(
        """We added a temporary login form to prevent spam/abuse.
               Please login using user/pass as cms/llm"""
    )

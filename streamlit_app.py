import streamlit as st
from textwrap import dedent

# ----------------#
# Config & Assets #
# ----------------#

LOGO_PATH = "aza_labs.png"

st.set_page_config(
    page_title="Aza-Labs Resume Bullet Forge",
    page_icon="🧨",
    layout="wide",
)

# Aza-Labs brand colors
AZA_BG = "#001529"
AZA_ORANGE = "#F58B02"
AZA_CYAN = "#00C4E8"
AZA_TEXT = "#F9FAFB"
AZA_MUTED = "#9CA3AF"

# --------------#
# Custom Styles #
# --------------#
CUSTOM_CSS = f"""
<style>
    .main {{
        background-color: {AZA_BG};
    }}
    .app-title {{
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
        background: linear-gradient(120deg, {AZA_ORANGE}, {AZA_CYAN}, {AZA_TEXT});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .app-subtitle {{
        font-size: 0.98rem;
        color: {AZA_MUTED};
        margin-bottom: 1.5rem;
    }}
    .section-title {{
        font-size: 1.05rem;
        font-weight: 600;
        color: {AZA_TEXT};
        margin-bottom: 0.4rem;
    }}
    .section-subtitle {{
        font-size: 0.85rem;
        color: {AZA_MUTED};
        margin-bottom: 0.8rem;
    }}
    .aza-panel {{
        border-radius: 1rem;
        padding: 1rem 1.1rem;
        background: radial-gradient(circle at top left, #0b1524, #000814);
        border: 1px solid rgba(148, 163, 184, 0.35);
        box-shadow: 0 14px 35px rgba(0, 0, 0, 0.8);
    }}
    .aza-panel-muted {{
        border-radius: 1rem;
        padding: 0.9rem 1rem;
        background: rgba(15, 23, 42, 0.9);
        border: 1px dashed rgba(148, 163, 184, 0.4);
    }}
    .label-strong {{
        font-weight: 600;
        color: {AZA_TEXT};
    }}
    .info-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.08rem 0.5rem;
        border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.6);
        font-size: 0.75rem;
        color: {AZA_MUTED};
        margin-left: 0.4rem;
    }}
    .info-dot {{
        width: 6px;
        height: 6px;
        border-radius: 999px;
        background: {AZA_CYAN};
        margin-right: 0.25rem;
    }}
    .result-title {{
        font-size: 0.9rem;
        font-weight: 600;
        color: {AZA_TEXT};
        margin-bottom: 0.2rem;
    }}
    .result-label {{
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {AZA_ORANGE};
        margin-bottom: 0.15rem;
    }}
    .helper-text {{
        font-size: 0.8rem;
        color: {AZA_MUTED};
    }}
    /* Footer */
    .aza-footer {{
        margin-top: 2rem;
        padding: 1rem 0 0.5rem 0;
        border-top: 1px solid rgba(148, 163, 184, 0.3);
    }}
    .aza-footer-text {{
        font-size: 0.85rem;
        color: {AZA_MUTED};
    }}
    .aza-footer-highlight {{
        color: {AZA_CYAN};
        font-weight: 600;
    }}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------------#
# OpenAI client helper  #
# ----------------------#
def get_openai_client(api_key: str):
    """
    Lazily import and return an OpenAI client.
    This avoids hard-crashing if the library isn't installed.
    """
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        return None, "The 'openai' Python package is not installed. Run: pip install openai"

    if not api_key:
        return None, "Please enter your OpenAI API key."

    client = OpenAI(api_key=api_key)
    return client, None


def generate_improved_bullets(
    client,
    model: str,
    job_title: str,
    seniority: str,
    tone: str,
    industry: str,
    bullets: str,
):
    prompt = dedent(
        f"""
        You are an expert resume writer and career coach.

        TASK:
        Rewrite the following resume bullet points to be:
        - Impact-focused
        - Quantified where possible
        - Tailored to the target role
        - Concise (1–2 lines per bullet)
        - Written in the selected tone

        Target role: {job_title or "Not specified"}
        Seniority: {seniority}
        Tone: {tone}
        Industry/domain: {industry or "Generic"}

        ORIGINAL BULLETS:
        {bullets}

        OUTPUT FORMAT:
        - Return ONLY the improved bullets as a Markdown numbered list.
        - Do NOT include explanations or headings.
        """
    ).strip()

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an expert resume writer who crafts high-impact, quantified bullets that pass resume screeners and ATS.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=600,
    )

    return completion.choices[0].message.content.strip()


# ----------------------#
# Session defaults      #
# ----------------------#
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = ""

if "last_output" not in st.session_state:
    st.session_state["last_output"] = ""


# --------------#
# Header        #
# --------------#
st.markdown('<div class="app-title">Aza-Labs Resume Bullet Forge</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">'
    "Turn basic bullets into quantified, high-impact lines tailored to your target role. "
    "Perfect for refreshing your resume or optimizing it for a new job."
    "</div>",
    unsafe_allow_html=True,
)

# --------------#
# Top layout    #
# --------------#
top_left, top_right = st.columns([2.2, 1.8])

with top_left:
    st.markdown('<div class="section-title">1. Connect your AI engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Paste your OpenAI API key. It is kept only in this session and not stored anywhere else.</div>',
        unsafe_allow_html=True,
    )

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        value=st.session_state["openai_api_key"],
        help="Your key is used only to call OpenAI from this app and is not logged or saved.",
    )
    st.session_state["openai_api_key"] = api_key

    st.markdown(
        f"""
        <div class="helper-text">
            <span class="label-strong">Tip:</span> Use a key with access to <code>gpt-4o</code> or similar for best results.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")  # small spacer

with top_right:
    st.markdown('<div class="section-title">How this works</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="aza-panel-muted">
            <ul style="padding-left: 1rem; margin-bottom: 0.4rem; color: #e5e7eb; font-size: 0.85rem;">
                <li>Describe the <b>target role</b> and <b>seniority</b>.</li>
                <li>Paste your current resume bullet points.</li>
                <li>Choose tone (e.g. neutral, confident).</li>
                <li>Click <b>Forge bullets</b> to generate upgraded lines.</li>
            </ul>
            <div style="font-size: 0.8rem; color: #9CA3AF;">
                You can copy the improved bullets directly into your resume or LinkedIn.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------#
# Input section #
# --------------#
st.markdown("---")

input_left, input_right = st.columns([2.3, 1.7])

with input_left:
    st.markdown('<div class="section-title">2. Describe your target role</div>', unsafe_allow_html=True)

    job_title = st.text_input(
        "Target role / job title",
        placeholder="e.g. Senior Data Engineer, AI Product Manager",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        seniority = st.selectbox(
            "Seniority level",
            ["Entry", "Mid", "Senior", "Lead / Principal", "Director & above"],
            index=2,
        )
    with col_b:
        tone = st.selectbox(
            "Tone",
            ["Neutral professional", "Confident", "Bold", "Concise & minimal"],
            index=1,
        )

    industry = st.text_input(
        "Industry / domain (optional)",
        placeholder="e.g. Fintech, Insurance, eCommerce…",
    )

    st.markdown("")
    st.markdown('<div class="section-title">3. Paste your existing bullet points</div>', unsafe_allow_html=True)
    bullets = st.text_area(
        "Existing bullets",
        height=220,
        placeholder="• Led a team of 4 engineers...\n• Worked on data pipelines...\n• Improved performance...",
    )

with input_right:
    st.markdown('<div class="section-title">Model & options</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="aza-panel">', unsafe_allow_html=True)

        model = st.selectbox(
            "OpenAI model",
            ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"],
            index=0,
        )

        quantify_pref = st.selectbox(
            "Quantification preference",
            ["Add metrics where obvious only", "Aggressively add metrics", "Light touch (minimal changes)"],
            index=0,
        )

        st.markdown(
            f"""
            <div class="helper-text" style="margin-top: 0.4rem;">
                The model will automatically weave in impact & metrics.  
                <br/>Preference: <b>{quantify_pref}</b>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")
    forge_clicked = st.button("🔥 Forge bullets", type="primary", use_container_width=True)

# --------------#
# Generate      #
# --------------#
error_message = None

if forge_clicked:
    if not api_key:
        error_message = "Please paste your OpenAI API key to continue."
    elif not bullets.strip():
        error_message = "Please paste at least one existing bullet point."
    else:
        client, client_error = get_openai_client(api_key)
        if client_error:
            error_message = client_error
        else:
            with st.spinner("Forging upgraded bullets with AI..."):
                try:
                    # Nudge quantification through the "tone" and context
                    quant_hint = {
                        "Add metrics where obvious only": "add metrics only when they are implied or obvious; avoid making up unrealistic numbers.",
                        "Aggressively add metrics": "prioritize quantification; infer reasonable metrics and percentages where possible.",
                        "Light touch (minimal changes)": "make subtle improvements and light quantification; preserve original wording as much as possible.",
                    }[quantify_pref]

                    enhanced_bullets = generate_improved_bullets(
                        client=client,
                        model=model,
                        job_title=job_title,
                        seniority=seniority,
                        tone=f"{tone}. Quantification preference: {quant_hint}",
                        industry=industry,
                        bullets=bullets,
                    )
                    st.session_state["last_output"] = enhanced_bullets
                except Exception as e:
                    error_message = f"Something went wrong while calling OpenAI: {e}"

if error_message:
    st.error(error_message)

# --------------#
# Results       #
# --------------#
if st.session_state.get("last_output"):
    st.markdown("---")
    st.markdown('<div class="section-title">4. Compare & copy</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Original vs. forged bullets side-by-side. Copy the right-hand side into your resume or LinkedIn.</div>',
        unsafe_allow_html=True,
    )

    col_orig, col_new = st.columns(2)

    with col_orig:
        st.markdown(
            """
            <div class="result-label">Original</div>
            <div class="result-title">Your current bullets</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="aza-panel"><div class="helper-text" style="color:#e5e7eb; white-space:pre-wrap;">{bullets}</div></div>',
            unsafe_allow_html=True,
        )

    with col_new:
        st.markdown(
            """
            <div class="result-label">Forged</div>
            <div class="result-title">AI-upgraded bullets</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(st.session_state["last_output"])
        st.markdown("</div>", unsafe_allow_html=True)

# --------------#
# Footer        #
# --------------#
st.markdown('<div class="aza-footer">', unsafe_allow_html=True)
footer_left, footer_right = st.columns([3, 1])

with footer_left:
    st.markdown(
        """
        <div class="aza-footer-text">
            Built at <span class="aza-footer-highlight">Aza-Labs</span>.  
            Forge sharper, louder, more impactful career stories — one bullet at a time.
        </div>
        """,
        unsafe_allow_html=True,
    )

with footer_right:
    try:
        st.image(LOGO_PATH, width=70)
    except Exception:
        st.caption("Add aza_labs.png next to this script to show the logo here.")

st.markdown("</div>", unsafe_allow_html=True)

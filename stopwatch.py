import streamlit as st
import time
from datetime import timedelta

# Inject responsive CSS (your existing + improvements)
st.markdown("""
    <style>
    /* Your existing styles - keeping them intact */
    .stApp {
        font-size: 12px;  /* Base body text */
    }
    h1 {
        font-size: 4rem !important;  /* Timer */
    }
    .split-text {
        font-size: 1.2rem;
    }
    .sum-text {
        font-size: 1.2rem;
    }
    button {
        font-size: 1.2rem !important;
        min-height: 50px !important;
    }
    /* Hide toolbar/status area*/
    [data-testid="stToolbar"] {
        visibility: hidden !important;
    }
    [data-testid="stStatusWidget"] {
        visibility: hidden !important;
    }
    header {
        visibility: hidden !important;  /* Hides the whole header if needed, but careful */
    }
    /* NEW: Make checkboxes larger for easier tapping */
    [data-testid="stCheckbox"] {
        transform: scale(1.6);          /* 3.6× size - good balance; try 1.4 to 2.0 */
        transform-origin: left center;  /* Keeps alignment nice */
        margin-right: 12px !important;  /* Extra space so it doesn't crowd text */
    }

    /* Make the checkbox container a bit taller to avoid clipping */
    [data-testid="stCheckbox"] > div {
        height: 32px !important;        /* Adjust if needed for your scale */
    }

    /* Mobile: Even larger checkboxes on small screens for fat-finger friendliness */
    @media (max-width: 768px) {
        [data-testid="stCheckbox"] {
            transform: scale(1.8);      /* Slightly bigger on phones */
            margin-right: 16px !important;
        }
        [data-testid="stCheckbox"] > div {
            height: 40px !important;
        }
        .stApp {
            font-size: 14px;
        }
        h1 {
            font-size: 3rem !important;
        }
        .split-text {
            font-size: 0.95rem;
        }
        .sum-text {
            font-size: 1.2rem;
        }
        button {
            font-size: 1.1rem !important;
        }
    }

    @media (max-width: 480px) {
        .stApp > div:first-child {
            padding: 1rem !important;
        }
    }

    /* Title styling */
    .stApp h1 {
        font-size: 1.8rem !important;
    }
    @media (max-width: 768px) {
        .stApp h1 {
            font-size: 1.8rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Helper format_time (unchanged)
def format_time(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total_sec = int(td.total_seconds())
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    hundredths = int((seconds - total_sec) * 100)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{hundredths:02d}"
    return f"{minutes:02d}:{secs:02d}.{hundredths:02d}"

# Session state init (unchanged)
if 'running' not in st.session_state:
    st.session_state.running = False
    st.session_state.start_time = 0.0
    st.session_state.elapsed = 0.0
    st.session_state.splits = []  
    st.session_state.selected = set()  

st.title("Stopwatch with Splits for Cheerleading Judging")

# Timer display
current_time = st.session_state.elapsed if not st.session_state.running else (time.time() - st.session_state.start_time) + st.session_state.elapsed
st.markdown(f"<h1 style='text-align: center;'>{format_time(current_time)}</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Start" if not st.session_state.running else "Stop", use_container_width=True, type="primary" if st.session_state.running else "secondary"):
        if not st.session_state.running:
            st.session_state.start_time = time.time() - st.session_state.elapsed
            st.session_state.running = True
        else:
            now = time.time()
            cum = now - st.session_state.start_time
            last_cum = st.session_state.splits[-1][1] if st.session_state.splits else 0
            split_dur = cum - last_cum
            if split_dur > 0.01:
                st.session_state.splits.append((split_dur, cum))
            st.session_state.elapsed = cum
            st.session_state.running = False
        st.rerun()

with col2:
    if st.button("Split", use_container_width=True, disabled=not st.session_state.running):
        now = time.time()
        cum = now - st.session_state.start_time
        last_cum = st.session_state.splits[-1][1] if st.session_state.splits else 0
        split_dur = cum - last_cum
        st.session_state.splits.append((split_dur, cum))
        st.rerun()

with col3:
    if st.button("Clear", use_container_width=True):
        st.session_state.running = False
        st.session_state.elapsed = 0.0
        st.session_state.start_time = 0.0
        st.session_state.splits = []
        st.session_state.selected = set()
        st.rerun()

# Splits list with added divider for clarity when stacked
if st.session_state.splits:
    st.subheader("Splits")
    total_selected = 0.0
    for i, (dur, cum) in enumerate(st.session_state.splits):
        if i > 0:
            st.markdown('<div class="split-row-divider"></div>', unsafe_allow_html=True)  # Horizontal line between rows

        col_check, col_text = st.columns([1, 8])
        with col_check:
            checked = i in st.session_state.selected
            if st.checkbox("", value=checked, key=f"check_{i}"):
                st.session_state.selected.add(i)
            else:
                st.session_state.selected.discard(i)
        with col_text:
            st.markdown(f"<div class='split-text'>#{i+1:2d}   {format_time(dur):>8}   (total {format_time(cum):>8})</div>", unsafe_allow_html=True)

    if st.session_state.selected:
        total_selected = sum(st.session_state.splits[i][0] for i in st.session_state.selected)
        st.markdown(f"<div class='sum-text'>Selected splits total: **{format_time(total_selected)}**</div>", unsafe_allow_html=True)
    else:
        st.info("Tap checkboxes to select splits and sum them.")

# Auto-rerun for timer
if st.session_state.running:
    time.sleep(0.1)
    st.rerun()

st.markdown(
    """
    <hr style="margin-top: 3rem; border-top: 1px solid #ccc;">
    <p style="text-align: center; font-size: 1rem; color: #555; margin-top: 1rem;">
        <a href="https://cospiritsigns.com/" target="_blank" style="text-decoration: none; color: #0066cc; font-weight: bold;">
            Need signs, bows, and custom apparel? Visit Colorado Spirit Signs today!
        </a>
    </p>
    """,
    unsafe_allow_html=True
)
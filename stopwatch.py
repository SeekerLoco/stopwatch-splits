import streamlit as st
import time
from datetime import timedelta

# Inject responsive CSS with flexbox for checkbox + text alignment
st.markdown("""
    <style>
    /* Base styles */
    .stApp {
        font-size: 16px;
    }
    h1 {
        font-size: 3.5rem !important;
        text-align: center !important;
    }
    button {
        font-size: 1.2rem !important;
        min-height: 50px !important;
        width: 100% !important;
    }

    /* Title font size override (smaller than default Streamlit h1) */
    .block-container h1 {
        font-size: 2.2rem !important;
        margin-bottom: 1.5rem !important;
    }

    /* Timer display */
    .timer-display {
        font-size: 4rem;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }

    /* Sum display */
    .sum-text {
        font-size: 1.4rem;
        font-weight: bold;
    }

    /* Force checkbox + text side-by-side using flexbox */
    .split-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;
        padding: 6px 0;
    }
    .split-row .stCheckbox {
        margin: 0 !important;
        padding: 0 !important;
        min-width: 24px;
    }
    .split-row .stCheckbox > div > label {
        margin: 0 !important;
        padding: 0 !important;
    }
    .split-row .split-text {
        flex: 1;
        white-space: normal;
        line-height: 1.4;
        font-size: 1.1rem;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .stApp {
            font-size: 14px;
        }
        h1, .block-container h1 {
            font-size: 1.8rem !important;
        }
        .timer-display {
            font-size: 3rem;
        }
        .split-row {
            flex-direction: row !important;
            align-items: flex-start;
            gap: 10px;
        }
        .split-row .split-text {
            font-size: 0.95rem;
        }
        button {
            font-size: 1.1rem !important;
            min-height: 48px !important;
        }
    }

    @media (max-width: 480px) {
        .split-row {
            gap: 8px;
        }
        .split-row .split-text {
            font-size: 0.9rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Time formatting helper
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

# Initialize session state
if 'running' not in st.session_state:
    st.session_state.running = False
    st.session_state.start_time = 0.0
    st.session_state.elapsed = 0.0
    st.session_state.splits = []           # list of (split_duration, cum_time)
    st.session_state.selected = set()      # indices of selected splits

# Page title (you can adjust the text here)
st.title("Stopwatch with Splits for Cheerleading Judging")

# Timer display
current_time = (
    st.session_state.elapsed
    if not st.session_state.running
    else (time.time() - st.session_state.start_time) + st.session_state.elapsed
)
st.markdown(f"<div class='timer-display'>{format_time(current_time)}</div>", unsafe_allow_html=True)

# Buttons in columns
col1, col2, col3 = st.columns(3)

with col1:
    if st.button(
        "Start" if not st.session_state.running else "Stop",
        use_container_width=True,
        type="primary" if st.session_state.running else "secondary"
    ):
        if not st.session_state.running:
            # Start / Resume
            st.session_state.start_time = time.time() - st.session_state.elapsed
            st.session_state.running = True
        else:
            # Stop: add final split
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

# Splits list with inline checkbox + text
if st.session_state.splits:
    st.subheader("Splits")
    total_selected = 0.0

    for i, (dur, cum) in enumerate(st.session_state.splits):
        with st.container():
            st.markdown('<div class="split-row">', unsafe_allow_html=True)

            # Checkbox (no label text)
            checked = i in st.session_state.selected
            if st.checkbox(
                label="",
                value=checked,
                key=f"check_{i}",
                help=f"Select split #{i+1}"
            ):
                st.session_state.selected.add(i)
            else:
                st.session_state.selected.discard(i)

            # Split text right next to checkbox
            st.markdown(
                f'<div class="split-text">#{i+1:2d}   {format_time(dur):>8}   (total {format_time(cum):>8})</div>',
                unsafe_allow_html=True
            )

            st.markdown('</div>', unsafe_allow_html=True)

    # Show sum if anything selected
    if st.session_state.selected:
        total_selected = sum(st.session_state.splits[i][0] for i in st.session_state.selected)
        st.markdown(
            f"<div class='sum-text'>Selected splits total: {format_time(total_selected)}</div>",
            unsafe_allow_html=True
        )
    else:
        st.info("Tap the box next to each split you want to include in the total.")

# Keep the timer updating while running
if st.session_state.running:
    time.sleep(0.1)
    st.rerun()
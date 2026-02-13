import streamlit as st
import time
from datetime import timedelta

# Helper to format time (mm:ss.hh or hh:mm:ss.hh)
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
    st.session_state.splits = []  # list of (split_duration, cum_time)
    st.session_state.selected = set()  # indices of selected splits

st.title("Cheerleading Competition Stopwatch")

# Large timer display
current_time = st.session_state.elapsed if not st.session_state.running else (time.time() - st.session_state.start_time) + st.session_state.elapsed
st.markdown(f"<h1 style='text-align: center; font-size: 4em;'>{format_time(current_time)}</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Start" if not st.session_state.running else "Stop", use_container_width=True, type="primary" if st.session_state.running else "secondary"):
        if not st.session_state.running:
            # Start/resume
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

# Splits list with checkboxes
if st.session_state.splits:
    st.subheader("Splits")
    total_selected = 0.0
    for i, (dur, cum) in enumerate(st.session_state.splits):
        col_check, col_text = st.columns([1, 8])
        with col_check:
            checked = i in st.session_state.selected
            if st.checkbox("", value=checked, key=f"check_{i}"):
                st.session_state.selected.add(i)
            else:
                st.session_state.selected.discard(i)
        with col_text:
            st.write(f"#{i+1:2d}   {format_time(dur):>8}   (cum {format_time(cum):>8})")

    if st.session_state.selected:
        total_selected = sum(st.session_state.splits[i][0] for i in st.session_state.selected)
        st.success(f"Selected splits total: **{format_time(total_selected)}**")
    else:
        st.info("Tap checkboxes to select splits and sum them.")

# Auto-update timer while running
if st.session_state.running:
    time.sleep(0.1)  # Adjust for smoother/faster updates (0.05-0.2)
    st.rerun()
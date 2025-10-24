import streamlit as st
import numpy as np
import random

st.set_page_config(page_title="Quantum Battleship", page_icon="⚓", layout="centered")

st.title("⚓ Quantum Battleship: Human vs Quantum Radar")
st.markdown("""
A fun interactive game to demonstrate **Quantum Illumination**!  
You (the human) will try to find hidden ships by clicking cells.  
Meanwhile, the **Quantum Radar AI** uses smart probability updates to detect ships faster, even under noise.
""")

# --- Game Setup ---
grid_size = st.sidebar.slider("Grid Size", 4, 8, 5)
num_ships = st.sidebar.slider("Number of Ships", 1, grid_size, 3)
false_positive = st.sidebar.slider("False Positive Rate (noise)", 0.0, 0.4, 0.1, 0.05)
false_negative = st.sidebar.slider("False Negative Rate (miss chance)", 0.0, 0.4, 0.1, 0.05)

# --- Initialize session state ---
if "board" not in st.session_state:
    board = np.zeros((grid_size, grid_size))
    ships = random.sample([(i, j) for i in range(grid_size) for j in range(grid_size)], num_ships)
    for x, y in ships:
        board[x, y] = 1
    st.session_state.board = board
    st.session_state.human_hits = np.zeros_like(board)
    st.session_state.quantum_hits = np.zeros_like(board)
    st.session_state.prob = np.ones_like(board) / (grid_size**2)
    st.session_state.turn = 0
    st.session_state.result_text = ""

# --- Reset Button ---
if st.sidebar.button("Reset Game"):
    st.session_state.clear()
    st.rerun()

board = st.session_state.board
human_hits = st.session_state.human_hits
quantum_hits = st.session_state.quantum_hits
prob = st.session_state.prob

# --- Helper Functions ---
def noisy_sensor(board, x, y):
    actual = board[x, y]
    if actual == 1 and random.random() < false_negative:
        return 0
    elif actual == 0 and random.random() < false_positive:
        return 1
    return actual

def quantum_move():
    # choose max probability cell
    x, y = np.unravel_index(np.argmax(prob), prob.shape)
    result = noisy_sensor(board, x, y)
    quantum_hits[x, y] = result
    # update probabilities
    if result == 1:
        for i in range(max(0, x-1), min(grid_size, x+2)):
            for j in range(max(0, y-1), min(grid_size, y+2)):
                prob[i, j] += 0.3
    prob[x, y] = 0
    prob[:] = prob / np.sum(prob)
    return result, (x, y)

# --- Human Turn ---
st.subheader("🎯 Your Turn — Click to Fire at the Hidden Ships")

cols = st.columns(grid_size)
for i in range(grid_size):
    for j in range(grid_size):
        label = "❌" if human_hits[i, j] == 0.5 else "💥" if human_hits[i, j] == 1 else " "
        if cols[j].button(label or " ", key=f"{i}-{j}"):
            if human_hits[i, j] == 0:  # only if not already tried
                res = noisy_sensor(board, i, j)
                human_hits[i, j] = 1 if res == 1 else 0.5
                # quantum radar moves right after
                q_res, (qx, qy) = quantum_move()
                st.session_state.turn += 1
                if np.sum(human_hits == 1) >= num_ships:
                    st.session_state.result_text = "🎉 You found all ships first! Quantum Radar loses."
                elif np.sum(quantum_hits == 1) >= num_ships:
                    st.session_state.result_text = "🤖 Quantum Radar found all ships first! It wins!"
                st.rerun()

# --- Display Boards ---
st.write("---")
col1, col2 = st.columns(2)
col1.markdown("### 👨‍🚀 Your Board")
col2.markdown("### ⚛️ Quantum Radar Board")

col1.image(human_hits, caption="Your detections (💥 = hit, ❌ = miss)", width=300)
col2.image(quantum_hits, caption="Quantum detections", width=300)

# --- Results Section ---
st.write("---")
if st.session_state.result_text:
    st.success(st.session_state.result_text)
else:
    st.info(f"Turns taken: {st.session_state.turn}. Keep firing!")

st.markdown("""
**Legend:**  
💥 = Hit  
❌ = Miss  
⚛️ Quantum Radar uses probability-based intelligent search.
""")


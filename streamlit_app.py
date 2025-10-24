import streamlit as st
import numpy as np
import random
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title="Quantum Battleship Radar", page_icon="⚓", layout="centered")

st.title("⚓ Quantum Battleship Radar — Live Detection Animation")
st.markdown("""
This interactive simulation compares **Classical** vs **Quantum-Inspired** radar detection  
in a noisy *Battleship-style* grid.  
Watch in real time how the **Quantum-inspired algorithm** locates hidden ships faster and smarter.
""")

# --- Sidebar Settings ---
st.sidebar.header("Game Controls")
size = st.sidebar.slider("Grid Size", 4, 8, 5)
num_ships = st.sidebar.slider("Number of Ships", 1, max(1, size*size//4), 3)
false_positive = st.sidebar.slider("False Positive Rate (noise)", 0.0, 0.5, 0.2, 0.05)
false_negative = st.sidebar.slider("False Negative Rate (miss chance)", 0.0, 0.5, 0.2, 0.05)
speed = st.sidebar.slider("Animation Speed (sec per step)", 0.05, 1.0, 0.2)
start_button = st.sidebar.button("Start Simulation 🚀")

# --- Utility: Create noisy detection function ---
def noisy_sensor(board, x, y, fp, fn):
    actual = board[x, y]
    if actual == 1 and random.random() < fn:
        return 0  # miss ship
    elif actual == 0 and random.random() < fp:
        return 1  # false detection
    return actual

# --- Utility: Draw grid state ---
def draw_board(board, found, title):
    fig, ax = plt.subplots(figsize=(4,4))
    combined = np.zeros_like(board)
    combined[board==1] = 0.3  # actual ship (light green)
    combined[found==1] = 1.0  # detected (bright)
    ax.imshow(combined, cmap="Greens")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title)
    st.pyplot(fig)

if start_button:
    # --- Step 1: Setup battlefield ---
    board = np.zeros((size, size))
    ship_positions = random.sample([(i, j) for i in range(size) for j in range(size)], num_ships)
    for (x, y) in ship_positions:
        board[x, y] = 1

    st.subheader("🎯 Real-Time Detection Simulation")

    # --- Create 2 columns for comparison ---
    col1, col2 = st.columns(2)
    classical_placeholder = col1.empty()
    quantum_placeholder = col2.empty()

    # --- Step 2: Classical Detection ---
    c_found = np.zeros((size, size))
    tried_c = set()
    guesses_c = 0

    # --- Step 3: Quantum-Inspired Detection ---
    q_found = np.zeros((size, size))
    prob = np.ones((size, size)) / (size*size)
    guesses_q = 0

    # --- Step 4: Real-time animation ---
    total_steps = size * size
    for step in range(total_steps):
        # Classical random guess
        while True:
            x, y = random.randint(0, size-1), random.randint(0, size-1)
            if (x, y) not in tried_c:
                tried_c.add((x, y))
                break
        result_c = noisy_sensor(board, x, y, false_positive, false_negative)
        c_found[x, y] = result_c
        guesses_c += 1

        # Quantum-inspired smart guess
        xq, yq = np.unravel_index(np.argmax(prob), prob.shape)
        result_q = noisy_sensor(board, xq, yq, false_positive, false_negative)
        q_found[xq, yq] = result_q
        guesses_q += 1
        if result_q == 1:
            for i in range(max(0, xq-1), min(size, xq+2)):
                for j in range(max(0, yq-1), min(size, yq+2)):
                    prob[i, j] += 0.3
        prob[xq, yq] = 0
        prob /= np.sum(prob)

        # Update radar visuals
        with classical_placeholder:
            draw_board(board, c_found, f"Classical Radar (Guesses: {guesses_c})")
        with quantum_placeholder:
            draw_board(board, q_found, f"Quantum Radar (Guesses: {guesses_q})")

        # Stop if both found all ships
        if np.sum(c_found * board) >= num_ships and np.sum(q_found * board) >= num_ships:
            break

        time.sleep(speed)

    # --- Step 5: Show final comparison ---
    c_acc = np.sum((c_found == 1) & (board == 1)) / num_ships
    q_acc = np.sum((q_found == 1) & (board == 1)) / num_ships

    st.success("✅ Simulation Complete!")

    st.markdown(f"""
    ### 📊 Results Summary
    - Classical Guesses: **{guesses_c}**
    - Quantum Guesses: **{guesses_q}**
    - Classical Accuracy: **{c_acc*100:.1f}%**
    - Quantum Accuracy: **{q_acc*100:.1f}%**

    The **Quantum-inspired radar** adapts its search strategy  
    using *correlation boosting* — similar to how **quantum entanglement**  
    helps real quantum radars detect targets under noise more efficiently.
    """)

else:
    st.info("👈 Adjust settings and click **Start Simulation 🚀** to watch the live radar in action.")

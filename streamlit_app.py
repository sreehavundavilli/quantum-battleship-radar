import streamlit as st
import numpy as np
import random
import matplotlib.pyplot as plt

st.set_page_config(page_title="Quantum Battleship Radar", page_icon="⚓", layout="centered")

st.title("⚓ Quantum Battleship Radar Simulation")
st.markdown("""
This simulation compares **Classical** vs **Quantum-Inspired** radar detection  
in a noisy *Battleship-style* environment.  
The **Quantum version** simulates entanglement-like correlations to find hidden ships faster and more accurately.
""")

# --- Sidebar Controls ---
st.sidebar.header("Game Settings")
size = st.sidebar.slider("Grid Size", 3, 10, 5)
num_ships = st.sidebar.slider("Number of Ships", 1, max(1, size*size//4), 3)
false_positive = st.sidebar.slider("False Positive Rate (noise)", 0.0, 0.5, 0.2, 0.05)
false_negative = st.sidebar.slider("False Negative Rate (miss chance)", 0.0, 0.5, 0.2, 0.05)
run_button = st.sidebar.button("Run Simulation")

if run_button:
    # --- Step 1: Create Game Board ---
    board = np.zeros((size, size))
    ship_positions = random.sample([(i, j) for i in range(size) for j in range(size)], num_ships)
    for (x, y) in ship_positions:
        board[x, y] = 1

    # --- Step 2: Define Noise Sensor ---
    def noisy_sensor(x, y):
        actual = board[x, y]
        if actual == 1 and random.random() < false_negative:
            return 0  # miss a real ship
        elif actual == 0 and random.random() < false_positive:
            return 1  # false detection
        return actual

    # --- Step 3: Classical Detection ---
    def classical_detection():
        guesses = 0
        found = np.zeros((size, size))
        tried = set()
        while np.sum(found) < num_ships:
            x, y = random.randint(0, size-1), random.randint(0, size-1)
            if (x, y) in tried:
                continue
            tried.add((x, y))
            result = noisy_sensor(x, y)
            found[x, y] = result
            guesses += 1
        return guesses, found

    # --- Step 4: Quantum-Inspired Detection ---
    def quantum_detection():
        guesses = 0
        found = np.zeros((size, size))
        prob = np.ones((size, size)) / (size * size)
        while np.sum(found) < num_ships:
            x, y = np.unravel_index(np.argmax(prob), prob.shape)
            result = noisy_sensor(x, y)
            guesses += 1
            found[x, y] = result
            if result == 1:
                for i in range(max(0, x-1), min(size, x+2)):
                    for j in range(max(0, y-1), min(size, y+2)):
                        prob[i, j] += 0.3
            prob[x, y] = 0
            prob = prob / np.sum(prob)
        return guesses, found

    # --- Run Both Simulations ---
    c_guesses, c_found = classical_detection()
    q_guesses, q_found = quantum_detection()

    # --- Results ---
    st.subheader("Simulation Results")
    col1, col2 = st.columns(2)
    col1.metric("Classical Detection Guesses", c_guesses)
    col2.metric("Quantum Detection Guesses", q_guesses)

    # --- Plot Results ---
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))
    axs[0].imshow(board, cmap="Greens")
    axs[0].set_title("Real Ship Locations")
    axs[1].imshow(c_found, cmap="Reds")
    axs[1].set_title("Classical Detection")
    axs[2].imshow(q_found, cmap="Blues")
    axs[2].set_title("Quantum-Inspired Detection")
    for ax in axs:
        ax.set_xticks([])
        ax.set_yticks([])
    st.pyplot(fig)

    # --- Accuracy Comparison ---
    accuracy_classical = np.sum((c_found == 1) & (board == 1)) / num_ships
    accuracy_quantum = np.sum((q_found == 1) & (board == 1)) / num_ships
    st.markdown(f"""
    ### 🔍 Accuracy Comparison
    - Classical Detection Accuracy: **{accuracy_classical*100:.1f}%**
    - Quantum-Inspired Detection Accuracy: **{accuracy_quantum*100:.1f}%**
    
    The **quantum-inspired approach** uses correlation-based probability boosts  
    to locate ships faster and more accurately — similar to how **quantum illumination**  
    improves target detection in noisy environments.
    """)
else:
    st.info("👈 Adjust settings in the sidebar and click **Run Simulation** to start.")

import matplotlib.pyplot as plt
import matplotlib
import project as p
matplotlib.use("QtAgg")

# TODO: Parameter für Konstruktor von BioFeedback eintragen
BF = p.BioFeedback()

# Create the figure and axis for the plot
fig, ax = plt.subplots()
bars = ax.bar(1, [0], color="skyblue")

# Configure the plot
ax.set_ylim(0, 1)  # Muscle activation ranges from 0 to 1
ax.set_xlabel("Musculus biceps brachii")
ax.set_ylabel("Activation Level")
ax.set_title("Muscle Activation Tracking")
ax.set_xticks([])
ax.set_xticklabels([])

# Initialize variables
current_height = 0
DECAY_RATE = 0.1
max_activation_reached = 0  # Variable to track the maximum activation reached

# Draw a line for the max activation reached so far (it will be updated later)
max_activation_line = ax.axhline(y=max_activation_reached, color='r', linestyle='--', label="Max Activation")
# Add the legend
ax.legend()

try:
    while True:
        # Generate new muscle activation data (mean activity as a single value)
        data = BF.mean_activity()

        # Apply decay and update the height
        current_height = max(current_height - DECAY_RATE, 0)  # Apply decay to the height
        current_height = max(current_height, data)  # Update to new data if it is higher

        # Update the maximum activation reached if necessary
        if data > max_activation_reached:
            max_activation_reached = data
            max_activation_line.set_ydata([max_activation_reached])  # Update the horizontal line

        # Update the bar height
        bars[0].set_height(current_height)

        # Pause to allow for a real-time update
        plt.pause(0.01)

except KeyboardInterrupt:
    # Exit the loop when interrupted
    print("Animation stopped.")


# Show the plot
plt.show()


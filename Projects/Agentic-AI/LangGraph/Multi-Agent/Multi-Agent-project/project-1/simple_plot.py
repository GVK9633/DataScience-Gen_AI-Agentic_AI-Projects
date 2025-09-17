import matplotlib
import matplotlib.pyplot as plt

# Try to use a GUI backend (Mac-friendly)
try:
    matplotlib.use("TkAgg")
    gui_available = True
except Exception:
    gui_available = False

# Sample data
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

# Create the plot
plt.plot(x, y, label="y = 2x", marker="o")
plt.title("Simple Line Plot")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()

# Show or Save
if gui_available:
    try:
        plt.show(block=True)  # keep window open
    except Exception:
        plt.savefig("plot.png")
        print("⚠️ GUI not available. Plot saved as plot.png")
else:
    plt.savefig("plot.png")
    print("⚠️ GUI not available. Plot saved as plot.png")

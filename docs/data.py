import numpy as np

def read_file_with_numpy(filename):
  """Reads a file with the format `x y` and returns two NumPy arrays, one for `x` and one for `y`, using the `numpy.loadtxt()` function.

  Args:
    filename: The path to the file to read.

  Returns:
    A tuple of two NumPy arrays, one for `x` and one for `y`.
  """

  x, y, angle = np.loadtxt(filename, unpack=True)

  return x, y, angle

import matplotlib.pyplot as plt
# Example usage:

x, y, angle = read_file_with_numpy("robot.txt")

print(x)
print(y)

tempo = np.arange(0, len(x))


# Create a figure.
fig, ax = plt.subplots()

# Add a scatter plot of `x` and `y`.
ax.scatter(x, y, s=50)



# Add an arrow for each point.
for i in range(len(x)):
# Calculate the offset from the middle of the field.
    offset_x = x[i]
    offset_y = y[i]

# Calculate the angle relative to the middle of the field.
    angle_rel = angle[i] - np.arctan2(offset_y, offset_x)
    print(angle_rel)

# Add the arrow.
    ax.arrow(offset_x, offset_y, np.cos(angle_rel), np.sin(angle_rel), head_width=0.1, head_length=0.2)

# Add labels for the x and y axes.
    ax.set_xlabel("x")
    ax.set_ylabel("y")

  # Show the plot.
plt.show()




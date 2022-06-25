import matplotlib as mpl
import matplotlib.pyplot as plt
from random import random

mas = [random() for _ in range(100)]

fig, ax = plt.subplots()  # Create a figure containing a single axes.
fig.suptitle('bold figure suptitle', fontsize=14, fontweight='bold')
ax.plot(range(len(mas)), mas)
# Plot some data on the axes.
plt.savefig('save/1.png')

mas = [random() for _ in range(100)]

fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.plot(range(len(mas)), mas)
# Plot some data on the axes.

plt.savefig('save/2.png')
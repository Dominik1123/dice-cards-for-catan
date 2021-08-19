from functools import partial
import math
import itertools as it

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Shadow
import numpy as np


FIGSIZE = 2.5, 3.5  # inches; standard trading card size
DPI = 100
EDGE_LENTH = 0.5
DOT_RADIUS = EDGE_LENTH / 7.5
DOT_OFFSET = EDGE_LENTH / 2.5
DOT_COLOR = 'black'
RED_POSITION   = FIGSIZE[0]/2 - EDGE_LENTH/1.1, FIGSIZE[1]/3.5
WHITE_POSITION = FIGSIZE[0]/2 + EDGE_LENTH/1.1, FIGSIZE[1]/3.5
VALUE_POSITION = FIGSIZE[0]/2, 2/3*FIGSIZE[1]
FONT_FAMILY = 'fantasy'
FONT_SIZE = 65
FONT_WEIGHT = 'extra bold'
RED = '#c90000'
WHITE = '#fff4d4'
SHADOW = '#262626'
SHADOW_OFFSET = 0.03

A4_FIGSIZE = 8.25, 11.75  # inches
A4_DPI = 100
A4_CARD_SHIFT = 0.1
A4_CARDS_PER_ROW = A4_FIGSIZE[0] // FIGSIZE[0]
A4_CARDS_PER_COL = A4_FIGSIZE[1] // FIGSIZE[1]


Dot = partial(Circle, radius=DOT_RADIUS, color=DOT_COLOR)
Face = partial(FancyBboxPatch, width=EDGE_LENTH, height=EDGE_LENTH, boxstyle='Round, pad=0.1')
Shadow = partial(Shadow, props=dict(color=SHADOW))

a4_figures, a4_axes = zip(*(
    plt.subplots(figsize=A4_FIGSIZE)
    for _ in range(int(math.ceil(36 / (A4_CARDS_PER_ROW*A4_CARDS_PER_COL))))
))
for a4_ax in a4_axes:
    a4_ax.set_xlim([0, A4_FIGSIZE[0]])
    a4_ax.set_ylim([0, A4_FIGSIZE[1]])
    a4_ax.set_axis_off()


def new_card_canvas():
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.set_xlim([0, FIGSIZE[0]])
    ax.set_ylim([0, FIGSIZE[1]])
    ax.set_axis_off()
    return fig, ax


def add_to_axis(value, *, color, where, ax):
    x, y = where
    rect = ax.add_patch(Face([x - EDGE_LENTH/2, y - EDGE_LENTH/2], color=color, transform=ax.transData))
    ax.add_patch(Shadow(rect, SHADOW_OFFSET, -SHADOW_OFFSET))
    if value not in range(1, 7):
        raise ValueError(value)
    if value % 2 == 1:
        ax.add_patch(Dot([x, y]))
    if value >= 2:
        ax.add_patch(Dot([x - DOT_OFFSET, y - DOT_OFFSET]))
        ax.add_patch(Dot([x + DOT_OFFSET, y + DOT_OFFSET]))
    if value >= 4:
        ax.add_patch(Dot([x - DOT_OFFSET, y + DOT_OFFSET]))
        ax.add_patch(Dot([x + DOT_OFFSET, y - DOT_OFFSET]))
    if value == 6:
        ax.add_patch(Dot([x - DOT_OFFSET, y]))
        ax.add_patch(Dot([x + DOT_OFFSET, y]))


def add_total_value(value, *, ax, offset=np.zeros(2)):
    color = 'red' if value in (6, 8) else 'black'
    text = ax.text(
        *(offset + VALUE_POSITION),
        str(value),
        fontfamily=FONT_FAMILY, fontsize=FONT_SIZE, fontweight=FONT_WEIGHT,
        color=color,
        ha='center', va='center',
    )


def add_card_frame(position, *, ax):
    ax.add_patch(Rectangle(
        position,
        width=FIGSIZE[0], height=FIGSIZE[1],
        facecolor='none', edgecolor='black',
        linewidth=0.5,
        transform=ax.transData,
))


a4_axes = it.chain(a4_axes, [None])  # pad with None to prevent StopIteration on last iteration
a4_ax = next(a4_axes)
index = row = col = 0
offset = np.zeros(2)
for red, white in it.product(range(1, 7), repeat=2):
    fig, ax = new_card_canvas()

    add_to_axis(red, color=RED, where=RED_POSITION, ax=ax)
    add_to_axis(white, color=WHITE, where=WHITE_POSITION, ax=ax)
    add_total_value(red + white, ax=ax)

    add_to_axis(red, color=RED, where=offset+RED_POSITION, ax=a4_ax)
    add_to_axis(white, color=WHITE, where=offset+WHITE_POSITION, ax=a4_ax)
    add_total_value(red + white, offset=offset, ax=a4_ax)
    add_card_frame(offset, ax=a4_ax)

    fig.savefig(f'cards/{red}{white}.png', bbox_inches='tight', pad_inches=0, dpi=DPI)
    plt.close(fig)

    index += 1
    row, col = divmod(index, A4_CARDS_PER_ROW)
    if row == A4_CARDS_PER_COL:
        row = 0
        assert col == 0
        index = 0
        a4_ax = next(a4_axes)
    offset = np.array([
        col * (FIGSIZE[0] + A4_CARD_SHIFT),
        row * (FIGSIZE[1] + A4_CARD_SHIFT),
    ])

for i, a4_fig in enumerate(a4_figures):
    a4_fig.savefig(f'A4/{i}.png', bbox_inches='tight', pad_inches=0, dpi=A4_DPI)

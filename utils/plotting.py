
"""
Functions to plot traffic situations.

Based on: https://github.com/dnv-opensource/ship-traffic-generator/blob/main/src/trafficgen/plot_traffic_situation.py
"""

import math
from typing import List, Optional
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle  
from trafficgen.types import Position, Ship, Situation, TargetShip
from trafficgen import deg_2_rad, m2nm, rad_2_deg

def add_ship_to_plot(
    ship: Ship,
    vector_time: float,
    axes: Optional[plt.Axes],
    color: str = "black",
    label_distance: float = 0.5
):
    """
    Add the ship to the plot.

    Params:
        ship: Ship information
        vector_time: Vector time [min]
        axes: Instance of figure axis. If not set, instance is set to None
        color: Color of the ship. If not set, color is 'black'
    """
    if axes is None:
        axes = plt.gca()
    assert isinstance(axes, plt.Axes)

    assert ship.start_pose is not None
    pos_0_north = m2nm(ship.start_pose.position.north)
    pos_0_east = m2nm(ship.start_pose.position.east)
    course = ship.start_pose.course
    speed = ship.start_pose.speed

    vector_length = m2nm(vector_time * knot_2_m_pr_min(speed))

    _ = axes.arrow(
        pos_0_east,
        pos_0_north,
        vector_length * np.sin(deg_2_rad(course)),
        vector_length * np.cos(deg_2_rad(course)),
        edgecolor=color,
        facecolor=color,
        width=0.0001,
        head_length=0.2,
        head_width=0.2,
        length_includes_head=True,
    )
    circle = Circle(
        xy=(pos_0_east, pos_0_north),
        radius=vector_time / 100.0,  # type: ignore
        color=color,
    )
    _ = axes.add_patch(circle)
    
    # Adding id label for target ships
    if isinstance(ship,TargetShip):
        label_x = pos_0_east - label_distance * np.sin(deg_2_rad(course))
        label_y = pos_0_north - label_distance * np.cos(deg_2_rad(course))
        axes.text(label_x, label_y, f"({ship.id})", color=color, ha='center', va='center')

    return axes

def find_max_value_for_plot(
    ship: Ship,
    max_value: float,
) -> float:
    """
    Find the maximum deviation from the Reference point in north and east direction.

    Params:
        ship: Ship information
        max_value: maximum deviation in north, east direction

    Returns
    -------
        max_value: updated maximum deviation in north, east direction
    """
    assert ship.start_pose is not None
    max_value = np.max(
        [
            max_value,
            np.abs(m2nm(ship.start_pose.position.north)),
            np.abs(m2nm(ship.start_pose.position.east)),
        ]
    )
    return max_value 
    

def plot_traffic_situations(
    traffic_situations: List[Situation],
    col: int,
    row: int,
    max_value: float = 0.0
):
    """
    Plot the traffic situations in one more figures.

    Params:
        traffic_situations: Traffic situations to be plotted
        col: Number of columns in each figure
        row: Number of rows in each figure
        max_value: Maximum range
    """
    max_columns = col
    max_rows = row
    num_subplots_pr_plot = max_columns * max_rows
    small_size = 6
    bigger_size = 10
    padding = 0.5

    plt.rc("axes", titlesize=small_size)  # fontsize of the axes title
    plt.rc("axes", labelsize=small_size)  # fontsize of the x and y labels
    plt.rc("xtick", labelsize=small_size)  # fontsize of the tick labels
    plt.rc("ytick", labelsize=small_size)  # fontsize of the tick labels
    plt.rc("figure", titlesize=bigger_size)  # fontsize of the figure title

    # The axes should have the same x/y limits, thus find max value for
    # north/east position to be used for plotting
    for situation in traffic_situations:
        assert situation.own_ship is not None
        max_value = find_max_value_for_plot(situation.own_ship, max_value)
        assert situation.target_ship is not None
        for target_ship in situation.target_ship:
            max_value = find_max_value_for_plot(target_ship, max_value)

    plot_number: int = 1
    _ = plt.figure(plot_number)
    for i, situation in enumerate(traffic_situations):
        if math.floor(i / num_subplots_pr_plot) + 1 > plot_number:
            plot_number += 1
            _ = plt.figure(plot_number)

        axes: plt.Axes = plt.subplot(
            max_rows,
            max_columns,
            int(1 + i - (plot_number - 1) * num_subplots_pr_plot),
            xlabel="[nm]",
            ylabel="[nm]",
        )
        # _ = axes.set_title(situation.title)
        assert situation.own_ship is not None
        assert situation.common_vector is not None
        axes = add_ship_to_plot(
            situation.own_ship,
            situation.common_vector,
            axes,
            "black"
        )
        assert situation.target_ship is not None
        for target_ship in situation.target_ship:
            axes = add_ship_to_plot(
                target_ship,
                situation.common_vector,
                axes,
                "red",
            )
        axes.set_aspect("equal")


        _ = plt.xlim(-max_value - padding, max_value + padding)
        _ = plt.ylim(-max_value - padding, max_value + padding)
        _ = plt.subplots_adjust(wspace=0.4, hspace=0.4)

    plt.show()
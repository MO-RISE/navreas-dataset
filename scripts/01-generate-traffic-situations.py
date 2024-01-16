import sys
from pathlib import Path

import matplotlib.pyplot as plt

## Monkey path read_situation_files, see https://github.com/dnv-opensource/ship-traffic-generator/pull/15
from functools import wraps
import trafficgen

@wraps(trafficgen.read_files.read_situation_files)
def sorted_read_situation_files(situation_folder: Path):
    situations = trafficgen.read_files.read_situation_files(situation_folder)

    return sorted(situations, key=lambda situation: situation.input_file_name)

trafficgen.ship_traffic_generator.read_situation_files = sorted_read_situation_files


from trafficgen import (
    generate_traffic_situations,
    write_traffic_situations_to_json_file,
)

parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from utils.plotting import plot_traffic_situations

BASE_PATH = Path(__file__).parent.parent / "traffic_situations"
INPUT_PATH = BASE_PATH / "input"
GENERATED_PATH = BASE_PATH / "generated"

for input_path in INPUT_PATH.glob("*"):

    # We only deal with subdirectories here
    if input_path.is_file():
        continue

    # if not input_path.stem == "spatial_understanding_set":
    #     continue

    generated_path = GENERATED_PATH / input_path.stem
    generated_path.mkdir(parents=True, exist_ok=True)

    generated_traffic_situations = generate_traffic_situations(
        situation_folder=input_path / "descriptions",
        own_ship_file=input_path / "own_ship.json",
        target_ship_folder=input_path / "target_ships",
        settings_file=input_path / "encounter_settings.json",
    )

    # Monkey fix for negative speed in spatial situations to create
    # situations with no risk of collision.
    for situation in generated_traffic_situations:
        for target_ship in situation.target_ship:
            if target_ship.start_pose.speed < 0.0:
                target_ship.start_pose.speed *= -1
                target_ship.start_pose.course += 180
                target_ship.start_pose.course %= 360

    with plt.ion():
        # Single plot for every situation
        plot_traffic_situations(generated_traffic_situations, 1, 1, max_value=8.0)

        for fig_num in plt.get_fignums():
            plt.figure(fig_num)
            plt.savefig(generated_path / f"traffic_situation_{fig_num:02d}.png")

        plt.close("all")

    write_traffic_situations_to_json_file(generated_traffic_situations, write_folder=generated_path)

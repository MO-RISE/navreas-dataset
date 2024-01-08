# Traffic situations

The folder structure is as follows:

* `input` contains input definitions for several discrete sets of situations. Each subfolder under `input` follows a strict layout as follows and all files:
  * `own_ship.json` is a file describing the own ship in each situation in the situation set.
  * `encounter_settings.json` is a file with global settings for teh generation of the situations.
  * `target_ships` is a folder containing one or several descriptions (json files) of target ships used in the situations.
  * `descriptions` is a folder with one description (json file) for each scenario part of the scenario set.

* `generated` contains the generated situations for each of the defined situation sets under `input`.


import os
import json
import duckdb
import pandas as pd
from pathlib import Path

PARQUET_DIR = Path("./parquet")
PARQUET_DIR.mkdir(parents=True, exist_ok=True)


DUCKDB_PATH = "dowsing-machine.duckdb"
con = duckdb.connect(DUCKDB_PATH)
cur = con.cursor()

# Extractors
def get_Pokemon(data): return (data["id"], data["name"], data["height"], data["weight"], data["base_experience"])
def get_Abilities(data): return (data["id"], data["name"], data["generation"]["name"])
def get_Moves(data): return (data["id"], data["name"], data["generation"]["name"], data["power"], data["accuracy"], data["pp"], data["priority"])
def get_Id_Name(data): return (data["id"], data["name"])
def get_Evolution_Chain(data): return (data["id"], data["id"])
def get_Machine(data): return (data["id"], data["item"]["name"], data["move"]["name"])
def get_Version_Group(data): return (data["id"], data["name"], data["order"])
def get_Location_Area(data): return (data["id"], data["location"]["name"], data["name"])
def get_Item(data): return (data["id"], data["name"], data["cost"], data["fling_power"])
def get_Natures(data): return (data["id"], data["name"], data["increased_stat"]["name"] if data["increased_stat"] else None, data["decreased_stat"]["name"] if data["decreased_stat"] else None)

TABLE_CONFIG = [
    {"name": "pokemon", "path": "./PokeData/api/v2/pokemon", "columns": ["pokemon_id","name","height","weight","base_experience"], "extract": get_Pokemon},
    {"name": "species", "path": "./PokeData/api/v2/pokemon-species", "columns": ["species_id","name"], "extract": get_Id_Name},
    {"name": "abilities", "path": "./PokeData/api/v2/ability", "columns": ["ability_id","name","generation"], "extract": get_Abilities},
    {"name": "moves", "path": "./PokeData/api/v2/move", "columns": ["move_id","name","generation","power","accuracy","pp","priority"], "extract": get_Moves},
    {"name": "berries", "path": "./PokeData/api/v2/berry", "columns": ["berry_id","name"], "extract": get_Id_Name},
    {"name": "egg_groups", "path": "./PokeData/api/v2/egg-group", "columns": ["egg_group_id","name"], "extract": get_Id_Name},
    {"name": "encounter_conds", "path": "./PokeData/api/v2/encounter-condition", "columns": ["encounter_id","name"], "extract": get_Id_Name},
    {"name": "encounter_values", "path": "./PokeData/api/v2/encounter-condition-value", "columns": ["encounter_value_id","name"], "extract": get_Id_Name},
    {"name": "encounter_methods", "path": "./PokeData/api/v2/encounter-method", "columns": ["encounter_method_id","name"], "extract": get_Id_Name},
    {"name": "evolution_chains", "path": "./PokeData/api/v2/evolution-chain", "columns": ["evolution_chain_id", "evolution_chain_id2"], "extract": get_Evolution_Chain},
    {"name": "evolution_triggers", "path": "./PokeData/api/v2/evolution-trigger", "columns": ["evolution_trigger_id","name"], "extract": get_Id_Name},
    {"name": "genders", "path": "./PokeData/api/v2/gender", "columns": ["gender_id","name"], "extract": get_Id_Name},
    {"name": "generations", "path": "./PokeData/api/v2/generation", "columns": ["generation_id","name"], "extract": get_Id_Name},
    {"name": "growth_rates", "path": "./PokeData/api/v2/growth-rate", "columns": ["growth_rate_id","name"], "extract": get_Id_Name},
    {"name": "items", "path": "./PokeData/api/v2/item", "columns": ["item_id","name", "cost", "fling_power"], "extract": get_Item},
    {"name": "item_attributes", "path": "./PokeData/api/v2/item-attribute", "columns": ["item_attribute_id","name"], "extract": get_Id_Name},
    {"name": "item_categories", "path": "./PokeData/api/v2/item-category", "columns": ["item_category_id","name"], "extract": get_Id_Name},
    {"name": "item_fling_effects", "path": "./PokeData/api/v2/item-fling-effect", "columns": ["item_fling_effect_id","name"], "extract": get_Id_Name},
    {"name": "item_pockets", "path": "./PokeData/api/v2/item-pocket", "columns": ["item_pocket_id","name"], "extract": get_Id_Name},
    {"name": "locations", "path": "./PokeData/api/v2/location", "columns": ["location_id","name"], "extract": get_Id_Name},
    {"name": "location_areas", "path": "./PokeData/api/v2/location-area", "columns": ["location_area_id","location_name", "name"], "extract": get_Location_Area},
    {"name": "machines", "path": "./PokeData/api/v2/machine", "columns": ["machine_id","item_name", "move_name"], "extract": get_Machine},
    {"name": "move_ailments", "path": "./PokeData/api/v2/move-ailment", "columns": ["move_ailment_id","name"], "extract": get_Id_Name},
    {"name": "move_battle_styles", "path": "./PokeData/api/v2/move-battle-style", "columns": ["move_battle_style_id","name"], "extract": get_Id_Name},
    {"name": "move_categories", "path": "./PokeData/api/v2/move-category", "columns": ["move_category_id","name"], "extract": get_Id_Name},
    {"name": "move_damage_classes", "path": "./PokeData/api/v2/move-damage-class", "columns": ["move_damage_class_id","name"], "extract": get_Id_Name},
    {"name": "move_learn_methods", "path": "./PokeData/api/v2/move-learn-method", "columns": ["move_learn_method_id","name"], "extract": get_Id_Name},
    {"name": "move_targets", "path": "./PokeData/api/v2/move-target", "columns": ["move_target_id","name"], "extract": get_Id_Name},
    {"name": "natures", "path": "./PokeData/api/v2/nature", "columns": ["nature_id","name", "increased_stat", "decreased_stat"], "extract": get_Natures},
    {"name": "pokedexes", "path": "./PokeData/api/v2/pokedex", "columns": ["pokedex_id","name"], "extract": get_Id_Name},
    {"name": "colors", "path": "./PokeData/api/v2/pokemon-color", "columns": ["color_id","name"], "extract": get_Id_Name},
    {"name": "habitats", "path": "./PokeData/api/v2/pokemon-habitat", "columns": ["habitat_id","name"], "extract": get_Id_Name},
    {"name": "shapes", "path": "./PokeData/api/v2/pokemon-shape", "columns": ["shape_id","name"], "extract": get_Id_Name},
    {"name": "regions", "path": "./PokeData/api/v2/region", "columns": ["region_id","name"], "extract": get_Id_Name},
    {"name": "stats", "path": "./PokeData/api/v2/stat", "columns": ["stat_id","name"], "extract": get_Id_Name},
    {"name": "pokemon_types_def", "path": "./PokeData/api/v2/type", "columns": ["type_id","name"], "extract": get_Id_Name},
    {"name": "versions", "path": "./PokeData/api/v2/version", "columns": ["version_id","name"], "extract": get_Id_Name},
    {"name": "version_groups", "path": "./PokeData/api/v2/version-group", "columns": ["version_group_id","name", "order_num"], "extract": get_Version_Group}
]

# loader for simple tables
def load_table_to_parquet(cfg):
    rows = []

    for folder in os.listdir(cfg["path"]):
        folder_path = os.path.join(cfg["path"], folder)

        if not os.path.isdir(folder_path):
            continue

        json_path = os.path.join(folder_path, "index.json")
        if not os.path.exists(json_path):
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        values = cfg["extract"](data)

        # make sure values is always a tuple/list of tuples
        if isinstance(values, tuple):
            rows.append(values)
        elif isinstance(values, list):
            rows.extend(values)

    if rows:
        df = pd.DataFrame(rows, columns=cfg["columns"])
        # Check for duplicates
        #df = df.drop_duplicates()
        out_path = PARQUET_DIR / f"{cfg['name']}.parquet"
        df.to_parquet(out_path, index=False)

        # create or replace a DuckDB view pointing to the parquet
        con.execute(f"CREATE OR REPLACE VIEW {cfg['name']} AS SELECT * FROM read_parquet('{out_path.as_posix()}')")

# Load loop
for cfg in TABLE_CONFIG:
    load_table_to_parquet(cfg)
    print("done with ", cfg['name'])


def build_cache(cur, table_name, id_col, name_col="name"):
    # Query the parquet-backed view in DuckDB
    cur.execute(f"SELECT {id_col}, {name_col} FROM {table_name}")
    return {name: _id for _id, name in cur.fetchall()}

ability_cache = build_cache(cur, "abilities", "ability_id")
type_cache = build_cache(cur, "pokemon_types_def", "type_id")
move_cache = build_cache(cur, "moves", "move_id")
move_learn_method_cache = build_cache(cur, "move_learn_methods", "move_learn_method_id")
version_cache = build_cache(cur, "versions", "version_id")
version_group_cache = build_cache(cur, "version_groups", "version_group_id")
stat_cache = build_cache(cur, "stats", "stat_id")
species_cache = build_cache(cur, "species", "species_id")
location_area_cache = build_cache(cur, "location_areas", "location_area_id")
encounter_method_cache = build_cache(cur, "encounter_methods", "encounter_method_id")
egg_group_cache = build_cache(cur, "egg_groups", "egg_group_id")
color_cache = build_cache(cur, "colors", "color_id")
shape_cache = build_cache(cur, "shapes", "shape_id")
generation_cache = build_cache(cur, "generations", "generation_id")


ability_list = []
type_list = []
stat_list = []
species_list = []
move_list = []
encounter_list = []
egg_group_list = []
move_type_list = []
color_list = []
shape_list = []
version_groups_generations_list = []
pokemon_generations_list = []


for folder in os.listdir("./PokeData/api/v2/pokemon"):
    folder_path = os.path.join("./PokeData/api/v2/pokemon", folder)
    if not os.path.isdir(folder_path):
        continue
    json_path = os.path.join(folder_path, "index.json")
    if not os.path.exists(json_path):
        continue
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    pokemon_id = data["id"]

    # pokemon_abilities
    for ability in data.get("abilities", []):
        ability_name = ability["ability"]["name"]
        ability_id = ability_cache.get(ability_name)
        if ability_id:
            ability_list.append((pokemon_id, ability_id))

    # pokemon_types
    for type in data.get("types", []):
        type_name = type["type"]["name"]
        type_id = type_cache.get(type_name)
        if type_id:
            type_list.append((pokemon_id, type_id))

    # pokemon_stats
    for stat in data.get("stats", []):
        stat_name = stat["stat"]["name"]
        stat_id = stat_cache.get(stat_name)
        value = stat['base_stat']
        if stat_id:
            stat_list.append((pokemon_id, stat_id, value))

    # pokemon_species
    species = data.get("species")
    if species:
        species_name = species['name']
        species_id = species_cache.get(species_name)
        if species_id:
            species_list.append((pokemon_id, species_id))

    # pokemon_moves
    for move in data.get("moves", []):
        move_name = move["move"]["name"]
        move_id = move_cache.get(move_name)
        if not move_id:
            continue

        for version_group in move.get('version_group_details', []):
            level_learned_at = version_group['level_learned_at']
            method_name = version_group['move_learn_method']['name']
            move_learn_method_id = move_learn_method_cache.get(method_name)
            version_group_name = version_group['version_group']['name']
            version_group_id = version_group_cache.get(version_group_name)

            if move_learn_method_id and version_group_id:
                move_list.append((pokemon_id, move_id, move_learn_method_id, version_group_id, level_learned_at))

    # pokemon_encounters
    encounter_path = os.path.join(folder_path, "encounters")
    if os.path.isdir(encounter_path):
        for enc_file in os.listdir(encounter_path):
            if not enc_file.endswith(".json"):
                continue
            json_path = os.path.join(encounter_path, enc_file)
            with open(json_path, "r", encoding="utf-8") as f:
                encounters = json.load(f)
            for encounter in encounters:
                location_area_name = encounter["location_area"]["name"]
                location_area_id = location_area_cache.get(location_area_name)
                if not location_area_id:
                    continue
                for version_detail in encounter.get("version_details", []):
                    version_name = version_detail["version"]["name"]
                    version_id = version_cache.get(version_name)
                    if not version_id:
                        continue
                    for detail in version_detail.get("encounter_details", []):
                        method_name = detail["method"]["name"]
                        encounter_method_id = encounter_method_cache.get(method_name)
                        if not encounter_method_id:
                            continue
                        min_level = detail.get("min_level", 0)
                        max_level = detail.get("max_level", 0)
                        encounter_list.append((pokemon_id, version_id, location_area_id, encounter_method_id, min_level, max_level))

# species_egg_groups
for folder in os.listdir("./PokeData/api/v2/pokemon-species"):
    folder_path = os.path.join("./PokeData/api/v2/pokemon-species", folder)
    if not os.path.isdir(folder_path):
        continue
    json_path = os.path.join(folder_path, "index.json")
    if not os.path.exists(json_path):
        continue
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    species_id = data["id"]
    for egg_group in data.get("egg_groups", []):
        egg_group_name = egg_group["name"]
        egg_group_id = egg_group_cache.get(egg_group_name)
        if egg_group_id:
            egg_group_list.append((species_id, egg_group_id))

    color_name = data['color']['name']
    color_id = color_cache.get(color_name)
    if color_id:
        color_list.append((species_id, color_id))

    shape_name = data['shape']['name']
    shape_id = shape_cache.get(shape_name)
    if shape_id:
        shape_list.append((species_id, shape_id))

# move_types
for folder in os.listdir("./PokeData/api/v2/move"):
    folder_path = os.path.join("./PokeData/api/v2/move", folder)
    if not os.path.isdir(folder_path):
        continue
    json_path = os.path.join(folder_path, "index.json")
    if not os.path.exists(json_path):
        continue
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    move_id = data["id"]
    type_name = data["type"]["name"]
    type_id = type_cache.get(type_name)
    if type_id:
        move_type_list.append((move_id, type_id))

# version_group_generations
for folder in os.listdir("./PokeData/api/v2/generation"):
    folder_path = os.path.join("./PokeData/api/v2/generation", folder)
    if not os.path.isdir(folder_path):
        continue
    json_path = os.path.join(folder_path, "index.json")
    if not os.path.exists(json_path):
        continue
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    generation_id = data['id']

    for vg in data['version_groups']:
        vg_name = vg['name']
        vg_id = version_group_cache.get(vg_name)
        version_groups_generations_list.append((vg_id, generation_id))


def write_parquet_and_view(table_name, columns, rows):
    if not rows:
        return
    df = pd.DataFrame(rows, columns=columns)
    #df = df.drop_duplicates()
    out_path = PARQUET_DIR / f"{table_name}.parquet"
    df.to_parquet(out_path, index=False)
    con.execute(f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_parquet('{out_path.as_posix()}')")

# write parquet + create view
write_parquet_and_view("pokemon_abilities", ["pokemon_id", "ability_id"], ability_list)
write_parquet_and_view("pokemon_types", ["pokemon_id", "type_id"], type_list)
write_parquet_and_view("pokemon_stats", ["pokemon_id","stat_id","value"], stat_list)
write_parquet_and_view("pokemon_species", ["pokemon_id","species_id"], species_list)
write_parquet_and_view("pokemon_moves", ["pokemon_id","move_id","move_learn_method_id","version_group_id","level_learned_at"], move_list)
write_parquet_and_view("pokemon_encounters", ["pokemon_id","version_id","location_area_id","encounter_method_id","min_level","max_level"], encounter_list)
write_parquet_and_view("species_egg_groups", ["species_id","egg_group_id"], egg_group_list)
write_parquet_and_view("move_types", ["move_id","type_id"], move_type_list)
write_parquet_and_view("species_colors", ["species_id","color_id"], color_list)
write_parquet_and_view("species_shapes", ["species_id","shape_id"], shape_list)
write_parquet_and_view("version_groups_generations", ["version_group_id","generation_id"], version_groups_generations_list)


con.commit()
version_groups_generations_cache = build_cache(cur, "version_groups_generations", "generation_id", "version_group_id")
print(version_groups_generations_cache)

# pokemon_generations
for folder in os.listdir("./PokeData/api/v2/pokemon"):
    folder_path = os.path.join("./PokeData/api/v2/pokemon", folder)
    if not os.path.isdir(folder_path):
        continue
    json_path = os.path.join(folder_path, "index.json")
    if not os.path.exists(json_path):
        continue
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    vg_set = set()
    pokemon_id = data["id"]
    if not data['moves']:
        earliest_gen = 8
    else:

        for move in data['moves']:
            for vgd in move['version_group_details']:
                vg_name = vgd['version_group']['name']
                vg_id = version_group_cache.get(vg_name)
                vg_gen = version_groups_generations_cache.get(vg_id)
                vg_set.add(vg_gen)
        earliest_gen = min(vg_set)

    pokemon_generations_list.append((pokemon_id, earliest_gen))


write_parquet_and_view("pokemon_generations", ["pokemon_id", "generation_id"], pokemon_generations_list)
con.commit()

con.close()
print("Wrote parquet files to:", PARQUET_DIR.resolve())
print("DuckDB database created:", DUCKDB_PATH)

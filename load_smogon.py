import os
import json
import sqlite3
import pandas as pd
import gzip
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("PG_DBNAME"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT")
)
cur = conn.cursor()

with open("schema.sql", "r", encoding="utf-8") as f:
    cur.execute(f.read())

variants = {
    "indeedee": "indeedee-male",
    "indeedee-f": "indeedee-female",
    "meowstic": "meowstic-male",
    "meowstic-f" : "meowstic-female",
    "basculegion": "basculegion-male",
    "basculegion-f": "basculegion-female",
    "oinkologne": "oinkologne-male",
    "oinkologne-f": "oinkologne-female",
    "ogerpon-hearthflame": "ogerpon-hearthflame-mask",
    "ogerpon-wellspring": "ogerpon-wellspring-mask",
    "ogerpon-cornerstone": "ogerpon-cornerstone-mask",
    "tornadus": "tornadus-incarnate",
    "landorus": "landorus-incarnate",
    "thundurus": "thundurus-incarnate",
    "enamorus": "enamorus-incarnate",
    "tatsugiri": "tatsugiri-curly",
    "urshifu": "urshifu-rapid-strike",
    "maushold": "maushold-family-of-four",
    "meloetta" : "meloetta-aria",
    "necrozma-dawn-wings" : "necrozma-dawn",
    "necrozma-dusk-mane" : "necrozma-dusk",
    "giratina": "giratina-altered",
    "palafin": "palafin-hero",
    "tauros-paldea-blaze": "tauros-paldea-blaze-breed",
    "tauros-paldea-combat": "tauros-paldea-combat-breed",
    "tauros-paldea-aqua": "tauros-paldea-aqua-breed",
    "dudunsparce" : "dudunsparce-three-segment",
    "keldeo": "keldeo-ordinary",
    "mimikyu": "mimikyu-disguised",
    "mimikyu-totem": "mimikyu-totem-disguised",
    "arceus-bug": "arceus",
    "arceus-dark": "arceus",
    "arceus-dragon": "arceus",
    "arceus-electric": "arceus",
    "arceus-fairy": "arceus",
    "arceus-fighting": "arceus",
    "arceus-fire": "arceus",
    "arceus-flying": "arceus",
    "arceus-ghost": "arceus",
    "arceus-grass": "arceus",
    "arceus-ground": "arceus",
    "arceus-ice": "arceus",
    "arceus-poison": "arceus",
    "arceus-psychic": "arceus",
    "arceus-rock": "arceus",
    "arceus-steel": "arceus",
    "arceus-water": "arceus",
    "toxtricity": "toxtricity-amped",
    "minior" : "minior-red",
    "lycanroc" : "lycanroc-midday",
    "morpeko" : "morpeko-full-belly",
    "shaymin" : "shaymin-land",
    "eiscue" : "eiscue-noice",
    "deoxys" : "deoxys-normal",
    "squawkabilly" : "squawkabilly-green-plumage",
    "basculin" : "basculin-red-striped",
    "oricorio" : 'oricorio-baile',
    "darmanitan" : 'darmanitan-standard',
    "gourgeist" : "gourgeist-average",
    "zygarde" : 'zygarde-50',
    "silvally-bug": "silvally",
    "silvally-dark": "silvally",
    "silvally-dragon": "silvally",
    "silvally-electric": "silvally",
    "silvally-fairy": "silvally",
    "silvally-fighting": "silvally",
    "silvally-fire": "silvally",
    "silvally-flying": "silvally",
    "silvally-ghost": "silvally",
    "silvally-grass": "silvally",
    "silvally-ground": "silvally",
    "silvally-ice": "silvally",
    "silvally-poison": "silvally",
    "silvally-psychic": "silvally",
    "silvally-rock": "silvally",
    "silvally-steel": "silvally",
    "silvally-water": "silvally",
    "aegislash" : "aegislash-shield",
    "wishiwashi" : "wishiwashi-school",
    "nidoranf" : "nidoran-f",
    "nidoranm" : "nidoran-m",
    "pumpkaboo" : "pumpkaboo-average",
    "wormadam" : "wormadam-plant",
    "marowak-alola-totem" : "marowak-totem",
    "darmanitan-galar" : "darmanitan-galar-standard",
    "rockruff-dusk" : "rockruff-own-tempo",
    "xerneas-neutral" : "xerneas"
}

item_variants = {
    "leek" : "stick",
    "miracleberry" : "lumberry",
    "mintberry" : "chestoberry",
    "goldberry" : "sitrusberry",
    "pinkbow" : "silkscarf",
    "polkadotbow" : "silkscarf",
    "przcureberry" : "cheriberry",
    "mysteryberry" : "leppaberry",
    "psncureberry" : "pechaberry",
    "bitterberry" : "persimberry",
    "iceberry" : "rawstberry",
    "burntberry" : "aspearberry",
    "berry" : "oranberry",
    "mail" : "likemail"
}

def normalize_name(name):
    # lowercase, replace spaces with hyphens, strip punctuation issues
    name = name.lower()
    name = name.replace(" ", "-")
    name = name.replace("'", "")
    name = name.replace(".", "")
    name = name.replace("%", "")
    name = name.replace(":", "")
    if "--" in name:
        name = name.split("--")[0]

    return name

# for file in os.listdir("./SmogonData/2025-09/chaos/gen9ou-0.json"):
#     json_path = os.path.join("./SmogonData/2025-09/chaos", file)
#     with open(json_path, "r", encoding="utf-8") as f:
#         data = json.load(f)
#     print(data["info"]["metagame"])

def build_cache(cur, table_name, id_col, name_col="name"):
    cur.execute(f"SELECT {id_col}, {name_col} FROM {table_name}")
    return {name: _id for _id, name in cur.fetchall()}

pokemon_cache = build_cache(cur, "pokemon", "pokemon_id")
item_cache = build_cache(cur, "items", "item_id", "normalized_name")
move_cache = build_cache(cur, "moves", "move_id", "normalized_name")
ability_cache = build_cache(cur, "abilities", "ability_id", "normalized_name")
type_cache = build_cache(cur, "pokemon_types_def", "type_id")
nature_cache = build_cache(cur, "natures", "nature_id")


months = ["2025-09"]


missed_pokemon = []
missed_moves = []
missed_items = []
missed_abilities = []



for month in months:

    print("starting ", month)
    data_dir = Path(f"./SmogonData/{month}/chaos/")
    month = month + "-01"

    for json_file in data_dir.glob("*.json"):

        if "cap" in json_file.name.lower() or "metronome" in json_file.name.lower():
            print(f"Skipping file: {json_file.name}")
            continue
        if not any(tier in json_file.name.lower() for tier in ["ou", "uu", "ru", "nu", "pu", "zu", "vgc", "double", "ubers", "mono", "1v1"]):
            print(f"Skipping file: {json_file.name}")
            continue

        print(f"{json_file.name}")
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            metagame = data['info']['metagame']
            cutoff = str(int(data['info']['cutoff']))
            num_battles = data['info']['number of battles']

            full_metagame = metagame + '-' + cutoff

            # battle_formats insert
            cur.execute("""
                INSERT INTO battle_formats (full_metagame, name, cutoff)
                VALUES (%s, %s, %s)
                ON CONFLICT (name, cutoff) DO NOTHING
            """, (full_metagame, metagame, cutoff))

            # monthly_stats insert
            cur.execute("""
                INSERT INTO monthly_stats (name, month, num_battles)
                VALUES (%s, %s, %s)
                ON CONFLICT (name, month) DO NOTHING
            """, (metagame, month, num_battles))

            # Retrieve metagame_id
            cur.execute("SELECT battle_format_id FROM battle_formats WHERE full_metagame = %s", (full_metagame,))
            result = cur.fetchone()
            if not result:
                print("could not find ", full_metagame)
                continue
            metagame_id = result[0]

            metagame = metagame + '-' + cutoff

            # Initialize all insert lists
            pokemon_usage_inserts = []
            smogon_abilities_inserts = []
            smogon_items_inserts = []
            smogon_moves_inserts = []
            smogon_teammates_inserts = []
            smogon_checks_inserts = []
            smogon_teras_inserts = []
            smogon_natures_inserts = []

            for pokemon_name, pokemon_data in data["data"].items():
                viability = pokemon_data["Viability Ceiling"]
                players_used, gxe_top, gxe_99, gxe_95 = viability
                normalized = normalize_name(pokemon_name)
                if normalized in variants:
                    normalized = variants[normalized]

                pokemon_id = pokemon_cache.get(normalized)
                raw_count = pokemon_data.get('Raw count')
                usage_percent = pokemon_data.get('usage')
                if usage_percent is not None:
                    usage_percent *= 100
                else:
                    usage_percent = (raw_count / (num_battles * 2)) * 100

                pokemon_usage_inserts.append(
                    (pokemon_id, raw_count, usage_percent, players_used, gxe_top, gxe_99, gxe_95, metagame_id, month)
                )

                if pokemon_id is None and normalized not in missed_pokemon:
                    missed_pokemon.append(normalized)

                # ABILITIES
                if "Abilities" in pokemon_data:
                    total_count = sum(pokemon_data["Abilities"].values())
                    for ability_name, ability_count in pokemon_data["Abilities"].items():
                        if not ability_name or ability_name.lower() in ("noability") or ability_count == 0:
                            ability_id = 0
                        else:
                            ability_id = ability_cache.get(ability_name)
                        if ability_id is None and ability_name not in missed_abilities:
                            missed_abilities.append(ability_name)
                        ability_perc = (ability_count / total_count) * 100
                        smogon_abilities_inserts.append((pokemon_id, ability_id, ability_count, ability_perc, month, metagame))

                # ITEMS
                if "Items" in pokemon_data:
                    for item_name, item_count in pokemon_data["Items"].items():
                        if item_name in item_variants:
                            item_name = item_variants[item_name]
                        if not item_name or item_name.lower() in ("nothing", "empty") or item_count == 0:
                            continue
                        item_id = item_cache.get(item_name)
                        if item_id is None and item_name not in missed_items:
                            missed_items.append(item_name)
                        smogon_items_inserts.append((pokemon_id, item_id, item_count, month, metagame))

                # TERAS
                if "Tera Types" in pokemon_data:
                    total_count = sum(pokemon_data["Tera Types"].values())
                    for type_name, type_count in pokemon_data["Tera Types"].items():
                        type_id = type_cache.get(type_name)
                        type_perc = ((type_count/total_count) * 100)
                        smogon_teras_inserts.append((pokemon_id, type_id, type_count, type_perc, month, metagame))

                # NATURES
                if "Spreads" in pokemon_data:
                    nature_counts = {}
                    for spread, count in pokemon_data["Spreads"].items():
                        nature = spread.split(":")[0]  # e.g. "Bold" from "Bold:252/0/252/0/4/0"
                        nature_counts[nature] = nature_counts.get(nature, 0) + count


                    total_count = sum(nature_counts.values())
                    for nature_name, nature_count in nature_counts.items():
                        nature_name = normalize_name(nature_name)
                        nature_id = nature_cache.get(nature_name)
                        nature_perc = (nature_count / total_count) * 100

                        smogon_natures_inserts.append(
                            (pokemon_id, nature_id, nature_count, nature_perc, month, metagame)
                        )

                # MOVES
                if "Moves" in pokemon_data:
                    total_count = sum(pokemon_data["Moves"].values())
                    for move_name, move_count in pokemon_data["Moves"].items():
                        if not move_name or move_name.lower() == "" or move_count == 0:
                            continue
                        if move_name == 'visegrip':
                            move_name = 'vicegrip'
                        move_id = move_cache.get(move_name)
                        if move_id is None and move_name not in missed_moves:
                            missed_moves.append(move_name)
                        move_perc = (move_count / (total_count / 4)) * 100
                        smogon_moves_inserts.append((pokemon_id, move_id, move_count, move_perc, month, metagame))

                # TEAMMATES
                if "Teammates" in pokemon_data:
                    for teammate_name, teammate_count in pokemon_data["Teammates"].items():
                        if not teammate_name or teammate_name.lower() == "empty" or teammate_count == 0:
                            continue
                        normalized_teammate = normalize_name(teammate_name)
                        if normalized_teammate in variants:
                            normalized_teammate = variants[normalized_teammate]
                        teammate_id = pokemon_cache.get(normalized_teammate)
                        smogon_teammates_inserts.append((pokemon_id, teammate_id, teammate_count, month, metagame))

                # CHECKS
                if "Checks and Counters" in pokemon_data:
                    for check_name, check_arr in pokemon_data["Checks and Counters"].items():
                        if not check_name or check_name.lower() == "empty":
                            continue
                        normalized_check = normalize_name(check_name)
                        if normalized_check in variants:
                            normalized_check = variants[normalized_check]
                        check_id = pokemon_cache.get(normalized_check)
                        check_count, check_perc, check_sd = check_arr
                        check_perc *= 100
                        smogon_checks_inserts.append((pokemon_id, check_id, check_count, check_perc, check_sd, month, metagame))

            # Single batch inserts per table per month
            with conn:
                if pokemon_usage_inserts:
                    execute_values(cur, """
                        INSERT INTO pokemon_usage
                        (pokemon_id, raw_count, usage_percent, players_used, gxe_top, gxe_99, gxe_95, metagame_id, month)
                        VALUES %s
                    """, pokemon_usage_inserts)

                if smogon_abilities_inserts:
                    execute_values(cur, """
                        INSERT INTO smogon_abilities
                        (pokemon_id, ability_id, ability_count, ability_perc, month, metagame)
                        VALUES %s
                    """, smogon_abilities_inserts)

                if smogon_items_inserts:
                    execute_values(cur, """
                        INSERT INTO smogon_items
                        (pokemon_id, item_id, item_count, month, metagame)
                        VALUES %s
                    """, smogon_items_inserts)

                if smogon_moves_inserts:
                    execute_values(cur, """
                        INSERT INTO smogon_moves
                        (pokemon_id, move_id, move_count, move_perc, month, metagame)
                        VALUES %s
                    """, smogon_moves_inserts)

                if smogon_teammates_inserts:
                    execute_values(cur, """
                        INSERT INTO smogon_teammates
                        (pokemon_id, teammate_id, teammate_count, month, metagame)
                        VALUES %s
                    """, smogon_teammates_inserts)

                if smogon_checks_inserts:
                    execute_values(cur, """
                        INSERT INTO smogon_checks
                        (pokemon_id, check_id, check_count, check_perc, check_sd, month, metagame)
                        VALUES %s
                    """, smogon_checks_inserts)

                if smogon_teras_inserts:
                    execute_values(cur, """
                        INSERT INTO smogon_teras
                        (pokemon_id, type_id, type_count, type_perc, month, metagame)
                        VALUES %s
                    """, smogon_teras_inserts)



print("missed abilities", missed_abilities)
print("missed moves", missed_moves)
print("missed items", missed_items)

conn.commit()
conn.close()




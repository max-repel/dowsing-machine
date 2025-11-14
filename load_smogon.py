import duckdb
import json
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


# --- Config ---
PARQUET_DIR = Path("./parquet")
PARQUET_DIR.mkdir(exist_ok=True)

months = ["2014-11"]  # example month
tiers = ["ou", "uu", "ru", "nu", "pu", "zu", "vgc", "double", "ubers", "mono", "1v1"]

# --- DuckDB connection ---
con = duckdb.connect("dowsing-machine.duckdb")

# --- Helper functions ---
def normalize_name(name):
    name = name.lower().replace(" ", "-").replace("'", "").replace(".", "").replace("%", "").replace(":", "")
    if "--" in name:
        name = name.split("--")[0]
    return name

# Get list of all available months
BASE_URL = "https://www.smogon.com/stats/"

# def fetch_smogon_months():
#     url = "https://www.smogon.com/stats/"
#     resp = requests.get(url)
#     resp.raise_for_status()

#     soup = BeautifulSoup(resp.text, "html.parser")

#     months = []

#     # Smogon lists folders as <a href="2020-06/">2020-06/</a>
#     for link in soup.find_all("a"):
#         href = link.get("href", "")
#         # months always end with "/"
#         if href.endswith("/") and href[0].isdigit():
#             # remove trailing slash
#             months.append(href[:-1])

#     return months


# months = fetch_smogon_months()
# print(months)
months = ['2025-08', '2025-09']

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

def build_cache(con, table_name, id_col, name_col="name"):
    if con.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'").fetchone()[0] == 0:
        return {}
    res = con.execute(f"SELECT {id_col}, {name_col} FROM {table_name}").fetchall()
    return {name: _id for _id, name in res}


def write_table(name, columns, rows, month_str=None):
    if not rows:
        return


    if month_str is None:
        month_str = datetime.now().strftime("%Y-%m")


    month_folder = PARQUET_DIR / month_str
    month_folder.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows, columns=columns)


    path = month_folder / f"{name}.parquet"
    df.to_parquet(path, index=False)


    con.execute(
        f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM read_parquet('{path.as_posix()}')"
    )


pokemon_cache = build_cache(con, "pokemon", "pokemon_id")
item_cache = build_cache(con, "items", "item_id", "normalized_name")
move_cache = build_cache(con, "moves", "move_id", "normalized_name")
ability_cache = build_cache(con, "abilities", "ability_id", "normalized_name")
type_cache = build_cache(con, "pokemon_types_def", "type_id")
nature_cache = build_cache(con, "natures", "nature_id")



BASE_URL = "https://www.smogon.com/stats"

for month in months:

    battle_formats_rows = []
    monthly_stats_rows = []
    pokemon_usage_rows = []
    smogon_abilities_rows = []
    smogon_items_rows = []
    smogon_moves_rows = []
    smogon_teammates_rows = []
    smogon_teras_rows = []
    smogon_natures_rows = []
    smogon_checks_rows = []

    battle_formats_dict = {}

    print("Processing month:", month)
    data_dir = Path(f"./SmogonData/{month}/chaos/")
    month_date = month + "-01"

    for json_file in data_dir.glob("*.json"):
        print(json_file)
        fname = json_file.name.lower()
        if "cap" in fname or "metronome" in fname:
            continue
        if not any(tier in fname for tier in tiers):
            continue

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Battle format
        metagame = data['info']['metagame']
        cutoff = str(int(data['info']['cutoff']))
        full_metagame = f"{metagame}-{cutoff}"
        num_battles = data['info']['number of battles']

        if full_metagame not in battle_formats_dict:
            battle_format_id = len(battle_formats_dict) + 1
            battle_formats_dict[full_metagame] = battle_format_id
            battle_formats_rows.append((battle_format_id, full_metagame, metagame, cutoff))
        else:
            battle_format_id = battle_formats_dict[full_metagame]

        monthly_stats_rows.append((full_metagame, month_date, num_battles))

        seen_pairs = set()

        for pokemon_name, pokemon_data in data["data"].items():
            normalized = normalize_name(pokemon_name)
            if normalized in variants:
                normalized = variants[normalized]
            pokemon_id = pokemon_cache.get(normalized)

            # Pokemon usage
            viability = pokemon_data["Viability Ceiling"]
            players_used, gxe_top, gxe_99, gxe_95 = viability
            raw_count = pokemon_data.get('Raw count')
            usage_percent = pokemon_data.get('usage')
            if usage_percent is not None:
                usage_percent *= 100
            else:
                usage_percent = (raw_count / (num_battles * 2)) * 100

            pokemon_usage_rows.append(
                (pokemon_id, raw_count, usage_percent, players_used, gxe_top, gxe_99, gxe_95, battle_format_id, month_date)
            )

            # Abilities
            if "Abilities" in pokemon_data:
                total_count = sum(pokemon_data["Abilities"].values())
                for ability_name, ability_count in pokemon_data["Abilities"].items():
                    ability_id = ability_cache.get(ability_name)
                    ability_perc = (ability_count / total_count) * 100 if total_count else 0
                    smogon_abilities_rows.append(
                        (pokemon_id, ability_id, ability_count, ability_perc, month_date, full_metagame)
                    )

            # Items
            if "Items" in pokemon_data:
                for item_name, item_count in pokemon_data["Items"].items():
                    if item_name in item_variants:
                        item_name = item_variants[item_name]
                    item_id = item_cache.get(item_name)
                    smogon_items_rows.append((pokemon_id, item_id, item_count, month_date, full_metagame))

            # Moves
            if "Moves" in pokemon_data:
                total_count = sum(pokemon_data["Moves"].values())
                for move_name, move_count in pokemon_data["Moves"].items():
                    move_id = move_cache.get(move_name)
                    move_perc = (move_count / (total_count / 4)) * 100 if total_count else 0
                    smogon_moves_rows.append((pokemon_id, move_id, move_count, move_perc, month_date, full_metagame))

            # Teammates
            if "Teammates" in pokemon_data:
                for teammate_name, teammate_count in pokemon_data["Teammates"].items():
                    normalized_teammate = normalize_name(teammate_name)
                    if normalized_teammate in variants:
                        normalized_teammate = variants[normalized_teammate]
                    teammate_id = pokemon_cache.get(normalized_teammate)
                    if not teammate_id or teammate_id == pokemon_id or not pokemon_id:
                        continue
                    id1, id2 = sorted([pokemon_id, teammate_id])
                    key = (id1, id2, month_date, full_metagame)
                    if key in seen_pairs:
                        continue
                    seen_pairs.add(key)
                    smogon_teammates_rows.append((id1, id2, teammate_count, month_date, full_metagame))

            # Tera types
            if "Tera Types" in pokemon_data:
                total_count = sum(pokemon_data["Tera Types"].values())
                for type_name, type_count in pokemon_data["Tera Types"].items():
                    type_id = type_cache.get(type_name)
                    type_perc = (type_count / total_count) * 100 if total_count else 0
                    smogon_teras_rows.append((pokemon_id, type_id, type_count, type_perc, month_date, full_metagame))

            # Natures
            if "Spreads" in pokemon_data:
                nature_counts = {}
                for spread, count in pokemon_data["Spreads"].items():
                    nature = spread.split(":")[0]
                    nature_counts[nature] = nature_counts.get(nature, 0) + count
                total_count = sum(nature_counts.values())
                for nature_name, nature_count in nature_counts.items():
                    nature_id = nature_cache.get(normalize_name(nature_name))
                    nature_perc = (nature_count / total_count) * 100 if total_count else 0
                    smogon_natures_rows.append((pokemon_id, nature_id, nature_count, nature_perc, month_date, full_metagame))

            # Checks
            if "Checks and Counters" in pokemon_data:
                for check_name, check_arr in pokemon_data["Checks and Counters"].items():
                    check_id = pokemon_cache.get(normalize_name(check_name))
                    check_count, check_perc, check_sd = check_arr
                    check_perc *= 100
                    smogon_checks_rows.append((pokemon_id, check_id, check_count, check_perc, check_sd, month_date, full_metagame))

# --- Write tables to Parquet and create DuckDB views ---
# def write_table(name, columns, rows):
#     if not rows:
#         return
#     df = pd.DataFrame(rows, columns=columns)
#     path = PARQUET_DIR / f"{name}.parquet"
#     df.to_parquet(path, index=False)
#     con.execute(f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM read_parquet('{path.as_posix()}')")





    write_table("battle_formats", ["battle_format_id", "full_metagame", "name", "cutoff"], battle_formats_rows, month)
    write_table("monthly_stats", ["full_metagame", "month", "num_battles"], monthly_stats_rows, month)
    write_table("pokemon_usage", ["pokemon_id","raw_count","usage_percent","players_used","gxe_top","gxe_99","gxe_95","battle_format_id","month"], pokemon_usage_rows, month)
    write_table("smogon_abilities", ["pokemon_id","ability_id","ability_count","ability_perc","month","metagame"], smogon_abilities_rows, month)
    write_table("smogon_items", ["pokemon_id","item_id","item_count","month","metagame"], smogon_items_rows, month)
    write_table("smogon_moves", ["pokemon_id","move_id","move_count","move_perc","month","metagame"], smogon_moves_rows, month)
    write_table("smogon_teammates", ["pokemon_id","teammate_id","teammate_count","month","metagame"], smogon_teammates_rows, month)
    write_table("smogon_teras", ["pokemon_id","type_id","type_count","type_perc","month","metagame"], smogon_teras_rows, month)
    write_table("smogon_natures", ["pokemon_id","nature_id","nature_count","nature_perc","month","metagame"], smogon_natures_rows, month)
    write_table("smogon_checks", ["pokemon_id","check_id","check_count","check_perc","check_sd","month","metagame"], smogon_checks_rows, month)


print("All data ingested into DuckDB and Parquet views!")

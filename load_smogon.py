import duckdb
import json
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import orjson
import aiohttp
import asyncio
from urllib.parse import urljoin


PARQUET_DIR = Path("./parquet")
PARQUET_DIR.mkdir(exist_ok=True)

BASE_URL = "https://www.smogon.com/stats/"
tiers = ["ou", "uu", "ru", "nu", "pu", "zu", "vgc", "double", "ubers", "mono", "1v1"]
con = duckdb.connect("dowsing-machine.duckdb")


con.execute("DROP SEQUENCE IF EXISTS seq_metagame;")
con.execute("CREATE SEQUENCE IF NOT EXISTS seq_metagame START WITH 1;")

con.execute("""
DROP TABLE IF EXISTS metagames;
""")

# Create table
con.execute("""
CREATE TABLE IF NOT EXISTS metagames (
    metagame_id INTEGER PRIMARY KEY DEFAULT NEXTVAL('seq_metagame'),
    full_metagame TEXT UNIQUE,
    metagame TEXT,
    generation INTEGER,
    cutoff INTEGER
);
""")

# Helpers
def normalize_name(name):
    name = name.lower().replace(" ", "-").replace("'", "").replace(".", "").replace("%", "").replace(":", "")
    if "--" in name:
        name = name.split("--")[0]
    return name

def fetch_smogon_months():
    url = "https://www.smogon.com/stats/"
    resp = requests.get(url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    months = []

    for link in soup.find_all("a"):
        href = link.get("href", "")
        if href.endswith("/") and href[0].isdigit():
            months.append(href[:-1])

    return months


def build_cache(con, table_name, id_col, name_col="name"):
    if con.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'").fetchone()[0] == 0:
        return {}
    res = con.execute(f"SELECT {id_col}, {name_col} FROM {table_name}").fetchall()
    return {name: _id for _id, name in res}



# My own list of months to test smaller data
# months = ['2015-01', '2016-01', '2017-01', '2018-01', '2019-01', '2020-01', '2021-01', '2022-01', '2023-01', '2024-01', '2025-01']
months = ['2015-01', '2015-02']

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
    "mail" : "likemail",
    'psychiumz': 'psychiumzheld',
    'decidiumz': 'decidiumzheld',
    'pikashuniumz': 'pikashuniumzheld',
    'normaliumz': 'normaliumzheld',
    'flyiniumz': 'flyiniumzheld',
    'fairiumz': 'fairiumzheld',
    'marshadiumz': 'marshadiumzheld',
    'eeviumz': 'eeviumzheld',
    'pikaniumz': 'pikaniumzheld',
    'wateriumz': 'wateriumzheld',
    'electriumz': 'electriumzheld',
    'ghostiumz': 'ghostiumzheld',
    'grassiumz': 'grassiumzheld',
    'buginiumz': 'buginiumzheld',
    'iciumz': 'iciumzheld',
    'mewniumz': 'mewniumzheld',
    'inciniumz': 'inciniumzheld',
    'rockiumz': 'rockiumzheld',
    'fightiniumz': 'fightiniumzheld',
    'poisoniumz': 'poisoniumzheld',
    'mimikiumz': 'mimikiumzheld',
    'firiumz': 'firiumzheld',
    'aloraichiumz': 'aloraichiumzheld',
    'tapuniumz': 'tapuniumzheld',
    'lycaniumz': 'lycaniumzheld',
    'snorliumz': 'snorliumzheld',
    'primariumz': 'primariumzheld',
    'lunaliumz': 'lunaliumzheld',
    'kommoniumz': 'kommoniumzheld',
    'groundiumz': 'groundiumzheld',
    'steeliumz': 'steeliumzheld',
    'solganiumz': 'solganiumzheld',
    'darkiniumz': 'darkiniumzheld',
    'ultranecroziumz': 'ultranecroziumzheld',
    'dragoniumz': 'dragoniumzheld'
}

pokemon_cache = build_cache(con, "pokemon", "pokemon_id")
item_cache = build_cache(con, "items", "item_id", "normalized_name")
move_cache = build_cache(con, "moves", "move_id", "normalized_name")
ability_cache = build_cache(con, "abilities", "ability_id", "normalized_name")
type_cache = build_cache(con, "pokemon_types_def", "type_id")
nature_cache = build_cache(con, "natures", "nature_id")

# Writer for parquet folders
def write_table(name, columns, rows, month_str):

    if not rows:
        return

    table_folder = PARQUET_DIR / name
    table_folder.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows, columns=columns)

    # File is named by month (2025-01.parquet)
    path = table_folder / f"{month_str}.parquet"

    df.to_parquet(path, index=False)

    # Create a view that reads ALL monthly parquet files for this table
    con.execute(
        f"""
        CREATE OR REPLACE VIEW {name} AS
        SELECT * FROM read_parquet('{(table_folder / "*.parquet").as_posix()}');
        """
    )



# Async json get
async def get_json_file_urls(month):
    base = f"https://www.smogon.com/stats/{month}/chaos/"
    async with aiohttp.ClientSession() as session:
        async with session.get(base) as resp:
            resp.raise_for_status()
            html = await resp.text()
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if not href.endswith(".json"):
            continue
        if "cap" in href or "metronome" in href or "random" in href or "challenge" in href or "hack" in href or "custom" in href:
            continue
        if not any(tier in href for tier in tiers):
            continue
        urls.append(urljoin(base, a["href"]))
    return urls

async def fetch_json(session, url):
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            content = await resp.read()
            return url, orjson.loads(content)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return url, None

async def fetch_month_jsons(month, max_concurrent=20):
    urls = await get_json_file_urls(month)
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async with aiohttp.ClientSession() as session:
        async def sem_fetch(url):
            async with semaphore:
                return await fetch_json(session, url)

        tasks = [sem_fetch(url) for url in urls]
        for future in asyncio.as_completed(tasks):
            url, data = await future
            results.append((url, data))
            print(f"[{len(results)}/{len(urls)}] Fetched {url}")

    return results

def get_generation_from_metagame(metagame):
    m = re.match(r"gen([1-9])", metagame.lower())
    return int(m.group(1)) if m else 6

def get_or_create_metagame_id(con, full_metagame, metagame, cutoff, generation):

    # row = con.execute(
    #     "SELECT metagame_id FROM metagames WHERE full_metagame = ?",
    #     [full_metagame],
    # ).fetchone()

    # if row is not None:
    #     return row[0]

    # new_id = con.execute("SELECT nextval('seq_metagame')").fetchone()[0]
    # con.execute(
    #     """
    #     INSERT INTO metagames_test (metagame_id, full_metagame, metagame, cutoff, generation)
    #     VALUES (?, ?, ?, ?, ?)
    #     """,
    #     [new_id, full_metagame, metagame, cutoff, generation],
    # )

    # return new_id
    row = con.execute(
        "SELECT metagame_id FROM metagames WHERE full_metagame = ?",
        [full_metagame],
    ).fetchone()

    if row:
        return row[0]

    try:
        con.execute("""
            INSERT INTO metagames (full_metagame, metagame, cutoff, generation)
            VALUES (?, ?, ?, ?)
        """, [full_metagame, metagame, cutoff, generation])
    except Exception:
        # Another thread inserted it at the same moment
        pass

    row = con.execute("""
        SELECT metagame_id FROM metagames WHERE full_metagame = ?
    """, [full_metagame]).fetchone()

    return row[0]




# Load each month
def process_jsons(month, json_files_data):
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
    monthly_stats_seen = set()

    battle_formats_dict = {}
    month_date = month + "-01"

    missed_pokemon = set()
    missed_items = set()
    missed_abilities = set()
    missed_moves = set()

    for url, data in json_files_data:
        if data is None:
            continue

        # Battle format
        metagame = data['info']['metagame']
        if not metagame.startswith("gen"):
            metagame = "gen6" + metagame

        generation = get_generation_from_metagame(metagame)

        cutoff = str(int(data['info']['cutoff']))
        full_metagame = f"{metagame}-{cutoff}"
        num_battles = data['info']['number of battles']

        # if full_metagame not in battle_formats_dict:
        #     battle_format_id = len(battle_formats_dict) + 1
        #     battle_formats_dict[full_metagame] = battle_format_id
        #     battle_formats_rows.append((battle_format_id, full_metagame, metagame, cutoff, generation))
        # else:
        #     battle_format_id = battle_formats_dict[full_metagame]


        # if metagame not in monthly_stats_seen:
        #     monthly_stats_rows.append((metagame, month_date, num_battles))
        #     monthly_stats_seen.add(metagame)

        metagame_id = get_or_create_metagame_id(con, full_metagame, metagame, cutoff, generation)

        if metagame not in monthly_stats_seen:
            monthly_stats_rows.append((metagame_id, metagame, month_date, num_battles))
            monthly_stats_seen.add(metagame)

        # Set to remove duplicates from inverse entries for smogon_teammates
        seen_pairs = set()

        for pokemon_name, pokemon_data in data["data"].items():
            normalized = normalize_name(pokemon_name)
            if normalized in variants:
                normalized = variants[normalized]
            pokemon_id = pokemon_cache.get(normalized)

            if not pokemon_id:
                missed_pokemon.add(normalized)
            # Pokemon usage

            if "Viability Ceiling" in pokemon_data:

                viability = pokemon_data["Viability Ceiling"]
                players_used, gxe_top, gxe_99, gxe_95 = viability
            else:
                viability = [0,0,0,0]
                players_used, gxe_top, gxe_99, gxe_95 = viability
            raw_count = pokemon_data.get('Raw count')
            usage_percent = pokemon_data.get('usage')
            if usage_percent is not None:
                usage_percent *= 100
            else:
                usage_percent = (raw_count / (num_battles * 2)) * 100

            pokemon_usage_rows.append(
                (pokemon_id, raw_count, usage_percent, players_used, gxe_top, gxe_99, gxe_95, metagame_id, month_date)
            )

            # Abilities
            if "Abilities" in pokemon_data:
                total_count = sum(pokemon_data["Abilities"].values())
                for ability_name, ability_count in pokemon_data["Abilities"].items():
                    ability_id = ability_cache.get(ability_name)
                    if not ability_id:
                        missed_abilities.add(ability_name)
                    ability_perc = (ability_count / total_count) * 100 if total_count else 0
                    smogon_abilities_rows.append(
                        (pokemon_id, ability_id, ability_count, ability_perc, month_date, full_metagame, metagame_id)
                    )

            # Items
            if "Items" in pokemon_data:
                total_count = sum(pokemon_data["Items"].values())
                for item_name, item_count in pokemon_data["Items"].items():
                    if item_name in item_variants:
                        item_name = item_variants[item_name]
                    if not item_name or item_name.lower() in ("nothing", "empty", "berserkgene", "metalalloy") or item_count == 0:
                        continue
                    item_id = item_cache.get(item_name)
                    if item_id is None and item_name not in missed_items:
                        missed_items.add(item_name)
                    item_perc = (item_count / total_count) * 100 if total_count else 0
                    smogon_items_rows.append((pokemon_id, item_id, item_count, item_perc, month_date, full_metagame, metagame_id))

            # Moves
            if "Moves" in pokemon_data:
                total_count = sum(pokemon_data["Moves"].values())
                for move_name, move_count in pokemon_data["Moves"].items():
                    if not move_name or move_name.lower() == "" or move_count == 0:
                        continue
                    if move_name == 'visegrip':
                        move_name = 'vicegrip'
                    move_id = move_cache.get(move_name)
                    if move_id is None and move_name not in missed_moves:
                        missed_moves.add(move_name)
                    move_perc = (move_count / (total_count / 4)) * 100
                    smogon_moves_rows.append((pokemon_id, move_id, move_count, move_perc, month_date, full_metagame, metagame_id))

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
                    smogon_teammates_rows.append((id1, id2, teammate_count, month_date, full_metagame, metagame_id))

            # Tera types
            if "Tera Types" in pokemon_data:
                total_count = sum(pokemon_data["Tera Types"].values())
                for type_name, type_count in pokemon_data["Tera Types"].items():
                    type_id = type_cache.get(type_name)
                    type_perc = (type_count / total_count) * 100 if total_count else 0
                    smogon_teras_rows.append((pokemon_id, type_id, type_count, type_perc, month_date, full_metagame, metagame_id))

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
                    smogon_natures_rows.append((pokemon_id, nature_id, nature_count, nature_perc, month_date, full_metagame, metagame_id))

            # Checks
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
                    smogon_checks_rows.append((pokemon_id, check_id, check_count, check_perc, check_sd, month_date, full_metagame, metagame_id))

    # Writer

    #write_table("battle_formats", ["battle_format_id", "full_metagame", "name", "cutoff", "generation"], battle_formats_rows, month)
    write_table("monthly_stats", ["metagame_id","metagame", "month", "num_battles"], monthly_stats_rows, month)
    write_table("pokemon_usage", ["pokemon_id","raw_count","usage_percent","players_used","gxe_top","gxe_99","gxe_95","metagame_id","month"], pokemon_usage_rows, month)
    write_table("smogon_abilities", ["pokemon_id","ability_id","ability_count","ability_perc","month","metagame","metagame_id"], smogon_abilities_rows, month)
    write_table("smogon_items", ["pokemon_id","item_id","item_count","item_perc","month","metagame","metagame_id"], smogon_items_rows, month)
    write_table("smogon_moves", ["pokemon_id","move_id","move_count","move_perc","month","metagame","metagame_id"], smogon_moves_rows, month)
    write_table("smogon_teammates", ["pokemon_id","teammate_id","teammate_count","month","metagame","metagame_id"], smogon_teammates_rows, month)
    write_table("smogon_teras", ["pokemon_id","type_id","type_count","type_perc","month","metagame","metagame_id"], smogon_teras_rows, month)
    write_table("smogon_natures", ["pokemon_id","nature_id","nature_count","nature_perc","month","metagame","metagame_id"], smogon_natures_rows, month)
    write_table("smogon_checks", ["pokemon_id","check_id","check_count","check_perc","check_sd","month","metagame","metagame_id"], smogon_checks_rows, month)

    # Check data that I missed
    print("missed pokemon: ", missed_pokemon)
    print("missed items: ", missed_items)
    print("missed abilities", missed_abilities)
    print("missed moves", missed_moves)

async def main(months):
    for month in months:
        print(f"\nProcessing month: {month}")
        json_files_data = await fetch_month_jsons(month)
        process_jsons(month, json_files_data)

# Run main
asyncio.run(main(months))

import os
import json
import sqlite3
import pandas as pd
import gzip
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed


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


conn = sqlite3.connect("silph-scope.db")
cur = conn.cursor()

with open("schema.sql", "r", encoding="utf-8") as f:
    cur.executescript(f.read())


def build_cache(cur, table_name, id_col, name_col="name"):
    cur.execute(f"SELECT {id_col}, {name_col} FROM {table_name}")
    return {name: _id for _id, name in cur.fetchall()}


# Load in all of the months
url = "https://www.smogon.com/stats/"
r = requests.get(url)
months = []
if r.status_code == 200:
    soup = BeautifulSoup(r.text, "html.parser")
    months = [a['href'].rstrip('/') for a in soup.find_all('a') if a.get('href', '').endswith('/')]
    months = months[1:]
    print(months)
else:
    print("Failed")

# Loading all formats possible to battle_formats
session = requests.Session()

for month in months:
    url = f"https://www.smogon.com/stats/{month}/chaos"
    r = session.get(url, timeout=10)

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        files = [
            a['href'].removesuffix('.json')
            for a in soup.find_all('a')
            if a.get('href', '').endswith('.json') and "cap" not in a['href'].lower()
        ]
        cur.executemany(
            "INSERT OR IGNORE INTO battle_formats (name) VALUES (?)",
            [(f,) for f in files]
        )
    else:
        print("Failed", month)

conn.commit()

month = "2020-01"
# Getting all json files from a specific url
url = f"https://www.smogon.com/stats/{month}/chaos"
files = []
r = session.get(url)

if r.status_code == 200:
    soup = BeautifulSoup(r.text, "html.parser")

    files = [
        a['href'].removesuffix('.json')
        for a in soup.find_all('a')
        if a.get('href', '').endswith('.json') and "cap" not in a['href'].lower() and "metronome" not in a['href'].lower() and "21v1" not in a['href'].lower()
    ]
    print(files)
else:
    print("Failed")



def normalize_name(name):
    # lowercase, replace spaces with hyphens, strip punctuation issues
    name = name.lower()
    name = name.replace(" ", "-")
    name = name.replace("'", "")
    name = name.replace(".", "")
    name = name.replace("%", "")
    name = name.replace(":", "")
    return name

battle_format_cache = build_cache(cur, "battle_formats", "battle_format_id")
pokemon_cache = build_cache(cur, "pokemon", "pokemon_id")

for month in months:
    url = f"https://www.smogon.com/stats/{month}/chaos"
    files = []
    r = session.get(url)

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")

        files = [
            a['href'].removesuffix('.json')
            for a in soup.find_all('a')
            if a.get('href', '').endswith('.json') and "cap" not in a['href'].lower() and "metronome" not in a['href'].lower() and "21v1" not in a['href'].lower()
        ]
        print(files)
    else:
        print("Failed")

    for file in files:
        url = f"https://www.smogon.com/stats/{month}/chaos/{file}.json"
        print(file)
        r = session.get(url)
        data = r.json()

        battle_format_name = file
        # cur.execute("SELECT battle_format_id FROM battle_formats WHERE battle_format_name = ?", (battle_format_name,))
        # bf_result = cur.fetchone()
        # if not bf_result:
        #     print("could not find battle format", battle_format_name)
        #     continue
        # battle_format_id = bf_result[0]
        battle_format_id = battle_format_cache.get(battle_format_name)

        usage_list = []
        for name in data['data']:

            normalized = normalize_name(name)
            if normalized in variants:
                normalized = variants[normalized]
            # cur.execute("SELECT pokemon_id FROM pokemon WHERE name = ?", (normalized,))
            # result = cur.fetchone()
            # if not result:
            #     print("could not find ", normalized)
            # pokemon_id = result[0]
            pokemon_id = pokemon_cache.get(normalized)
            raw_count = data['data'][name].get('Raw count')
            num_battles = data['info']["number of battles"]
            usage_percent = data['data'][name].get('usage')
            if usage_percent is None:
                usage_percent = raw_count / (num_battles * 2)


            usage_list.append((pokemon_id, battle_format_id, raw_count, usage_percent, month))

        cur.executemany("""
            INSERT INTO pokemon_usage (pokemon_id, battle_format_id, raw_count, usage_percent, month)
            VALUES (?, ?, ?, ?, ?)
        """, usage_list)


conn.commit()
cur.close()
conn.close()





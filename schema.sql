CREATE TABLE IF NOT EXISTS pokemon (
    pokemon_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    height INTEGER,
    weight INTEGER,
    base_experience INTEGER
);

CREATE TABLE IF NOT EXISTS species (
    species_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS abilities (
    ability_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    generation TEXT
);

CREATE TABLE IF NOT EXISTS moves (
    move_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    generation TEXT,
    power INTEGER,
    accuracy INTEGER,
    pp INTEGER,
    priority INTEGER
);

CREATE TABLE IF NOT EXISTS berries (
    berry_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS egg_groups (
    egg_group_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS encounter_conds (
    encounter_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS encounter_values (
    encounter_value_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS encounter_methods (
    encounter_method_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evolution_chains (
    evolution_chain_id SERIAL PRIMARY KEY,
    evolution_chain_id2 INTEGER
);

CREATE TABLE IF NOT EXISTS evolution_triggers (
    evolution_trigger_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS genders (
    gender_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS generations (
    generation_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS growth_rates (
    growth_rate_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS items (
    item_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    cost INTEGER,
    fling_power INTEGER,
    normalized_name TEXT
);

CREATE TABLE IF NOT EXISTS item_attributes (
    item_attribute_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS item_categories (
    item_category_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS item_fling_effects (
    item_fling_effect_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS item_pockets (
    item_pocket_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS locations (
    location_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS location_areas (
    location_area_id SERIAL PRIMARY KEY,
    location_name TEXT NOT NULL,
    name TEXT
);

CREATE TABLE IF NOT EXISTS machines (
    machine_id SERIAL PRIMARY KEY,
    item_name TEXT NOT NULL,
    move_name TEXT
);

CREATE TABLE IF NOT EXISTS move_ailments (
    move_ailment_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS move_battle_styles (
    move_battle_style_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS move_categories(
    move_category_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS move_damage_classes (
    move_damage_class_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS move_learn_methods (
    move_learn_method_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS move_targets (
    move_target_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS natures (
    nature_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    decreased_stat TEXT,
    increased_stat TEXT
);

CREATE TABLE IF NOT EXISTS pokedexes (
    pokedex_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS colors (
    color_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS shapes (
    shape_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS habitats (
    habitat_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS regions (
    region_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stats (
    stat_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

-- renamed type table to avoid reserved keyword conflict
CREATE TABLE IF NOT EXISTS pokemon_types_def (
    type_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS versions (
    version_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS version_groups (
    version_group_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    order_num INTEGER
);


-- =========================
-- Linking Tables
-- =========================

CREATE TABLE IF NOT EXISTS pokemon_abilities (
    pokemon_id INTEGER REFERENCES pokemon(pokemon_id),
    ability_id INTEGER REFERENCES abilities(ability_id),
    PRIMARY KEY (pokemon_id, ability_id)
);

DROP TABLE IF EXISTS pokemon_generations;
CREATE TABLE IF NOT EXISTS pokemon_generations (
    pokemon_id INTEGER REFERENCES pokemon(pokemon_id),
    generation_id INTEGER REFERENCES version_groups(version_group_id),
    PRIMARY KEY (pokemon_id, generation_id)
);


CREATE TABLE IF NOT EXISTS pokemon_types (
    pokemon_id INTEGER REFERENCES pokemon(pokemon_id),
    type_id INTEGER REFERENCES pokemon_types_def(type_id),
    PRIMARY KEY (pokemon_id, type_id)
);


CREATE TABLE IF NOT EXISTS pokemon_species (
    pokemon_id INTEGER REFERENCES pokemon(pokemon_id),
    species_id INTEGER REFERENCES species(species_id),
    PRIMARY KEY (pokemon_id, species_id)
);

CREATE TABLE IF NOT EXISTS species_egg_groups (
    species_id INTEGER REFERENCES species(species_id),
    egg_group_id INTEGER REFERENCES egg_groups(egg_group_id),
    PRIMARY KEY (species_id, egg_group_id)
);

CREATE TABLE IF NOT EXISTS pokemon_moves (
    pokemon_id INTEGER REFERENCES pokemon(pokemon_id),
    move_id INTEGER REFERENCES moves(move_id),
    move_learn_method_id INTEGER REFERENCES move_learn_methods(move_learn_method_id),
    version_group_id INTEGER REFERENCES version_groups(version_group_id),
    level_learned_at INTEGER,
    PRIMARY KEY (pokemon_id, move_id, move_learn_method_id, version_group_id)
);

CREATE TABLE IF NOT EXISTS pokemon_encounters (
    pokemon_id INTEGER REFERENCES pokemon(pokemon_id),
    version_id INTEGER REFERENCES versions(version_id),
    location_area_id INTEGER REFERENCES location_areas(location_area_id),
    encounter_method_id INTEGER REFERENCES encounter_methods(encounter_method_id),
    min_level INTEGER,
    max_level INTEGER,
    PRIMARY KEY (pokemon_id, version_id, location_area_id, encounter_method_id)
);

CREATE TABLE IF NOT EXISTS pokemon_stats (
    pokemon_id INTEGER REFERENCES pokemon(pokemon_id),
    stat_id INTEGER REFERENCES stats(stat_id),
    value INTEGER,
    PRIMARY KEY (pokemon_id, stat_id)
);

CREATE TABLE IF NOT EXISTS move_types (
    move_id INTEGER REFERENCES moves(move_id),
    type_id INTEGER REFERENCES pokemon_types_def(type_id),
    PRIMARY KEY (move_id, type_id)
);

CREATE TABLE IF NOT EXISTS species_colors (
    species_id INTEGER REFERENCES species(species_id),
    color_id INTEGER REFERENCES colors(color_id),
    PRIMARY KEY (species_id, color_id)
);

CREATE TABLE IF NOT EXISTS species_shapes (
    species_id INTEGER REFERENCES species(species_id),
    shape_id INTEGER REFERENCES shapes(shape_id),
    PRIMARY KEY (species_id, shape_id)
);

CREATE TABLE IF NOT EXISTS version_groups_generations (
    version_group_id INTEGER REFERENCES version_groups(version_group_id),
    generation_id INTEGER REFERENCES generations(generation_id),
    PRIMARY KEY (version_group_id, generation_id)
);




-- =========================
-- Smogon Tables
-- =========================
DROP TABLE IF EXISTS pokemon_usage;
CREATE TABLE IF NOT EXISTS pokemon_usage (
    pokemon_usage_id SERIAL PRIMARY KEY,
    pokemon_id INTEGER REFERENCES pokemon(pokemon_id),
    raw_count DOUBLE PRECISION,
    usage_percent DOUBLE PRECISION,
    players_used INTEGER,
    gxe_top INTEGER,
    gxe_99 INTEGER,
    gxe_95 INTEGER,
    metagame_id INTEGER,
    month DATE
);

DROP TABLE IF EXISTS battle_formats;
CREATE TABLE IF NOT EXISTS battle_formats (
    battle_format_id SERIAL PRIMARY KEY,
    full_metagame TEXT,
    name TEXT,
    cutoff INTEGER,
    UNIQUE (name, cutoff)
);

DROP TABLE IF EXISTS monthly_stats;
CREATE TABLE IF NOT EXISTS monthly_stats (
    name TEXT,
    month DATE,
    num_battles INTEGER,
    UNIQUE (name, month)
);

DROP TABLE IF EXISTS smogon_items;
CREATE TABLE IF NOT EXISTS smogon_items (
    smogon_item_id SERIAL PRIMARY KEY,
    pokemon_id INTEGER,
    item_id INTEGER,
    item_count DOUBLE PRECISION,
    month DATE,
    metagame TEXT
);

DROP TABLE IF EXISTS smogon_moves;
CREATE TABLE IF NOT EXISTS smogon_moves (
    smogon_move_id SERIAL PRIMARY KEY,
    pokemon_id INTEGER,
    move_id INTEGER,
    move_count DOUBLE PRECISION,
    move_perc DOUBLE PRECISION,
    month DATE,
    metagame TEXT
);

DROP TABLE IF EXISTS smogon_teammates;
CREATE TABLE IF NOT EXISTS smogon_teammates (
    smogon_teammate_id SERIAL PRIMARY KEY,
    pokemon_id INTEGER,
    teammate_id INTEGER,
    teammate_count DOUBLE PRECISION,
    month DATE,
    metagame TEXT
);

DROP TABLE IF EXISTS smogon_checks;
CREATE TABLE IF NOT EXISTS smogon_checks (
    smogon_check_id SERIAL PRIMARY KEY,
    pokemon_id INTEGER,
    check_id INTEGER,
    check_count DOUBLE PRECISION,
    check_perc DOUBLE PRECISION,
    check_sd DOUBLE PRECISION,
    month DATE,
    metagame TEXT
);

DROP TABLE IF EXISTS smogon_abilities;
CREATE TABLE IF NOT EXISTS smogon_abilities (
    smogon_ability_id SERIAL PRIMARY KEY,
    pokemon_id INTEGER,
    ability_id INTEGER,
    ability_count DOUBLE PRECISION,
    ability_perc DOUBLE PRECISION,
    month DATE,
    metagame TEXT
);

DROP TABLE IF EXISTS smogon_teras;
CREATE TABLE IF NOT EXISTS smogon_teras (
    smogon_tera_id SERIAL PRIMARY KEY,
    pokemon_id INTEGER,
    type_id INTEGER,
    type_count DOUBLE PRECISION,
    type_perc DOUBLE PRECISION,
    month DATE,
    metagame TEXT
);

DROP TABLE IF EXISTS smogon_natures;
CREATE TABLE IF NOT EXISTS smogon_natures (
    smogon_nature_id SERIAL PRIMARY KEY,
    pokemon_id INTEGER,
    nature_id INTEGER,
    nature_count DOUBLE PRECISION,
    nature_perc DOUBLE PRECISION,
    month DATE,
    metagame TEXT
);




DROP TABLE IF EXISTS sprites;
CREATE TABLE IF NOT EXISTS sprites (
    sprite_id INTEGER PRIMARY KEY,
    sprite_name VARCHAR(255),
    sprite_data TEXT
);


-- ITEMS
ALTER TABLE items ADD COLUMN IF NOT EXISTS normalized_name TEXT;

UPDATE items
SET normalized_name = LOWER(
    REPLACE(
        CASE
            WHEN POSITION('--' IN name) > 0 THEN SUBSTRING(name FROM 1 FOR POSITION('--' IN name) - 1)
            ELSE name
        END,
        '-', ''
    )
);

-- MOVES
ALTER TABLE moves ADD COLUMN IF NOT EXISTS normalized_name TEXT;

UPDATE moves
SET normalized_name = LOWER(
    REPLACE(
        CASE
            WHEN POSITION('--' IN name) > 0 THEN SUBSTRING(name FROM 1 FOR POSITION('--' IN name) - 1)
            ELSE name
        END,
        '-', ''
    )
);

-- ABILITIES
ALTER TABLE abilities ADD COLUMN IF NOT EXISTS normalized_name TEXT;

UPDATE abilities
SET normalized_name = LOWER(
    REPLACE(
        CASE
            WHEN POSITION('--' IN name) > 0 THEN SUBSTRING(name FROM 1 FOR POSITION('--' IN name) - 1)
            ELSE name
        END,
        '-', ''
    )
);

import type { FileNode } from './FileTree';

/** A labelled code sample inside a tile. */
export interface Snippet {
    lang: string;
    code: string;
    /** Translation key of the caption above the sample. */
    labelKey?: string;
    /** Caption that is a file name, shown as is. */
    label?: string;
}

export type GainVisual =
    | { kind: 'image'; src: string; altKey: string; pixelated?: boolean; snippets?: Snippet[] }
    | { kind: 'code'; snippets: Snippet[] }
    | { kind: 'tree'; nodes: FileNode[]; snippets: Snippet[] };

/**
 * One tile of the bento grid. `span` is its footprint at lg and above (5, 6 or 7 of 12 columns); every
 * tile collapses to a single column below md. The comparison lead tile is not in this list, since it
 * is the only one with its own layout.
 */
export interface GainTile {
    id: string;
    titleKey: string;
    bodyKey: string;
    span: 'narrow' | 'half' | 'wide';
    visual: GainVisual;
}

/** The files a datapacker touches by hand for one custom block, in the order they hit them. */
export interface HandFile {
    path: string;
    role: string;
    /** Which pack the file lands in, which is what makes the count feel like work. */
    pack: 'data' | 'assets';
}

export const BY_HAND: HandFile[] = [
    { path: 'function/place.mcfunction',         role: 'placement',       pack: 'data' },
    { path: 'function/destroy.mcfunction',       role: 'destruction',     pack: 'data' },
    { path: 'loot_table/block.json',             role: 'drops',           pack: 'data' },
    { path: 'recipe/block.json',                 role: 'vanilla recipe',  pack: 'data' },
    { path: 'function/calls/crafter.mcfunction', role: 'NBT recipe',      pack: 'data' },
    { path: 'items/block.json',                  role: 'item definition', pack: 'assets' },
    { path: 'models/item/block.json',            role: 'model',           pack: 'assets' },
    { path: 'lang/en_us.json',                   role: 'translation key', pack: 'assets' },
];

/** Textures a datapack author drops in, and the model StewBeet infers from their names. */
const TEXTURE_FILES: FileNode[] = [
    {
        name: 'assets/textures/',
        children: [
            { name: 'electric_furnace_top.png', note: 'top face' },
            { name: 'electric_furnace_side.png', note: 'sides' },
            { name: 'electric_furnace_front.png', note: 'front face' },
            { name: 'electric_furnace_front_on.png', note: 'powered state' },
        ],
    },
];

export const GAIN_TILES: GainTile[] = [
    {
        id: 'loot_tables',
        titleKey: 'gains.lootTablesTitle',
        bodyKey: 'gains.lootTablesDesc',
        span: 'narrow',
        visual: { kind: 'image', src: '/img/datapack.loot_tables.give_all.jpg', altKey: 'gains.lootTablesImageAlt' },
    },
    {
        id: 'materials',
        titleKey: 'gains.materialsTitle',
        bodyKey: 'gains.materialsDesc',
        span: 'wide',
        visual: {
            kind: 'image',
            src: '/img/material_tier.png',
            altKey: 'gains.materialsImageAlt',
            pixelated: true,
            snippets: [{
                lang: 'python',
                labelKey: 'gains.materialsSnippetLabel',
                code: `ORES_CONFIGS: dict[str, EquipmentsConfig | None] = {
    "solarium_ingot": EquipmentsConfig(
        # Solarium behaves like diamond,
        equivalent_to=DefaultOre.DIAMOND,
        # but the pickaxe lasts three times longer
        pickaxe_durability=3 * DIAMOND_PICKAXE["durability"],
        attributes={"attack_damage": 1, "armor": 0.5},
    ),
}
generate_everything_about_these_materials(ORES_CONFIGS)`,
            }],
        },
    },
    {
        id: 'item_models',
        titleKey: 'gains.itemModelsTitle',
        bodyKey: 'gains.itemModelsDesc',
        span: 'wide',
        visual: {
            kind: 'tree',
            nodes: TEXTURE_FILES,
            snippets: [{
                lang: 'json',
                labelKey: 'gains.itemModelsOnLabel',
                code: `{
  "parent": "block/orientable",
  "textures": {
    "front": "simplenergy:item/electric_furnace_front_on",
    "side": "simplenergy:item/electric_furnace_side",
    "top": "simplenergy:item/electric_furnace_top"
  }
}`,
            }],
        },
    },
    {
        id: 'dependencies',
        titleKey: 'gains.dependenciesTitle',
        bodyKey: 'gains.dependenciesDesc',
        span: 'narrow',
        visual: { kind: 'image', src: '/img/finalyze.dependencies.ingame_errors.jpg', altKey: 'gains.dependenciesImageAlt', pixelated: true },
    },
    {
        id: 'recipes',
        titleKey: 'gains.recipesTitle',
        bodyKey: 'gains.recipesDesc',
        span: 'half',
        visual: {
            kind: 'code',
            snippets: [{
                lang: 'mcfunction',
                label: 'calls/smithed_crafter/shapeless_recipes.mcfunction',
                code: `# The backslashes are ours so it fits: the real file is one line per recipe.
execute \\
  if score @s smithed.data matches 0 \\
  store result score @s smithed.data \\
  if score count smithed.data matches 2 \\
  if data storage smithed.crafter:input {"recipe": [ \\
    {"id": "minecraft:iron_ingot", "count": 1}, \\
    {"components": {"minecraft:custom_data": \\
      {"stardust": {"stardust_fragment": true}}}, "count": 8} \\
  ]} \\
  run function stardust:calls/smithed_crafter/apply_recipe \\
  {"command":"loot replace block ~ ~ ~ container.16 loot
   stardust:i/stardust_ingot"}`,
            }],
        },
    },
    {
        id: 'lang',
        titleKey: 'gains.langTitle',
        bodyKey: 'gains.langDesc',
        span: 'half',
        visual: {
            kind: 'code',
            snippets: [
                {
                    lang: 'mcfunction',
                    labelKey: 'gains.langBeforeLabel',
                    code: `tellraw @s [{text:"Entities: ",color:"gray"}, \\
    {score:{name:"#entities",objective:"simplenergy.data"},color:"gold"}]`,
                },
                {
                    lang: 'mcfunction',
                    labelKey: 'gains.langAfterLabel',
                    code: `tellraw @s [{"translate":"simplenergy.entities",color:"gray"}, \\
    {score:{name:"#entities",objective:"simplenergy.data"},color:"gold"}]`,
                },
                {
                    lang: 'json',
                    labelKey: 'gains.langFileLabel',
                    code: `{
  "simplenergy.entities": "Entities: ",
  "simplenergy.electric_furnace": "Electric Furnace"
}`,
                },
            ],
        },
    },
];

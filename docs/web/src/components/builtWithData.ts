/**
 * Projects that compile with the framework, in the order of the Showcase strip: other people's
 * first, then the maintainer's packs, then the maintainer's libraries. Most of the list is the
 * maintainer's work, so the community projects lead and carry their own mark. The counts of
 * the two packs with `stats` are measured: outputs from their build directories, source lines
 * from tokenising every .py file and dropping comments, docstrings and blank lines.
 */

export interface Entry {
    name: string;
    owner: string;
    url: string;
}

export interface ShowcaseProject extends Entry {
    /** Its pack.png under public/showcase/, absent for a project with none. */
    icon?: string;
    /** Written by someone other than StewBeet's author. */
    community?: boolean;
    stats?: { sourceLines: number; functions: number; jsonFiles: number; textures: number };
}

export const SHOWCASE: ShowcaseProject[] = [
    { name: 'Switch', owner: 'Paralya', url: 'https://github.com/Paralya/Switch', community: true },
    { name: 'Headconomics', owner: 'RacoonJohn', url: 'https://github.com/RacoonJohn/Headconomics', icon: 'headconomics', community: true },
    { name: 'Crazy Adventure', owner: 'VGreluchon', url: 'https://github.com/VGreluchon/Crazy-Adventure-Datapack', icon: 'crazy_adventure', community: true },
    { name: 'Lucky Pillar', owner: 'YuWan886', url: 'https://github.com/YuWan886/Lucky-Pillar', icon: 'lucky_pillar', community: true },
    { name: 'Elemental Wands', owner: 'PlanetMinecraft', url: 'https://www.planetminecraft.com/data-pack/elemental-wands/', community: true },
    {
        name: 'Stardust Fragment', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/StardustFragment', icon: 'stardust_fragment',
        stats: { sourceLines: 5738, functions: 774, jsonFiles: 1331, textures: 971 },
    },
    {
        name: 'SimplEnergy', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SimplEnergy', icon: 'simplenergy',
        stats: { sourceLines: 1422, functions: 270, jsonFiles: 805, textures: 434 },
    },
    { name: 'MC Guns System', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/MC_Guns_System', icon: 'mc_guns_system' },
    { name: 'LifeSteal', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/LifeSteal', icon: 'lifesteal' },
    { name: 'Imagine Your Craft', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/ImagineYourCraftDatapack' },
    { name: 'Survisland', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/Survisland', icon: 'survisland' },
    { name: 'Cauldron Concrete Powder', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/CauldronConcretePowder', icon: 'cauldron_concrete_powder' },
    { name: 'More Apples', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/MoreApples', icon: 'more_apples' },
    { name: 'Random Mob Sizes', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/RandomMobSizes', icon: 'random_mob_sizes' },
    { name: 'Smithed Summit 2026', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmithedSummit2026' },
    { name: 'Smithed Summit 2024', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmithedSummit2024' },
    { name: 'Smithed Direct', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmithedDirect', icon: 'smithed_direct' },
    { name: 'Smart Ore Generation', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmartOreGeneration', icon: 'smart_ore_generation' },
    { name: 'Furnace NBT Recipes', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/FurnaceNbtRecipes', icon: 'furnace_nbt_recipes' },
    { name: 'Common Signals', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/CommonSignals', icon: 'common_signals' },
    { name: 'Realistic Explosion', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/RealisticExplosion', icon: 'realistic_explosion' },
    { name: 'Shopping Kart', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/ShoppingKart', icon: 'shopping_kart' },
    { name: 'Sheep Wars', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SheepWars', icon: 'sheep_wars' },
    { name: 'Golf Ball', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/GolfBall', icon: 'golf_ball' },
];

/** Everything with public source that compiles with the framework, for the trust strip. */
export const TOTAL_BUILT_WITH: number = SHOWCASE.length;

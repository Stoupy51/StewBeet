/**
 * Projects that compile with the framework, split by who wrote them.
 *
 * The split is deliberate. Most of this list is the maintainer's own work, and a page that
 * presents all of it as undifferentiated adoption invites a visitor to check two links and
 * conclude the whole list is self-referential. Naming the third-party projects first, and
 * labelling the rest as the maintainer's, is both honest and the stronger claim: the
 * maintainer's packs are what proves the framework holds up at size, and the counts below
 * are measured rather than estimated: outputs from their build directories, source lines
 * from tokenising every .py file and dropping comments, docstrings and blank lines.
 */

export interface Entry {
    name: string;
    owner: string;
    url: string;
}

/** A project shown as a card, with the build output it produces. */
export interface Flagship extends Entry {
    /** Where players get it. `url` stays on the repository, for reading the source. */
    modrinth: string;
    /** Statements only: comments, docstrings and blank lines are excluded from the count. */
    sourceLines: number;
    image: string;
    functions: number;
    jsonFiles: number;
    textures: number;
    descriptionKey: string;
}

/** Written and maintained by people other than the framework's author. */
export const COMMUNITY_PROJECTS: Entry[] = [
    { name: 'Switch',          owner: 'Paralya',         url: 'https://github.com/Paralya/Switch' },
    { name: 'Crazy Adventure', owner: 'VGreluchon',      url: 'https://github.com/VGreluchon/Crazy-Adventure-Datapack' },
    { name: 'Lucky Pillar',    owner: 'YuWan886',        url: 'https://github.com/YuWan886/Lucky-Pillar' },
    { name: 'Elemental Wands', owner: 'PlanetMinecraft', url: 'https://www.planetminecraft.com/data-pack/elemental-wands/' },
];

/**
 * The two packs the framework is developed against, with counts taken from their build
 * directories. They are the answer to "does this scale past a toy example?".
 */
export const FLAGSHIPS: Flagship[] = [
    {
        name: 'Stardust Fragment',
        owner: 'Stoupy51',
        url: 'https://github.com/Stoupy51/StardustFragment',
        modrinth: 'https://modrinth.com/datapack/stardust-fragment',
        image: '/img/stardustfragment_items.png',
        sourceLines: 5738,
        functions: 774,
        jsonFiles: 1331,
        textures: 971,
        descriptionKey: 'builtWith.stardustDesc',
    },
    {
        name: 'SimplEnergy',
        owner: 'Stoupy51',
        url: 'https://github.com/Stoupy51/SimplEnergy',
        modrinth: 'https://modrinth.com/datapack/simplenergy',
        image: '/img/simplenergy_items.png',
        sourceLines: 1422,
        functions: 270,
        jsonFiles: 805,
        textures: 434,
        descriptionKey: 'builtWith.simplenergyDesc',
    },
];

/** The maintainer's remaining packs, listed without individual cards. */
export const MAINTAINER_PROJECTS: Entry[] = [
    { name: 'MC Guns System',           owner: 'Stoupy51', url: 'https://github.com/Stoupy51/MC_Guns_System' },
    { name: 'LifeSteal',                owner: 'Stoupy51', url: 'https://github.com/Stoupy51/LifeSteal' },
    { name: 'Imagine Your Craft',       owner: 'Stoupy51', url: 'https://github.com/Stoupy51/ImagineYourCraftDatapack' },
    { name: 'Survisland',               owner: 'Stoupy51', url: 'https://github.com/Stoupy51/Survisland' },
    { name: 'Cauldron Concrete Powder', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/CauldronConcretePowder' },
    { name: 'More Apples',              owner: 'Stoupy51', url: 'https://github.com/Stoupy51/MoreApples' },
    { name: 'Random Mob Sizes',         owner: 'Stoupy51', url: 'https://github.com/Stoupy51/RandomMobSizes' },
    { name: 'Smithed Summit 2026',      owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmithedSummit2026' },
    { name: 'Smithed Summit 2024',      owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmithedSummit2024' },
    { name: 'Smithed Direct',           owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmithedDirect' },
];

/** Libraries and tools that are themselves built with the framework. */
export const LIBRARIES: Entry[] = [
    { name: 'Smart Ore Generation', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmartOreGeneration' },
    { name: 'Furnace NBT Recipes',  owner: 'Stoupy51', url: 'https://github.com/Stoupy51/FurnaceNbtRecipes' },
    { name: 'Common Signals',       owner: 'Stoupy51', url: 'https://github.com/Stoupy51/CommonSignals' },
    { name: 'Realistic Explosion',  owner: 'Stoupy51', url: 'https://github.com/Stoupy51/RealisticExplosion' },
    { name: 'Shopping Kart',        owner: 'Stoupy51', url: 'https://github.com/Stoupy51/ShoppingKart' },
    { name: 'Sheep Wars',           owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SheepWars' },
    { name: 'Golf Ball',            owner: 'Stoupy51', url: 'https://github.com/Stoupy51/GolfBall' },
];

/** Third-party libraries StewBeet detects in your code and wires into the build. */
export const INTEGRATIONS: Entry[] = [
    { name: 'Smithed Custom Blocks', owner: 'smithed.dev', url: 'https://wiki.smithed.dev/libraries/custom-block/' },
    { name: 'Smithed Crafter',       owner: 'smithed.dev', url: 'https://wiki.smithed.dev/libraries/crafter/' },
    { name: 'Smithed Weld',          owner: 'smithed.dev', url: 'https://weld.smithed.dev/' },
    { name: 'Bookshelf',             owner: 'mcbookshelf', url: 'https://github.com/mcbookshelf/bookshelf' },
    { name: 'ItemIO',                owner: 'edayot',      url: 'https://github.com/edayot/ItemIO' },
    { name: 'LanternLoad',           owner: 'LanternMC',   url: 'https://github.com/LanternMC/load' },
    { name: 'NeoEnchant',            owner: 'Modrinth',    url: 'https://modrinth.com/datapack/neoenchant' },
    { name: 'SimpleDrawer',          owner: 'edayot',      url: 'https://edayot.github.io/SimpleDrawer/material.html' },
];

/** Everything with public source that compiles with the framework, for the trust strip. */
export const TOTAL_BUILT_WITH: number =
    COMMUNITY_PROJECTS.length + FLAGSHIPS.length + MAINTAINER_PROJECTS.length + LIBRARIES.length;

/**
 * The upstream projects StewBeet is built on.
 *
 * This is the other half of the story builtWithData.ts tells. That file is downstream, the
 * packs people ship with the framework; this one is upstream, the tools the framework would
 * not exist without. Keeping them in separate modules keeps the two sections from drifting
 * into one undifferentiated list of names.
 *
 * `AUTO_LIBRARIES` mirrors OFFICIAL_LIBS in python_package/stewbeet/dependencies/official_libs.py.
 * When a library is added there, add it here too: the site is what tells people it exists.
 */
import type { Entry } from './builtWithData';

/** One outbound destination on a card. Several projects are documented in more than one place. */
export interface GiantLink {
    label: string;
    url: string;
}

/** A project the framework stands on, credited with a card of its own. */
export interface Giant {
    name: string;
    /** Who maintains it, shown beside the name. */
    owner: string;
    /** Where the card points. The first entry is the card's own anchor. */
    links: GiantLink[];
    /** One line, in the `giants` group: what this project does for the framework. */
    roleKey: string;
    /** The longer paragraph, in the `credits` group, shown on /credits only. */
    bodyKey: string;
}

/** Credited in the order a build meets them: the pipeline, the compiler, the renderer, the ecosystem. */
export const GIANTS: Giant[] = [
    {
        name: 'beet',
        owner: 'mcbeet',
        links: [{ label: 'github.com/mcbeet/beet', url: 'https://github.com/mcbeet/beet' }],
        roleKey: 'giants.beetRole',
        bodyKey: 'credits.beetBody',
    },
    {
        name: 'mecha + bolt',
        owner: 'mcbeet',
        links: [
            { label: 'mecha', url: 'https://github.com/mcbeet/beet/blob/main/packages/mecha/README.md' },
            { label: 'bolt', url: 'https://github.com/mcbeet/beet/blob/main/packages/bolt/README.md' },
        ],
        roleKey: 'giants.mechaRole',
        bodyKey: 'credits.mechaBody',
    },
    {
        name: 'Model Resolver',
        owner: 'edayot (airdox)',
        links: [{ label: 'github.com/edayot/model_resolver', url: 'https://github.com/edayot/model_resolver' }],
        roleKey: 'giants.modelResolverRole',
        bodyKey: 'credits.modelResolverBody',
    },
    {
        name: 'The Smithed ecosystem',
        owner: 'smithed.dev',
        links: [
            { label: 'docs.smithed.dev', url: 'https://docs.smithed.dev/' },
            { label: 'Smithed Weld', url: 'https://weld.smithed.dev/' },
        ],
        roleKey: 'giants.smithedRole',
        bodyKey: 'credits.smithedBody',
    },
    {
        name: 'Bookshelf',
        owner: 'mcbookshelf',
        links: [{ label: 'github.com/mcbookshelf/bookshelf', url: 'https://github.com/mcbookshelf/bookshelf' }],
        roleKey: 'giants.bookshelfRole',
        bodyKey: 'credits.bookshelfBody',
    },
];

/**
 * Libraries the build detects in your functions and downloads for you.
 * Names and urls come from OFFICIAL_LIBS; Lantern Load is added because every generated
 * pack loads through it even though it is not a detected dependency.
 */
export const AUTO_LIBRARIES: Entry[] = [
    { name: 'Smithed Custom Block', owner: 'smithed.dev', url: 'https://wiki.smithed.dev/libraries/custom-block/' },
    { name: 'Smithed Crafter',      owner: 'smithed.dev', url: 'https://wiki.smithed.dev/libraries/crafter/' },
    { name: 'Smithed Actionbar',    owner: 'smithed.dev', url: 'https://wiki.smithed.dev/libraries/actionbar/' },
    { name: 'Player Motion API',    owner: 'MulverineX',  url: 'https://github.com/MulverineX/player_motion' },
    { name: 'ItemIO',               owner: 'edayot',      url: 'https://github.com/edayot/ItemIO' },
    { name: 'Realistic Explosion',  owner: 'Stoupy51',    url: 'https://github.com/Stoupy51/RealisticExplosion' },
    { name: 'Common Signals',       owner: 'Stoupy51',    url: 'https://github.com/Stoupy51/CommonSignals' },
    { name: 'Furnace NBT Recipes',  owner: 'Stoupy51',    url: 'https://github.com/Stoupy51/FurnaceNbtRecipes' },
    { name: 'Smart Ore Generation', owner: 'Stoupy51',    url: 'https://github.com/Stoupy51/SmartOreGeneration' },
    { name: 'Bookshelf modules',    owner: 'mcbookshelf', url: 'https://github.com/mcbookshelf/bookshelf' },
    { name: 'Lantern Load',         owner: 'LanternMC',   url: 'https://github.com/LanternMC/load' },
];

/**
 * Packs StewBeet knows how to cooperate with, through a plugin rather than a dependency.
 * Nothing is downloaded for these: the build only emits the extra files they look for.
 */
export const COMPATIBILITIES: Entry[] = [
    { name: 'NeoEnchant',   owner: 'Modrinth', url: 'https://modrinth.com/datapack/neoenchant' },
    { name: 'SimpleDrawer', owner: 'edayot',   url: 'https://edayot.github.io/SimpleDrawer/material.html' },
];

/** How many `bs.*` modules the build can resolve by name, from OFFICIAL_LIBS. */
export const BOOKSHELF_MODULE_COUNT: number = 24;

/** Where the dependencies guide lives, per language. */
export const DEPENDENCIES_DOC: Record<'en' | 'fr', string> = {
    en: '5_dependencies/en.md',
    fr: '5_dependencies/fr.md',
};

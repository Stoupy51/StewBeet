/**
 * Projects that compile with the framework, in the order of the Showcase: other people's first,
 * then the maintainer's packs, then the maintainer's libraries. Most of the list is the
 * maintainer's work, so the community projects lead and carry their own mark. The counts of
 * the two packs with `stats` are measured: outputs from their build directories, source lines
 * from tokenising every .py file and dropping comments, docstrings and blank lines. Summaries
 * come from each project's README or GitHub description.
 */
import type { Language } from '../context/LanguageContext';

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
    /** A library other packs call. */
    library?: boolean;
    summary?: Record<Language, string>;
    /** The author's own words about building it, with their consent. */
    quote?: Record<Language, string>;
    stats?: { sourceLines: number; functions: number; jsonFiles: number; textures: number };
}

export const SHOWCASE: ShowcaseProject[] = [
    {
        name: 'Switch', owner: 'Paralya', url: 'https://github.com/Paralya/Switch', community: true,
        summary: { en: "The datapack running Paralya's Switch minigame server.", fr: 'Le datapack du serveur de mini-jeux Switch de Paralya.' },
    },
    {
        name: 'Headconomics', owner: 'RacoonJohn', url: 'https://github.com/RacoonJohn/Headconomics', icon: 'headconomics', community: true,
        summary: { en: 'Turns player heads into an economy, with a digital wallet and transfer vouchers.', fr: 'Fait des têtes de joueurs une économie, avec un portefeuille et des bons de transfert.' },
        quote: { en: 'Programming Headconomics took me about one evening, thanks to StewBeet.', fr: "La programmation de Headconomics m'a pris une soirée, grâce à StewBeet." },
    },
    {
        name: 'Crazy Adventure', owner: 'VGreluchon', url: 'https://github.com/VGreluchon/Crazy-Adventure-Datapack', icon: 'crazy_adventure', community: true,
        summary: { en: 'An adventure and technology datapack built on SimplEnergy.', fr: 'Un datapack aventure et technologie construit sur SimplEnergy.' },
    },
    {
        name: 'Lucky Pillar', owner: 'YuWan886', url: 'https://github.com/YuWan886/Lucky-Pillar', icon: 'lucky_pillar', community: true,
        summary: { en: 'A multiplayer game on towering pillars, with random items and random events.', fr: 'Un jeu multijoueur sur des piliers, avec des items et des événements aléatoires.' },
    },
    { name: 'Elemental Wands', owner: 'PlanetMinecraft', url: 'https://www.planetminecraft.com/data-pack/elemental-wands/', community: true },
    {
        name: 'Stardust Fragment', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/StardustFragment', icon: 'stardust_fragment',
        summary: { en: 'An adventure and technology datapack, the largest project built with StewBeet.', fr: 'Un datapack aventure et technologie, le plus gros projet fait avec StewBeet.' },
        stats: { sourceLines: 5738, functions: 774, jsonFiles: 1331, textures: 971 },
    },
    {
        name: 'SimplEnergy', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SimplEnergy', icon: 'simplenergy',
        summary: { en: 'Energy, machines and cables for survival, and a base for other energy packs.', fr: "De l'énergie, des machines et des câbles en survie, et une base pour d'autres packs d'énergie." },
        stats: { sourceLines: 1422, functions: 270, jsonFiles: 805, textures: 434 },
    },
    {
        name: 'MC Guns System', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/MC_Guns_System', icon: 'mc_guns_system',
        summary: { en: 'Guns, Call of Duty style game modes and a Zombies mode, with no mods.', fr: 'Des armes, des modes de jeu façon Call of Duty et un mode Zombies, sans mods.' },
    },
    {
        name: 'LifeSteal', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/LifeSteal', icon: 'lifesteal',
        summary: { en: 'Life steal from the Lifesteal SMP, with hearts to eat and a beacon to revive players.', fr: 'Le vol de vie du Lifesteal SMP, avec des cœurs à manger et une balise pour ressusciter.' },
    },
    {
        name: 'Imagine Your Craft', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/ImagineYourCraftDatapack',
        summary: { en: 'The ImagineYourCraft mod, rebuilt as a datapack.', fr: 'Le mod ImagineYourCraft, refait en datapack.' },
    },
    {
        name: 'Survisland', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/Survisland', icon: 'survisland',
        summary: { en: 'The packs of the Survisland server: custom items, their textures, sounds and game modes.', fr: 'Les packs du serveur Survisland : items custom, textures, sons et modes de jeu.' },
    },
    {
        name: 'Cauldron Concrete Powder', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/CauldronConcretePowder', icon: 'cauldron_concrete_powder',
        summary: { en: 'Drop concrete powder in a water cauldron to turn it into concrete.', fr: "Jetez de la poudre de béton dans un chaudron d'eau pour en faire du béton." },
    },
    {
        name: 'More Apples', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/MoreApples', icon: 'more_apples',
        summary: { en: 'Every kind of leaves drops apples, twice as many as vanilla oak leaves.', fr: 'Toutes les feuilles donnent des pommes, deux fois plus que le chêne vanilla.' },
    },
    {
        name: 'Random Mob Sizes', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/RandomMobSizes', icon: 'random_mob_sizes',
        summary: { en: 'Each mob gets a random scale between a minimum and a maximum.', fr: 'Chaque mob reçoit une taille aléatoire entre un minimum et un maximum.' },
    },
    {
        name: 'Smithed Summit 2026', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmithedSummit2026',
        summary: { en: 'Made for the Smithed Summit 2026.', fr: 'Fait pour le Smithed Summit 2026.' },
    },
    {
        name: 'Smithed Summit 2024', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmithedSummit',
        summary: { en: 'Made for the Smithed Summit 2024.', fr: 'Fait pour le Smithed Summit 2024.' },
    },
    {
        name: 'Smithed Direct', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmithedDirect', icon: 'smithed_direct',
        summary: { en: 'The datapack shown in the Smithed Direct 2025 video.', fr: 'Le datapack montré dans la vidéo du Smithed Direct 2025.' },
    },
    {
        name: 'Shopping Kart', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/ShoppingKart', icon: 'shopping_kart',
        summary: { en: 'A kart, its controls and its physics.', fr: 'Un kart, ses contrôles et sa physique.' },
    },
    {
        name: 'Sheep Wars', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SheepWars', icon: 'sheep_wars',
        summary: { en: 'The sheep of the SheepWars minigame.', fr: 'Les moutons du mini-jeu SheepWars.' },
    },
    {
        name: 'Golf Ball', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/GolfBall', icon: 'golf_ball',
        summary: { en: 'A golf ball, its controls and its physics.', fr: 'Une balle de golf, ses contrôles et sa physique.' },
    },
    {
        name: 'Smart Ore Generation', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/SmartOreGeneration', icon: 'smart_ore_generation', library: true,
        summary: { en: 'Generates custom ores in the world.', fr: 'Génère des minerais custom dans le monde.' },
    },
    {
        name: 'Furnace NBT Recipes', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/FurnaceNbtRecipes', icon: 'furnace_nbt_recipes', library: true,
        summary: { en: 'Furnace recipes whose ingredients and results carry components.', fr: 'Des recettes de four dont les ingrédients et résultats portent des components.' },
    },
    {
        name: 'Common Signals', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/CommonSignals', icon: 'common_signals', library: true,
        summary: { en: 'Selectors shared between packs, so each pack does not run them on its own.', fr: 'Des sélecteurs partagés entre packs, pour que chacun ne les lance pas de son côté.' },
    },
    {
        name: 'Realistic Explosion', owner: 'Stoupy51', url: 'https://github.com/Stoupy51/RealisticExplosion', icon: 'realistic_explosion', library: true,
        summary: { en: 'Realistic explosions any pack can trigger.', fr: "Des explosions réalistes que n'importe quel pack peut déclencher." },
    },
];

/** Everything with public source that compiles with the framework, for the trust strip. */
export const TOTAL_BUILT_WITH: number = SHOWCASE.length;

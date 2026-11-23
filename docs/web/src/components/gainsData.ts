/** The files a datapacker writes by hand for one custom block, in the order they hit them. */
export const BY_HAND: { path: string; role: string }[] = [
    { path: 'function/place.mcfunction', role: 'placement' },
    { path: 'function/destroy.mcfunction', role: 'destruction' },
    { path: 'loot_table/block.json', role: 'drops' },
    { path: 'recipe/block.json', role: 'vanilla recipe' },
    { path: 'function/calls/crafter.mcfunction', role: 'NBT recipe' },
    { path: 'items/block.json', role: 'item definition' },
    { path: 'models/item/block.json', role: 'model' },
    { path: 'lang/en_us.json', role: 'translation key' },
];

/**
 * The code of the two examples under the comparison, highlighted at build time by
 * scripts/highlight-docs.ts into src/generated/gainsCode.json under the same keys.
 * Both are what Stardust Fragment and SimplEnergy write and build, cut to fit a phone.
 */
export const GAIN_SNIPPETS: Record<string, { lang: string; code: string }> = {
    materials: {
        lang: 'python',
        code: `generate_everything_about_these_materials({
  "solarium_ingot": EquipmentsConfig(
    DefaultOre.NETHERITE,
    attributes={
      "attack_damage": 15,
      "armor": 6.0,
    },
  ),
})`,
    },
    langBefore: {
        lang: 'mcfunction',
        code: 'tellraw @s {"text":"Energy stored: "}',
    },
    langAfter: {
        lang: 'mcfunction',
        code: 'tellraw @s {"translate":"simplenergy.energy_stored","fallback":"Energy stored: "}',
    },
    langFile: {
        lang: 'json',
        code: `{
  "simplenergy.energy_stored": "Energy stored: "
}`,
    },
};

// Fictional TypeScript datapack DSL. See ../../README.md.
import {aura} from 'sniffer-example-runtime';

/** Run once on every entity the pack spawns. */
export function onSpawn(): void {
    aura();
    aura.tick('ns.spawned');
}

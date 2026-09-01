// Fictional TypeScript datapack DSL. See ../../../README.md.
import {aura, damage, effect, say} from 'sniffer-example-runtime';

/** Everything a hit does to the entity it landed on. */
export function hit(): void {
    say('hit!');
    damage(4);
    effect('slowness', 3);
    aura();
}
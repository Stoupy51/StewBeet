/**
 * "Who makes what" diagram: beet at the base, bolt and mecha beside it inside the mcbeet team's
 * frame, StewBeet outside the frame on top.
 *
 * Written as an SVG string so one source serves both the home page, where it takes the site's
 * colours, and the shareable files scripts/build-stack-diagram.ts writes to public/img/stack/.
 * Text is laid out by hand: SVG does not wrap, so every line break below is a real one.
 */
import type { Language } from '../context/LanguageContext';

export interface StackPalette {
    background: string;
    panel: string;
    border: string;
    strong: string;
    body: string;
    muted: string;
    /** StewBeet's colour. */
    stewbeet: string;
    stewbeetTint: string;
    /** The mcbeet team's colour, shared by beet, bolt and mecha. */
    team: string;
    teamTint: string;
}

/** Channel values mirror THEMED in tailwind.config.js, which the files cannot read at runtime. */
export const STACK_PALETTES = {
    dark: {
        background: '#141518', panel: '#0c0d0f', border: '#383b42',
        strong: '#f2f3f5', body: '#b8bcc4', muted: '#a3a7b0',
        stewbeet: '#2e9bff', stewbeetTint: 'rgba(46, 155, 255, 0.08)',
        team: '#7fd35b', teamTint: 'rgba(127, 211, 91, 0.06)',
    },
    light: {
        background: '#f7f7f8', panel: '#ffffff', border: '#d0d2d7',
        strong: '#111214', body: '#3d4047', muted: '#565964',
        stewbeet: '#0a6fd6', stewbeetTint: 'rgba(10, 111, 214, 0.08)',
        team: '#2b7a19', teamTint: 'rgba(43, 122, 25, 0.06)',
    },
} as const satisfies Record<string, StackPalette>;

/** Lines of text; a span between backticks is set in monospace. */
type Lines = string[];

interface StackText {
    title: string;
    subtitle: string;
    stewbeet: Lines;
    stewbeetTag: string;
    plugsInto: string;
    team: string;
    bolt: Lines;
    mecha: Lines;
    beet: Lines;
    output: string;
    factsTitle: string;
    facts: [Lines, Lines, Lines];
}

export const STACK_TEXT: Record<Language, StackText> = {
    en: {
        title: 'beet, bolt, mecha and StewBeet',
        subtitle: 'Who does what when you build a Minecraft pack',
        stewbeet: ['A framework made of beet plugins. Declare an item in Python', 'and get its models, recipes, loot tables and manual page.'],
        stewbeetTag: 'independent project',
        plugsInto: 'runs inside beet, as plugins',
        team: 'mcbeet, the beet team',
        bolt: ['Python-like syntax (loops,', 'variables) inside functions'],
        mecha: ['Parses, checks and compiles', 'every command you write'],
        beet: ['The build tool: runs the plugins in order and writes', 'the datapack and the resource pack.'],
        output: 'datapack + resource pack, ready for Minecraft',
        factsTitle: 'IN SHORT',
        facts: [
            ['beet runs the build.', 'Everything else plugs into it.'],
            ['bolt and mecha are made by', 'the beet team. StewBeet is a', 'separate project by Stoupy.'],
            ['`pip install stewbeet` brings', 'beet, bolt and mecha along.'],
        ],
    },
    fr: {
        title: 'beet, bolt, mecha et StewBeet',
        subtitle: 'Qui fait quoi quand vous construisez un pack Minecraft',
        stewbeet: ['Un framework fait de plugins beet. Déclarez un item en Python', 'et obtenez ses modèles, recettes, loot tables et page de manuel.'],
        stewbeetTag: 'projet indépendant',
        plugsInto: 'tourne dans beet, sous forme de plugins',
        team: "mcbeet, l'équipe de beet",
        bolt: ['Une syntaxe proche de Python', 'dans vos fonctions'],
        mecha: ['Analyse, vérifie et compile', 'chaque commande écrite'],
        beet: ["L'outil de build : lance les plugins dans l'ordre et écrit", 'le datapack et le resource pack.'],
        output: 'datapack + resource pack, prêts pour Minecraft',
        factsTitle: 'EN BREF',
        facts: [
            ['beet lance le build.', "Tout le reste s'y branche."],
            ["bolt et mecha sont faits par", "l'équipe de beet. StewBeet est", 'un projet à part, par Stoupy.'],
            ['`pip install stewbeet` installe', 'aussi beet, bolt et mecha.'],
        ],
    },
};

export const STACK_SIZE = { width: 1200, height: 630 } as const;

const SANS = "'Archivo Variable', Archivo, ui-sans-serif, system-ui, sans-serif";
const MONO = "'JetBrains Mono Variable', ui-monospace, Consolas, monospace";

const escapeXml = (text: string) => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/** Odd segments of a backtick split are the code spans. */
const inline = (line: string) => line.split('`')
    .map((part, index) => index % 2 ? `<tspan font-family="${MONO}" font-size="0.9em">${escapeXml(part)}</tspan>` : escapeXml(part))
    .join('');

const textBlock = (lines: Lines, x: number, y: number, lineHeight: number, attributes: string) =>
    `<text x="${x}" y="${y}" ${attributes}>${lines.map((line, index) =>
        `<tspan x="${x}" dy="${index ? lineHeight : 0}">${inline(line)}</tspan>`).join('')}</text>`;

/** A group that rises into place `delay` seconds after the animation starts. */
const step = (delay: number, content: string, motion = 'stk-rise') =>
    `<g class="stk-a ${motion}" style="--d:${delay}s">${content}</g>`;

/** A label on a pill, sized from an estimate of the text width. */
const pill = (x: number, y: number, label: string, color: string, fill: string, fontSize: number) => {
    const width = Math.round(label.length * fontSize * 0.52 + 24);
    return `<rect x="${x}" y="${y - 13}" width="${width}" height="26" fill="${fill}" stroke="${color}" stroke-width="1.25"/>`
        + `<text x="${x + width / 2}" y="${y + 5}" text-anchor="middle" font-size="${fontSize}" font-weight="600" fill="${color}">${escapeXml(label)}</text>`;
};

const box = (x: number, y: number, width: number, height: number, name: string, lines: Lines, color: string, tint: string, p: StackPalette) =>
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" fill="${p.panel}"/>`
    + `<rect x="${x}" y="${y}" width="${width}" height="${height}" fill="${tint}" stroke="${color}" stroke-width="1.5"/>`
    + `<text x="${x + 24}" y="${y + 38}" font-size="24" font-weight="650" fill="${p.strong}">${escapeXml(name)}</text>`
    + textBlock(lines, x + 24, y + 66, 22, `font-size="16" fill="${p.body}"`);

/**
 * The animation runs once the root, or an ancestor on the page, carries `data-play`.
 * An ancestor with `data-armed` hides the pieces until then, so a page can wait for the reader to scroll there.
 */
const STYLE = `
.stk text { font-family: ${SANS}; }
@keyframes stk-rise { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: none; } }
@keyframes stk-drop { from { opacity: 0; transform: translateY(-28px); } to { opacity: 1; transform: none; } }
@keyframes stk-fade { from { opacity: 0; } to { opacity: 1; } }
[data-armed]:not([data-play]) .stk-a { opacity: 0; }
[data-play] .stk-a { animation: stk-rise 600ms cubic-bezier(0.2, 0.8, 0.2, 1) var(--d) both; }
[data-play] .stk-drop { animation-name: stk-drop; animation-duration: 700ms; }
[data-play] .stk-fade { animation-name: stk-fade; }
.stk-spark, .stk-flow { display: none; }
[data-play] .stk-spark { display: inline; filter: drop-shadow(0 0 4px currentColor); animation: stk-current 3.2s linear 3.6s infinite, stk-fade 600ms ease-out 3.6s both; }
[data-play] .stk-flow { display: inline; animation: stk-flow 0.8s linear 3.6s infinite, stk-fade 600ms ease-out 3.6s both; }
@keyframes stk-current { from { stroke-dashoffset: 100; } to { stroke-dashoffset: 0; } }
@keyframes stk-flow { from { stroke-dashoffset: 12; } to { stroke-dashoffset: 0; } }
@media (prefers-reduced-motion: reduce) { [data-play] .stk-a { animation: none; } [data-armed]:not([data-play]) .stk-a { opacity: 1; } [data-play] .stk-spark, [data-play] .stk-flow { animation: none; display: none; } }
`;

export interface StackDiagramOptions {
    language: Language;
    palette: StackPalette;
    /** Plays the build-up on load, as the shareable files do. Off, the diagram shows finished. */
    autoplay: boolean;
    /** @font-face rules to embed, so a file shared on its own keeps the site's typeface. */
    fontFaceCss?: string;
}

export function stackDiagramSvg({ language, palette: p, autoplay, fontFaceCss = '' }: StackDiagramOptions): string {
    const text = STACK_TEXT[language];
    const { width, height } = STACK_SIZE;
    const facts = text.facts.map((lines, index) => {
        const y = 222 + index * 118;
        const color = index === 1 ? p.stewbeet : p.team;
        return step(2.3 + index * 0.25,
            `<rect x="812" y="${y - 17}" width="3" height="${lines.length * 24 - 4}" fill="${color}"/>`
            + textBlock(lines, 832, y, 24, `font-size="17" fill="${p.strong}"`));
    }).join('');

    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" class="stk" role="img" aria-labelledby="stk-title stk-desc"${autoplay ? ' data-play=""' : ''}>
<title id="stk-title">${escapeXml(text.title)}</title>
<desc id="stk-desc">${escapeXml(text.facts.map((lines) => lines.join(' ').replace(/`/g, '')).join(' '))}</desc>
<style>${fontFaceCss}${STYLE}</style>
<rect width="${width}" height="${height}" fill="${p.background}"/>
<text x="60" y="80" font-size="36" font-weight="650" letter-spacing="-0.5" fill="${p.strong}">${escapeXml(text.title)}</text>
<text x="60" y="114" font-size="18" fill="${p.muted}">${escapeXml(text.subtitle)}</text>
${step(0.2, box(72, 432, 656, 100, 'beet', text.beet, p.team, p.teamTint, p))}
${step(0.5, `<path d="M400 552 v18 m-6 -6 l6 6 l6 -6" fill="none" stroke="${p.muted}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>`
    + `<text x="400" y="596" text-anchor="middle" font-size="15" fill="${p.muted}">${escapeXml(text.output)}</text>`, 'stk-fade')}
${step(0.8, box(72, 314, 320, 102, 'bolt', text.bolt, p.team, p.teamTint, p))}
${step(0.95, box(408, 314, 320, 102, 'mecha', text.mecha, p.team, p.teamTint, p))}
${step(1.4, `<rect x="48" y="290" width="704" height="258" fill="none" stroke="${p.team}" stroke-width="1.5" stroke-dasharray="7 6"/>`
    + pill(72, 290, text.team, p.team, p.background, 14), 'stk-fade')}
${step(1.9, box(60, 146, 680, 108, 'StewBeet', text.stewbeet, p.stewbeet, p.stewbeetTint, p)
    + pill(740 - 24 - Math.round(text.stewbeetTag.length * 14 * 0.52 + 24), 176, text.stewbeetTag, p.stewbeet, p.panel, 14)
    + `<rect class="stk-spark" color="${p.stewbeet}" x="60" y="146" width="680" height="108" pathLength="100" fill="none" stroke="${p.stewbeet}" stroke-width="3" stroke-dasharray="6 94" stroke-linecap="round"/>`
    + `<path d="M400 258 v26 m-6 -6 l6 6 l6 -6" fill="none" stroke="${p.stewbeet}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>`
    + `<path class="stk-flow" d="M400 258 v24" fill="none" stroke="${p.stewbeet}" stroke-width="3" stroke-dasharray="4 8" stroke-linecap="round"/>`
    + `<text x="414" y="276" font-size="14" fill="${p.muted}">${escapeXml(text.plugsInto)}</text>`, 'stk-drop')}
<line x1="780" y1="146" x2="780" y2="548" stroke="${p.border}"/>
${step(2.1, `<text x="812" y="170" font-size="13" font-weight="600" letter-spacing="1.5" fill="${p.muted}">${escapeXml(text.factsTitle)}</text>`, 'stk-fade')}
${facts}
<text x="1140" y="596" text-anchor="end" font-size="15" fill="${p.muted}">stewbeet.paralya.fr</text>
</svg>`;
}

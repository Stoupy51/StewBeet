/**
 * Writes src/generated/mediaSizes.json: the width and height of every image and video the docs show,
 * keyed by the address the page loads it from, so the page holds their place before they load and
 * nothing under them moves.
 *
 * Images on raw.githubusercontent.com are files of this repository, read from the checkout.
 */
import { existsSync, readdirSync, readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const WEB = join(import.meta.dir, '..');
const DOCS = join(WEB, 'public', 'docs');
const REPOSITORY_FILE = /^https:\/\/raw\.githubusercontent\.com\/Stoupy51\/StewBeet\/(?:refs\/heads\/)?main\//;
const MEDIA = /!\[[^\]]*\]\(([^)\s]+)|<(?:img|video)\b[^>]*?\ssrc="([^"]+)"/g;

/** PNG, GIF, JPEG and MP4, the formats the docs use, each keep their size near the start of the file. */
function mediaSize(file: Buffer): [number, number] | undefined {
    if (file.toString('ascii', 1, 4) === 'PNG') return [file.readUInt32BE(16), file.readUInt32BE(20)];
    if (file.toString('ascii', 0, 3) === 'GIF') return [file.readUInt16LE(6), file.readUInt16LE(8)];
    if (file[0] === 0xff && file[1] === 0xd8) {
        // Segments follow one another until the start of frame, which holds the size
        for (let at = 2; file[at] === 0xff && at + 9 < file.length; at += 2 + file.readUInt16BE(at + 2)) {
            const marker = file[at + 1];
            if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) return [file.readUInt16BE(at + 7), file.readUInt16BE(at + 5)];
        }
        return undefined;
    }
    // MP4: a track header ends with the track's width and height in 16.16 fixed point, and only the video track's are set
    for (let at = file.indexOf('tkhd'); at !== -1; at = file.indexOf('tkhd', at + 4)) {
        const size = at + 4 + (file[at + 4] === 1 ? 88 : 76);
        const [width, height] = [file.readUInt32BE(size) >>> 16, file.readUInt32BE(size + 4) >>> 16];
        if (width && height) return [width, height];
    }
    return undefined;
}

const sizes: Record<string, [number, number]> = {};
for (const name of readdirSync(DOCS, { recursive: true, encoding: 'utf-8' }).filter((path) => path.endsWith('.md'))) {
    const page = `https://site/docs/${name.replaceAll('\\', '/')}`;
    for (const [, markdownSrc, htmlSrc] of readFileSync(join(DOCS, name), 'utf-8').matchAll(MEDIA)) {
        const src = markdownSrc ?? htmlSrc;
        // The address MarkdownPage gives the element: as written when absolute, else resolved against the page
        const address = /^https?:/.test(src) ? src : new URL(src, page).pathname;
        const path = REPOSITORY_FILE.test(address) ? join(WEB, '..', '..', address.replace(REPOSITORY_FILE, '')) : join(WEB, 'public', decodeURIComponent(address));
        const size = existsSync(path) ? mediaSize(readFileSync(path)) : undefined;
        if (size) sizes[address] = size;
        else console.warn(`No size for ${src} in ${name}: its page will move when it loads`);
    }
}

writeFileSync(join(WEB, 'src', 'generated', 'mediaSizes.json'), `${JSON.stringify(sizes, null, '\t')}\n`);
console.log(`Sizes of ${Object.keys(sizes).length} images and videos written to src/generated/mediaSizes.json`);

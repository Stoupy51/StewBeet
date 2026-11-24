/**
 * Heading anchor slugs.
 *
 * Shared by MarkdownPage.tsx (which renders the ids) and scripts/build-search-index.ts
 * (which stores them in the search index). Both must agree or deep links break.
 */

/** Convert a heading's plain text to its anchor id, accents folded so French headings keep readable ids (`é` -> `e`). */
export function slugify(text: string): string {
    return text
        .normalize('NFD')
        .replace(/[̀-ͯ]/g, '')
        .toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/\s+/g, '-');
}

/**
 * Strip inline markdown markers from a heading so the slug matches what the
 * renderer produces from the rendered text nodes (`**bold**` -> `bold`).
 */
export function headingTextToSlug(markdown: string): string {
    const plain = markdown
        .replace(/<[^>]*>/g, '')
        .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
        .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
        // Underscores only wrap emphasis when they surround a word: snake_case must survive
        .replace(/(^|\s)_([^_]+)_(?=\s|$)/g, '$1$2')
        .replace(/[*`~]/g, '')
        .trim();
    return slugify(plain);
}

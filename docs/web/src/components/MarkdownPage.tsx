import { useEffect, useState, useMemo, isValidElement } from 'react';
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { remarkAlert } from 'remark-github-blockquote-alert';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize';
import { motion, AnimatePresence } from 'framer-motion';
import { HiArrowLeft, HiExternalLink, HiMenu, HiX } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { ZoomableImage } from './ZoomableImage';
import { useLanguage } from '../context/LanguageContext';
import { useTranslation } from '../i18n/useTranslation';
import { useMarkdownContent } from '../context/MarkdownContentContext';
import { useShiki } from '../hooks/useShiki';
import { headingTextToSlug, slugify } from '../utils/slugify';
import { LOADER_ACCENT, PAGE, SELECTION_BRAND } from '../theme';

interface Heading {
    id: string;
    text: string;
    level: number;
}

const ALERT_TYPES = ['note', 'tip', 'important', 'warning', 'caution'];

/**
 * GitHub's schema, plus the `<video>` a guide needs to show a recording rather than describe it,
 * and the classes remark-github-blockquote-alert puts on a `> [!TIP]` block (its icon is SVG,
 * which the schema drops, so the title keeps only its text).
 */
const MARKDOWN_SCHEMA = {
    ...defaultSchema,
    tagNames: [...(defaultSchema.tagNames ?? []), 'video'],
    attributes: {
        ...defaultSchema.attributes,
        video: ['src', 'controls', 'loop', 'muted', 'playsInline', 'preload', 'width', 'height'],
        div: [...(defaultSchema.attributes?.div ?? []), ['className', 'markdown-alert', ...ALERT_TYPES.map((type) => `markdown-alert-${type}`)]],
        p: [...(defaultSchema.attributes?.p ?? []), ['className', 'markdown-alert-title']],
    },
};

const DOC_SRC_PATTERN = /^(?:[A-Za-z0-9._-]+\/)*[A-Za-z0-9._-]+\.md$/;
const FETCH_TIMEOUT_MS = 7000;
/** How long to keep an anchor aligned while Shiki finishes highlighting the code blocks. */
const SCROLL_SETTLE_MS = 4000;
const MAX_MARKDOWN_CHARS = 500_000;
/** Marks a fenced block: react-markdown puts the language on the <code>, and both the <pre> and <code> renderers key off it. */
const LANGUAGE_CLASS = /language-([A-Za-z0-9_-]+)/;

function isValidDocSrc(src: string): boolean {
    return DOC_SRC_PATTERN.test(src) && !src.includes('..');
}

function srcToGithubUrl(src: string): string {
    return `https://github.com/Stoupy51/StewBeet/blob/main/docs/web/public/docs/${src}`;
}

/**
 * Documentation is served by this site from public/docs, so a page always matches the build
 * it shipped with. `srcToGithubUrl` is still used for the "View on GitHub" link and as the
 * fetch target for external sources.
 */
function srcToBundledUrl(src: string): string {
    return `/docs/${src}`;
}

/**
 * Resolve a relative markdown link against the document containing it, so links between
 * guides and plugin pages stay on the site: `2_writing_to_files/en.md` +
 * `../1_definitions_setup/en.md#-resource-locations` -> `1_definitions_setup/en.md`.
 * Returns null for anything that escapes docs/ or is not a markdown page (images, source
 * files...), which the caller then sends to GitHub as before.
 */
function resolveDocSrc(currentSrc: string, href: string): { src: string; hash: string } | null {
    const [path, hash = ''] = href.split('#');
    const segments = currentSrc.split('/').slice(0, -1);

    for (const part of path.split('/')) {
        if (part === '' || part === '.') continue;
        if (part === '..') {
            if (segments.length === 0) return null;
            segments.pop();
            continue;
        }
        segments.push(part);
    }

    const src = segments.join('/');
    return isValidDocSrc(src) ? { src, hash } : null;
}

function githubToRawUrl(githubUrl: string): string {
    return githubUrl
        .replace('github.com/', 'raw.githubusercontent.com/')
        .replace('/blob/', '/')
        .replace('/raw/refs/heads/', '/');
}

/** Plain text of a rendered node: headings may contain <strong>, <code>, links... */
function getNodeText(node: React.ReactNode): string {
    if (typeof node === 'string' || typeof node === 'number') {
        return String(node);
    }
    if (Array.isArray(node)) {
        return node.map(getNodeText).join('');
    }
    if (isValidElement<{ children?: React.ReactNode }>(node)) {
        return getNodeText(node.props.children);
    }
    return '';
}

/** Heading renderer that gives every level an anchor id matching the search index. */
function makeHeading(Tag: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6') {
    const Heading = ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
        <Tag id={slugify(getNodeText(children))} {...props}>{children}</Tag>
    );
    Heading.displayName = `Markdown${Tag.toUpperCase()}`;
    return Heading;
}

const HEADING_COMPONENTS = {
    h1: makeHeading('h1'),
    h2: makeHeading('h2'),
    h3: makeHeading('h3'),
    h4: makeHeading('h4'),
    h5: makeHeading('h5'),
    h6: makeHeading('h6'),
};

const ShikiCodeBlock: React.FC<{ code: string; language: string }> = ({ code, language }) => {
    const highlighted = useShiki(code, language, 'dark-plus');

    if (!highlighted) {
        return (
            <pre className="code-dark">
                <code>{code}</code>
            </pre>
        );
    }

    // Padding, size and the panel around it all come from `.markdown-body .md-code` in index.css,
    // so a highlighted block and the plain one above measure the same before and after Shiki runs.
    return <div className="md-code code-dark" dangerouslySetInnerHTML={{ __html: highlighted }} />;
};

export const MarkdownPage: React.FC = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();
    const { hash, search } = useLocation();
    const { language } = useLanguage();
    const { t } = useTranslation();
    const src = searchParams.get('src');
    // ssrContent is non-null when pre-rendered by the SSR server (server.tsx)
    const ssrContent = useMarkdownContent();
    const [content, setContent] = useState<string>(ssrContent ?? '');
    const [loading, setLoading] = useState<boolean>(ssrContent === null);
    const [error, setError] = useState<string | null>(null);
    const [tocOpen, setTocOpen] = useState<boolean>(false);
    
    // Handle language change - update URL if it ends with /en.md or /fr.md
    useEffect(() => {
        if (!src) return;
        
        const currentLang = src.endsWith('/en.md') ? 'en' : src.endsWith('/fr.md') ? 'fr' : null;
        
        if (currentLang && currentLang !== language) {
            // Replace the language in the URL
            const newSrc = src.replace(new RegExp(`/${currentLang}\\.md$`), `/${language}.md`);
            setSearchParams({ src: newSrc });
        }
    }, [language, src, setSearchParams]);
    
    // A bare <a href="#id"> is a same-document jump: it fires hashchange, which the router
    // does not listen to, so useLocation().hash would never update and the scroll effect
    // below would never run. Going through navigate() keeps both in sync.
    const goToHeading = (id: string) => (event: React.MouseEvent) => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        setTocOpen(false);

        // Re-clicking the current heading leaves the hash untouched, so the effect would
        // not re-run; by now the layout has settled and a plain scroll is enough.
        if (hash === `#${id}`) {
            document.getElementById(id)?.scrollIntoView();
            return;
        }
        navigate({ search, hash: `#${id}` });
    };

    const handleBack = () => {
        // Check if there's history to go back to
        if (window.history.length > 1) {
            navigate(-1);
        } else {
            // No history, go to plugins section
            navigate('/#plugins');
        }
    };

    const isExternalUrl = (s: string) => s.startsWith('https://') || s.startsWith('http://');
    const hasValidSrc = src ? (isExternalUrl(src) || isValidDocSrc(src))  : false;
    
    // Construct the full URL
    const fullUrl = src && hasValidSrc ? (isExternalUrl(src) ? src : srcToGithubUrl(src)) : null;
    
    // Convert to raw URL for fetching
    const rawUrl = fullUrl ? githubToRawUrl(fullUrl) : null;

    // Repo documentation is served by this site; external sources still come from their host.
    const bundledUrl = src && hasValidSrc && !isExternalUrl(src) ? srcToBundledUrl(src) : null;
    
    // Extract the base path for relative links (directory containing the markdown file)
    const basePath = rawUrl
        ? rawUrl.substring(0, rawUrl.lastIndexOf('/'))
        : null;

    // Only a document from the repo's own docs/ folder can resolve its links to site routes
    const localSrc = src && hasValidSrc && !isExternalUrl(src) ? src : null;

    // Extract headings for table of contents
    const headings = useMemo(() => {
        if (!content) return [];
        
        // Remove code blocks first to avoid matching # inside them
        const contentWithoutCodeBlocks = content.replace(/```[\s\S]*?```/g, '');
        
        const headingRegex = /^(#{1,6})\s+(.+)$/gm;
        const matches: Heading[] = [];
        let match;
        
        while ((match = headingRegex.exec(contentWithoutCodeBlocks)) !== null) {
            const level = match[1].length;
            let text = match[2].trim();

            // The id must come from the original heading, since that is what the renderer uses
            const id = headingTextToSlug(text);

            // Remove HTML tags from text
            text = text.replace(/<[^>]*>/g, '');

            // Remove markdown bold markers
            text = text.replace(/\*\*/g, '');

            // The document's own H1 is the label; it used to be swapped for the src path,
            // which showed the reader `5_dependencies/en` instead of the page title.

            matches.push({ id, text, level });
        }
        
        return matches;
    }, [content]);

    useEffect(() => {
        if (!src) {
            setError(t('markdown.noPlugin'));
            setLoading(false);
            return;
        }

        const fetchMarkdown = async () => {
            setLoading(true);
            setError(null);

            const controller = new AbortController();
            const timeoutId = window.setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
            try {
                if (!rawUrl) {
                    throw new Error('Invalid source URL');
                }

                let response = await fetch(bundledUrl ?? rawUrl, { signal: controller.signal });

                // A page that has not been translated yet should read in English, not 404.
                if (!response.ok && bundledUrl?.endsWith('/fr.md')) {
                    response = await fetch(bundledUrl.replace(/\/fr\.md$/, '/en.md'), { signal: controller.signal });
                }

                if (!response.ok) {
                    throw new Error(`Failed to fetch plugin documentation (${response.status})`);
                }

                const text = await response.text();
                if (text.length > MAX_MARKDOWN_CHARS) {
                    throw new Error('Documentation is too large to display safely.');
                }
                setContent(text);
            } catch (err) {
                if (err instanceof Error && err.name === 'AbortError') {
                    setError('Request timed out while loading plugin documentation.');
                    return;
                }
                setError(err instanceof Error ? err.message : 'Failed to load plugin documentation');
            } finally {
                window.clearTimeout(timeoutId);
                setLoading(false);
            }
        };

        fetchMarkdown();
    }, [src, rawUrl, bundledUrl, t]);

    // Scroll to the heading targeted by the URL hash (search results, shared links).
    // The content arrives asynchronously, so this cannot rely on the browser's own handling.
    useEffect(() => {
        if (loading || !content) return;

        // A plain document link keeps the previous page's scroll offset otherwise
        if (!hash) {
            window.scrollTo({ top: 0 });
            return;
        }

        const id = decodeURIComponent(hash.slice(1));
        const scroll = () => document.getElementById(id)?.scrollIntoView();
        scroll();

        // Shiki replaces every code block with taller highlighted markup one grammar at a
        // time, pushing later headings down long after the first paint. Re-align on each
        // layout change until it settles, or a deep anchor lands hundreds of pixels short.
        const observer = new ResizeObserver(scroll);
        observer.observe(document.body);

        // The reader taking over always wins over a late correction
        const release = () => observer.disconnect();
        const timeout = window.setTimeout(release, SCROLL_SETTLE_MS);
        window.addEventListener('wheel', release, { passive: true });
        window.addEventListener('touchstart', release, { passive: true });
        window.addEventListener('keydown', release);

        return () => {
            window.clearTimeout(timeout);
            window.removeEventListener('wheel', release);
            window.removeEventListener('touchstart', release);
            window.removeEventListener('keydown', release);
            observer.disconnect();
        };
    }, [loading, content, hash]);

    // Set page title
    useEffect(() => {
        // The document's own H1, falling back to the source path only if it has none
        // a browser tab reading `5_dependencies/en` tells the reader nothing.
        const heading = content.match(/^#\s+(.+)$/m)?.[1].replace(/[*`]/g, '').trim();
        const label = heading || (src && hasValidSrc ? src.replace('.md', '') : 'Documentation');

        document.title = `${label} | StewBeet`;
        
        // Reset title when component unmounts
        return () => {
            document.title = 'StewBeet';
        };
    }, [src, hasValidSrc, content]);

    const tocLinks = (
        <nav className="flex flex-col border-l border-ink-800">
            {headings.filter((heading) => heading.level > 1).map((heading, idx) => (
                <a
                    key={idx}
                    href={`#${heading.id}`}
                    onClick={goToHeading(heading.id)}
                    className={`-ml-px border-l py-1 text-sm leading-snug transition-colors ${
                        hash === `#${heading.id}` ? 'border-beet-400 text-ink-50' : 'border-transparent text-ink-400 hover:text-ink-100 hover:border-ink-500'
                    } ${heading.level === 2 ? 'pl-3' : 'pl-6'}`}
                >
                    {heading.text.replace(/`/g, '')}
                </a>
            ))}
        </nav>
    );

    return (
        // pt-14 makes room for the fixed navbar, so the toolbar's place in the flow matches where it is pinned.
        <div className={`doc-page min-h-screen pt-14 bg-ink-950 text-ink-200 ${SELECTION_BRAND}`}>
            <Navbar />

            {/* Toolbar, kept to one line: it is pinned over the document for the whole read. */}
            <div className="sticky top-14 z-30 border-b border-ink-800 bg-ink-950/90 backdrop-blur-md">
                <div className={`${PAGE} h-11 flex items-center justify-between`}>
                    <button onClick={handleBack} className="group flex items-center gap-2 text-sm text-ink-300 hover:text-ink-50 transition-colors">
                        <HiArrowLeft className="group-hover:-translate-x-0.5 transition-transform" aria-hidden="true" />
                        {t('markdown.back')}
                    </button>

                    <div className="flex items-center gap-4">
                        {headings.length > 0 && (
                            <button
                                onClick={() => setTocOpen(!tocOpen)}
                                className="lg:hidden flex items-center gap-1.5 text-sm text-ink-300 hover:text-ink-50 transition-colors"
                            >
                                <HiMenu aria-hidden="true" />
                                {t('markdown.contents')}
                            </button>
                        )}
                        {fullUrl && (
                            <a
                                href={fullUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1.5 text-sm text-ink-400 hover:text-ink-100 transition-colors"
                            >
                                {t('markdown.viewOnGithub')}
                                <HiExternalLink aria-hidden="true" />
                            </a>
                        )}
                    </div>
                </div>
            </div>

            <div className={`${PAGE} py-10 md:py-14`}>
                <div className="flex gap-12 xl:gap-16 items-start">
                    {headings.length > 0 && (
                        <aside className="hidden lg:block sticky top-[calc(var(--doc-header)_+_2rem)] w-60 shrink-0 self-start max-h-[calc(100vh_-_var(--doc-header)_-_4rem)] overflow-y-auto pb-6 [&::-webkit-scrollbar]:hidden [scrollbar-width:none]">
                            <p className="mb-3 font-mono text-xs uppercase tracking-wider text-ink-500">{t('markdown.contents')}</p>
                            {tocLinks}
                        </aside>
                    )}

                    <div className="flex-1 min-w-0 max-w-[48rem]">
                {loading && (
                    <div className="flex items-center justify-center py-20">
                        <div className={`animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 ${LOADER_ACCENT}`}></div>
                    </div>
                )}

                {error && (
                    <div className="rounded-panel border border-mc-gold/30 bg-mc-gold/5 p-8">
                        <p className="text-mc-gold text-lg font-semibold mb-2">{t('markdown.error')}</p>
                        <p className="text-ink-300 text-lg">{error}</p>
                    </div>
                )}

                {!loading && !error && content && (
                    <div>
                        {/* Every size and margin lives in `.markdown-body` in index.css. */}
                        <article className="markdown-body">
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm, remarkAlert]}
                            rehypePlugins={[rehypeRaw, [rehypeSanitize, MARKDOWN_SCHEMA]]}
                            components={{
                                pre({ children }: React.HTMLAttributes<HTMLPreElement>) {
                                    // The child is the `code` renderer below, still unrendered, so the language class is the only way to tell it apart here.
                                    // A fenced block becomes a ShikiCodeBlock, which draws its own panel and must not be wrapped in a second one.
                                    if (isValidElement<{ className?: string }>(children) && LANGUAGE_CLASS.test(children.props.className ?? '')) {
                                        return children;
                                    }
                                    return <pre className="code-dark">{children}</pre>;
                                },
                                code({ inline, className, children }: React.HTMLAttributes<HTMLElement> & { inline?: boolean }) {
                                    const match = LANGUAGE_CLASS.exec(className || '');
                                    const language = match ? match[1] : '';
                                    const code = String(children).replace(/\n$/, '');

                                    return !inline && language ? (
                                        <ShikiCodeBlock code={code} language={language} />
                                    ) : (
                                        // The rest of react-markdown's props are not spread here: they carry the hast `node`, which React writes out as node="[object Object]".
                                        <code className={className}>
                                            {children}
                                        </code>
                                    );
                                },
                                    ...HEADING_COMPONENTS,
                                img({ src, alt }: React.ImgHTMLAttributes<HTMLImageElement>) {
                                    // Convert relative GitHub image paths to absolute URLs
                                    let imageSrc = src;
                                    
                                    if (src && !src.startsWith('http') && basePath) {
                                        // Relative path - resolve based on current document location
                                        if (src.startsWith('img/')) {
                                            imageSrc = `${basePath}/${src}`;
                                        } else if (src.startsWith('./') || src.startsWith('../')) {
                                            // Handle relative paths
                                            imageSrc = `${basePath}/${src}`;
                                        } else {
                                            imageSrc = `${basePath}/${src}`;
                                        }
                                    }
                                    
                                    // Check if this is a badge/shield image
                                    const isBadge = src?.includes('shields.io') || src?.includes('img.shields.io') || 
                                                   src?.includes('badge') || src?.includes('github.com/workflows');
                                    
                                    if (isBadge) return <img src={imageSrc} alt={alt} className="inline-block h-6 mr-2 my-1" />;
                                    return (
                                        <ZoomableImage
                                            src={imageSrc ?? ''}
                                            alt={alt ?? ''}
                                            frameClassName="max-w-full align-top"
                                            className="max-w-full h-auto rounded-control"
                                        />
                                    );
                                },
                                a({ href, children }: React.AnchorHTMLAttributes<HTMLAnchorElement>) {
                                    // Keep anchor links as-is
                                    const isAnchor = href?.startsWith('#');
                                    const isExternal = href?.startsWith('http');
                                    const isRelative = !isAnchor && !isExternal && !!href && !!basePath;

                                    // A link to another documentation page keeps the reader on the site
                                    const target = isRelative && localSrc ? resolveDocSrc(localSrc, href) : null;
                                    const internalHref = target
                                        ? `/markdown?src=${encodeURIComponent(target.src)}${target.hash ? `#${target.hash}` : ''}`
                                        : null;

                                    let linkHref = internalHref ?? href;
                                    if (isRelative && !internalHref) {
                                        // Anything else (images, source files) still points at GitHub.
                                        // Convert basePath from raw.githubusercontent to github.com/blob format
                                        const viewBasePath = basePath.replace(
                                            'https://raw.githubusercontent.com/',
                                            'https://github.com/'
                                        ).replace('/main/', '/blob/main/');

                                        linkHref = `${viewBasePath}/${href}`;
                                    }

                                    // Leaving the site: including the GitHub fallback built just above
                                    const opensAway = linkHref?.startsWith('http') ?? false;

                                    return (
                                        <a
                                            href={linkHref}
                                            target={opensAway ? '_blank' : undefined}
                                            rel={opensAway ? 'noopener noreferrer' : undefined}
                                            onClick={
                                                // In-page links need the same settle handling as the contents panel
                                                isAnchor && href ? goToHeading(decodeURIComponent(href.slice(1)))
                                                : internalHref ? (event) => {
                                                    // Let the browser keep ctrl/cmd-click opening a new tab
                                                    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
                                                    event.preventDefault();
                                                    navigate(internalHref);
                                                }
                                                : undefined
                                            }
                                        >
                                            {children}
                                        </a>
                                    );
                                }
                            }}
                        >
                            {content}
                        </ReactMarkdown>
                    </article>
                    </div>
                )}
                    </div>
                </div>
            </div>

            {/* Mobile TOC Overlay */}
            <AnimatePresence>
                {tocOpen && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            transition={{ duration: 0.2 }}
                            onClick={() => setTocOpen(false)}
                            className="fixed inset-0 bg-black/60 z-40 lg:hidden"
                        />
                        <motion.div
                            initial={{ x: '100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '100%' }}
                            transition={{ type: 'tween', duration: 0.3 }}
                            className="fixed top-0 right-0 bottom-0 w-80 bg-ink-950 border-l border-ink-800 z-50 overflow-y-auto lg:hidden"
                        >
                            <div className="p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <p className="font-mono text-xs uppercase tracking-wider text-ink-500">{t('markdown.contents')}</p>
                                    <button onClick={() => setTocOpen(false)} aria-label={t('search.close')} className="p-2 rounded-control hover:bg-ink-850 transition-colors">
                                        <HiX className="text-xl text-ink-400" />
                                    </button>
                                </div>
                                {tocLinks}
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
            
            <Footer />
        </div>
    );
};

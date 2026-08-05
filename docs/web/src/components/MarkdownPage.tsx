import { useEffect, useState, useMemo, isValidElement } from 'react';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';
import { motion, AnimatePresence } from 'framer-motion';
import { HiArrowLeft, HiExternalLink, HiMenu, HiX } from 'react-icons/hi';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { useLanguage } from '../context/LanguageContext';
import { useTranslation } from '../i18n/useTranslation';
import { useMarkdownContent } from '../context/MarkdownContentContext';
import { useShiki } from '../hooks/useShiki';
import { headingTextToSlug, slugify } from '../utils/slugify';
import { ALERT_ACCENT, LOADER_ACCENT, PROSE_BRAND, SELECTION_BRAND, TEXT_ACCENT, TEXT_ACCENT_HOVER, TOOLBAR_ACCENT } from '../theme';

interface Heading {
    id: string;
    text: string;
    level: number;
}

const DOC_SRC_PATTERN = /^(?:[A-Za-z0-9._-]+\/)*[A-Za-z0-9._-]+\.md$/;
const FETCH_TIMEOUT_MS = 7000;
/** How long to keep an anchor aligned while Shiki finishes highlighting the code blocks. */
const SCROLL_SETTLE_MS = 4000;
const MAX_MARKDOWN_CHARS = 500_000;

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

/** Plain text of a rendered node — headings may contain <strong>, <code>, links... */
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
            <pre>
                <code>{code}</code>
            </pre>
        );
    }

    return (
        <div
            dangerouslySetInnerHTML={{ __html: highlighted }}
            className="[&>pre]:!bg-transparent [&>pre]:!m-0 [&>pre]:!p-4"
        />
    );
};

export const MarkdownPage: React.FC = () => {
    const motionSafe = useMotionSafe();
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

                const response = await fetch(bundledUrl ?? rawUrl, { signal: controller.signal });

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
        // The document's own H1, falling back to the source path only if it has none —
        // a browser tab reading `5_dependencies/en` tells the reader nothing.
        const heading = content.match(/^#\s+(.+)$/m)?.[1].replace(/[*`]/g, '').trim();
        const label = heading || (src && hasValidSrc ? src.replace('.md', '') : 'Documentation');

        document.title = `${label} | StewBeet`;
        
        // Reset title when component unmounts
        return () => {
            document.title = 'StewBeet';
        };
    }, [src, hasValidSrc, content]);

    return (
        <div className={`min-h-screen bg-slate-950 text-slate-100 ${SELECTION_BRAND}`}>
            <Navbar />
            
            {/* Header with back button */}
            <div className="sticky top-16 z-30 border-b border-white/10 bg-slate-950/80 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
                    <button
                        onClick={handleBack}
                        className={`flex items-center gap-2 ${TEXT_ACCENT_HOVER} group`}
                    >
                        <HiArrowLeft className="text-xl group-hover:-translate-x-1 transition-transform" />
                        <span className="font-medium">{t('markdown.back')}</span>
                    </button>
                    
                    <div className="flex items-center gap-4">
                        {headings.length > 0 && (
                            <button
                                onClick={() => setTocOpen(!tocOpen)}
                                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all lg:hidden ${TOOLBAR_ACCENT}`}
                            >
                                <HiMenu className="text-xl" />
                                <span className="text-sm font-medium">{t('markdown.contents')}</span>
                            </button>
                        )}
                        {fullUrl && (
                            <a
                                href={fullUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 text-slate-400 hover:text-slate-200 transition-colors text-sm group"
                            >
                                <span>{t('markdown.viewOnGithub')}</span>
                                <HiExternalLink className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                            </a>
                        )}
                    </div>
                </div>
            </div>

            {/* Content */}
            <motion.div
                {...motionSafe({
                    initial: { y: 20 },
                    animate: { y: 0 },
                    transition: { duration: 0.5 },
                })}
                className="relative z-10 max-w-7xl mx-auto px-4 py-16"
            >
                <div className="flex gap-8 items-start">
                    {/* Table of Contents - Desktop */}
                    {headings.length > 0 && (
                        <aside className="hidden lg:block sticky top-24 w-64 shrink-0 self-start max-h-[calc(100vh-7rem)] overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
                            <div className="bg-slate-900/30 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                                <h3 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2 sticky top-0 bg-slate-900/30 backdrop-blur-sm -mx-6 px-6 pb-4">
                                    <HiMenu className={TEXT_ACCENT} />
                                    Contents
                                </h3>
                                <nav className="space-y-2">
                                    {headings.map((heading, idx) => (
                                        <a
                                            key={idx}
                                            href={`#${heading.id}`}
                                            className={`block text-sm hover:text-mc-emerald transition-colors ${
                                                heading.level === 1 ? 'font-semibold text-slate-300' :
                                                heading.level === 2 ? 'pl-4 text-slate-400' :
                                                'pl-8 text-slate-400'
                                            }`}
                                            onClick={goToHeading(heading.id)}
                                        >
                                            {heading.text}
                                        </a>
                                    ))}
                                </nav>
                            </div>
                        </aside>
                    )}

                    {/* Main Content */}
                    <div className="flex-1 min-w-0">
                {loading && (
                    <div className="flex items-center justify-center py-20">
                        <div className={`animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 ${LOADER_ACCENT}`}></div>
                    </div>
                )}

                {error && (
                    <div className={`rounded-xl p-8 text-center backdrop-blur-sm ${ALERT_ACCENT}`}>
                        <p className="text-mc-emerald text-xl font-bold mb-3">{t('markdown.error')}</p>
                        <p className="text-slate-300 text-lg">{error}</p>
                    </div>
                )}

                {!loading && !error && content && (
                    <div className="bg-slate-900/30 backdrop-blur-sm border border-white/10 rounded-2xl p-8 md:p-12 shadow-2xl">
                        <article className={`prose prose-invert prose-slate prose-lg max-w-none
                            prose-headings:font-bold prose-headings:scroll-mt-32
                            prose-h1:text-3xl prose-h1:mb-6 prose-h1:border-b-2 prose-h1:border-white/20 prose-h1:pb-4
                            prose-h2:text-2xl prose-h2:mt-12 prose-h2:mb-5 prose-h2:border-b prose-h2:border-white/10 prose-h2:pb-2
                            prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-3 prose-h3:text-slate-200
                            prose-h4:text-xl prose-h4:mt-8 prose-h4:mb-3 prose-h4:text-slate-300
                            prose-h5:text-lg prose-h5:mt-6 prose-h5:mb-2 prose-h5:text-slate-300
                            prose-h6:text-base prose-h6:mt-4 prose-h6:mb-2 prose-h6:text-slate-400
                            prose-p:text-slate-300 prose-p:leading-relaxed prose-p:my-4
                            prose-a:no-underline hover:prose-a:underline prose-a:underline-offset-4 prose-a:transition-colors
                            prose-code:bg-slate-800/50 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-sm prose-code:font-medium prose-code:before:content-none prose-code:after:content-none
                            [&_pre_code]:bg-transparent [&_pre_code]:p-0 [&_pre_code]:rounded-none
                            prose-pre:bg-slate-900/90 prose-pre:border prose-pre:border-white/10 prose-pre:rounded-xl prose-pre:shadow-xl prose-pre:my-6
                            prose-strong:text-slate-100 prose-strong:font-bold
                            prose-em:text-slate-300 prose-em:italic
                            prose-ul:my-6 prose-ul:text-slate-300 prose-ol:my-6 prose-ol:text-slate-300
                            prose-li:my-2
                            prose-blockquote:border-l-4 prose-blockquote:py-2 prose-blockquote:px-6 prose-blockquote:my-6 prose-blockquote:rounded-r-lg prose-blockquote:text-slate-300 prose-blockquote:italic
                            prose-img:rounded-xl prose-img:border prose-img:border-white/20 prose-img:shadow-2xl prose-img:my-8
                            prose-table:border prose-table:border-white/10 prose-table:rounded-lg prose-table:overflow-hidden prose-table:my-8
                            prose-thead:bg-slate-800/50 prose-thead:border-b-2 prose-thead:border-white/20
                            prose-th:text-slate-200 prose-th:font-bold prose-th:px-6 prose-th:py-4 prose-th:text-left
                            prose-td:text-slate-300 prose-td:px-6 prose-td:py-4 prose-td:border-t prose-td:border-white/10
                            prose-hr:border-white/20 prose-hr:border-t-2 prose-hr:my-12
                            ${PROSE_BRAND}`}>
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            rehypePlugins={[rehypeRaw, rehypeSanitize]}
                            components={{
                                code({ inline, className, children, ...props }: React.HTMLAttributes<HTMLElement> & { inline?: boolean }) {
                                    const match = /language-([A-Za-z0-9_-]+)/.exec(className || '');
                                    const language = match ? match[1] : '';
                                    const code = String(children).replace(/\n$/, '');
                                    
                                    return !inline && language ? (
                                        <ShikiCodeBlock code={code} language={language} />
                                    ) : (
                                        <code className={className} {...props}>
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
                                    
                                    return (
                                        <img
                                            src={imageSrc}
                                            alt={alt}
                                            className={isBadge 
                                                ? "inline-block h-6 mr-2 my-1" 
                                                : "max-w-full h-auto hover:scale-[1.02] transition-transform duration-300"
                                            }
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

                                    // Leaving the site — including the GitHub fallback built just above
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
            </motion.div>
            
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
                            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
                        />
                        <motion.div
                            initial={{ x: '100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '100%' }}
                            transition={{ type: 'tween', duration: 0.3 }}
                            className="fixed top-0 right-0 bottom-0 w-80 bg-slate-900 border-l border-white/10 z-50 overflow-y-auto lg:hidden"
                        >
                            <div className="p-6">
                                <div className="flex items-center justify-between mb-6">
                                    <h3 className="text-lg font-bold text-slate-200 flex items-center gap-2">
                                        <HiMenu className={TEXT_ACCENT} />
                                        Contents
                                    </h3>
                                    <button
                                        onClick={() => setTocOpen(false)}
                                        className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                                    >
                                        <HiX className="text-xl text-slate-400" />
                                    </button>
                                </div>
                                <nav className="space-y-2">
                                    {headings.map((heading, idx) => (
                                        <a
                                            key={idx}
                                            href={`#${heading.id}`}
                                            className={`block text-sm hover:text-mc-emerald transition-colors ${
                                                heading.level === 1 ? 'font-semibold text-slate-300' :
                                                heading.level === 2 ? 'pl-4 text-slate-400' :
                                                'pl-8 text-slate-400'
                                            }`}
                                            onClick={goToHeading(heading.id)}
                                        >
                                            {heading.text}
                                        </a>
                                    ))}
                                </nav>
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
            
            <Footer />
        </div>
    );
};

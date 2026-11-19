import { useCallback, useEffect, useMemo, useRef, useState, isValidElement } from 'react';
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import ReactMarkdown, { type Components, type Options } from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { remarkAlert } from 'remark-github-blockquote-alert';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize';
import type { Element } from 'hast';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { ZoomableImage } from './ZoomableImage';
import { CodeBlock, CodeTabs } from './DocCode';
import { Breadcrumb, DocBar, PageAside, PageList, PagesPanel, PreviousNext, SourceLinks, type TocHeading } from './DocNav';
import { useLanguage } from '../context/LanguageContext';
import { useTranslation } from '../i18n/useTranslation';
import { useMarkdownContent } from '../context/MarkdownContentContext';
import { SECTIONS, docSrc, findDocPage, srcHref } from '../docsPages';
import { markdownPageMeta } from '../utils/pageMeta';
import { headingTextToSlug, slugify } from '../utils/slugify';
import { metaValue, rehypeCodeTabs, rehypeSteps, rehypeTableLabels, remarkCodeMeta, textOf } from '../utils/docMarkdown';

const ALERT_TYPES = ['note', 'tip', 'important', 'warning', 'caution'];

/**
 * GitHub's schema, plus the `<video>` a guide needs to show a recording rather than describe it,
 * the classes remark-github-blockquote-alert puts on a `> [!TIP]` block (its icon is SVG, which the
 * schema drops, so the title keeps only its text), and the text after a fence's language.
 */
const MARKDOWN_SCHEMA = {
    ...defaultSchema,
    tagNames: [...(defaultSchema.tagNames ?? []), 'video'],
    attributes: {
        ...defaultSchema.attributes,
        video: ['src', 'controls', 'loop', 'muted', 'playsInline', 'preload', 'width', 'height'],
        div: [...(defaultSchema.attributes?.div ?? []), ['className', 'markdown-alert', ...ALERT_TYPES.map((type) => `markdown-alert-${type}`)]],
        p: [...(defaultSchema.attributes?.p ?? []), ['className', 'markdown-alert-title']],
        code: [...(defaultSchema.attributes?.code ?? []), 'dataMeta'],
    },
};

const REMARK_PLUGINS: Options['remarkPlugins'] = [remarkGfm, remarkAlert, remarkCodeMeta];
const REHYPE_PLUGINS: Options['rehypePlugins'] = [rehypeRaw, [rehypeSanitize, MARKDOWN_SCHEMA], rehypeCodeTabs, rehypeSteps, rehypeTableLabels];

const DOC_SRC_PATTERN = /^(?:[A-Za-z0-9._-]+\/)*[A-Za-z0-9._-]+\.md$/;
const FETCH_TIMEOUT_MS = 7000;
/** How long to keep an anchor aligned while Shiki finishes highlighting the code blocks. */
const SCROLL_SETTLE_MS = 4000;
/** Marks a fenced block: react-markdown puts the language on the <code>. */
const LANGUAGE_CLASS = /language-([A-Za-z0-9_-]+)/;
/** Where a relative link to something other than a page leads: the file in the repository. */
const REPO_DOCS_URL = 'https://github.com/Stoupy51/StewBeet/blob/main/docs/web/public/docs/';

function isValidDocSrc(src: string): boolean {
    return DOC_SRC_PATTERN.test(src) && !src.includes('..');
}

/**
 * Resolve a relative markdown link against the document containing it, so links between
 * guides and plugin pages stay on the site: `2_writing_to_files/en.md` +
 * `../1_definitions_setup/en.md#-resource-locations` -> `1_definitions_setup/en.md`.
 * Returns null for anything that escapes docs/ or is not a markdown page (images, source
 * files...), which the caller then sends to GitHub.
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

/** Plain text of a rendered node: headings may contain <strong>, <code>, links... */
function getNodeText(node: React.ReactNode): string {
    if (typeof node === 'string' || typeof node === 'number') return String(node);
    if (Array.isArray(node)) return node.map(getNodeText).join('');
    if (isValidElement<{ children?: React.ReactNode }>(node)) return getNodeText(node.props.children);
    return '';
}

/** Heading renderer that gives every level an anchor id matching the search index. A step's heading arrives with its id already set. */
function makeHeading(Tag: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6') {
    const Heading = ({ children, id, style }: React.HTMLAttributes<HTMLHeadingElement>) => (
        <Tag id={id ?? slugify(getNodeText(children))} style={style}>{children}</Tag>
    );
    Heading.displayName = `Markdown${Tag.toUpperCase()}`;
    return Heading;
}

/** The fenced block inside a `<pre>`: its code, its language and the text after the language. */
function fencedCode(pre: Element) {
    const code = pre.children.find((child): child is Element => child.type === 'element' && child.tagName === 'code');
    const className = (code?.properties.className as string[] | undefined)?.join(' ') ?? '';
    return {
        code: code ? textOf(code).replace(/\n$/, '') : '',
        language: LANGUAGE_CLASS.exec(className)?.[1] ?? 'text',
        meta: code?.properties.dataMeta as string | undefined,
    };
}

export const MarkdownPage: React.FC = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();
    const { hash, search } = useLocation();
    const { language } = useLanguage();
    const { t } = useTranslation();
    const src = searchParams.get('src');
    const prerendered = useMarkdownContent();
    // Only for the page server.tsx rendered: once the reader moves on, the embedded markdown belongs to another page
    const initialContent = prerendered?.src === src ? prerendered.content : null;
    const [content, setContent] = useState<string>(initialContent ?? '');
    const [loading, setLoading] = useState<boolean>(initialContent === null);
    const prerenderedSrc = useRef(initialContent === null ? null : src);
    const [error, setError] = useState<string | null>(null);
    const [pagesOpen, setPagesOpen] = useState(false);
    const validSrc = src && isValidDocSrc(src) ? src : null;
    const page = validSrc ? findDocPage(validSrc) : undefined;

    // A page follows the reader to the other language when it is written in it
    useEffect(() => {
        if (page && docSrc(page, language) !== validSrc) setSearchParams({ src: docSrc(page, language) });
    }, [language, page, validSrc, setSearchParams]);

    // A bare <a href="#id"> is a same-document jump: it fires hashchange, which the router
    // does not listen to, so useLocation().hash would never update and the scroll effect
    // below would never run. Going through navigate() keeps both in sync.
    const goToHeading = useCallback((id: string) => (event: React.MouseEvent) => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();

        // Re-clicking the current heading leaves the hash untouched, so the effect would
        // not re-run; by now the layout has settled and a plain scroll is enough.
        if (hash === `#${id}`) {
            document.getElementById(id)?.scrollIntoView();
            return;
        }
        navigate({ search, hash: `#${id}` });
    }, [hash, navigate, search]);

    // The H2s, for "On this page": deeper levels would turn a long guide's list into a second page.
    const headings = useMemo<TocHeading[]>(() => {
        const withoutCode = content.replace(/```[\s\S]*?```/g, '');
        return [...withoutCode.matchAll(/^##\s+(.+)$/gm)].map(([, text]) => ({
            id: headingTextToSlug(text.trim()),
            text: text.replace(/<[^>]*>/g, '').replace(/\*\*|`/g, '').trim(),
        }));
    }, [content]);

    useEffect(() => {
        if (!validSrc) {
            setError(t('markdown.noPage'));
            setLoading(false);
            return;
        }

        // Already on screen from the embedded markdown: fetching it again would swap the page for the loading state
        if (validSrc === prerenderedSrc.current) return;
        prerenderedSrc.current = null;

        const controller = new AbortController();
        let timedOut = false;
        const timeoutId = window.setTimeout(() => {
            timedOut = true;
            controller.abort();
        }, FETCH_TIMEOUT_MS);
        setLoading(true);
        setError(null);

        (async () => {
            try {
                const response = await fetch(`/docs/${validSrc}`, { signal: controller.signal });
                if (response.ok) setContent(await response.text());
                else setError(t('markdown.notFound'));
                setLoading(false);
            } catch {
                // Aborted by the cleanup: the reader moved on, and the next run owns the state
                if (controller.signal.aborted && !timedOut) return;
                setError(t('markdown.unreachable'));
                setLoading(false);
            } finally {
                window.clearTimeout(timeoutId);
            }
        })();

        return () => {
            window.clearTimeout(timeoutId);
            controller.abort();
        };
    }, [validSrc, t]);

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

        // Images and highlighting can still change the height above the heading after the first
        // paint. Re-align on each layout change until it settles, or a deep anchor lands short.
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

    // Same title as the one server.tsx writes into the head
    useEffect(() => {
        document.title = markdownPageMeta(validSrc, content).title;
        return () => {
            document.title = 'StewBeet';
        };
    }, [validSrc, content]);

    const components = useMemo<Components>(() => ({
        h1: makeHeading('h1'),
        h2: makeHeading('h2'),
        h3: makeHeading('h3'),
        h4: makeHeading('h4'),
        h5: makeHeading('h5'),
        h6: makeHeading('h6'),
        pre({ node, style }) {
            return node ? <CodeBlock {...fencedCode(node)} style={style} /> : null;
        },
        div({ node, ...props }) {
            if (node?.properties.dataTabs === undefined) return <div {...props} />;
            const tabs = node.children
                .filter((child): child is Element => child.type === 'element' && child.tagName === 'pre')
                .map((pre) => {
                    const { code, language: lang, meta } = fencedCode(pre);
                    return { code, language: lang, label: metaValue(meta, 'tab') ?? lang };
                });
            return <CodeTabs tabs={tabs} style={props.style} />;
        },
        img({ src: imageSrc, alt, width, height }) {
            // Relative images are served by this site, beside the page that shows them
            const resolved = imageSrc && validSrc && !/^https?:/.test(imageSrc)
                ? new URL(imageSrc, `https://site/docs/${validSrc}`).pathname
                : imageSrc;
            return (
                <ZoomableImage
                    src={resolved ?? ''}
                    alt={alt ?? ''}
                    width={width}
                    height={height}
                    frameClassName="max-w-full align-top"
                    className="max-w-full h-auto"
                />
            );
        },
        a({ href, children }) {
            const isAnchor = href?.startsWith('#');
            const isExternal = !href || /^[a-z]+:/i.test(href);
            const target = !isAnchor && !isExternal && validSrc ? resolveDocSrc(validSrc, href) : null;
            const internalHref = target ? `${srcHref(target.src)}${target.hash ? `#${target.hash}` : ''}` : null;
            // Anything relative that is not a page, like a source file, opens in the repository
            const linkHref = internalHref ?? (!isAnchor && !isExternal && validSrc ? new URL(href, REPO_DOCS_URL + validSrc).href : href);
            const opensAway = /^https?:/.test(linkHref ?? '');

            return (
                <a
                    href={linkHref}
                    target={opensAway ? '_blank' : undefined}
                    rel={opensAway ? 'noopener noreferrer' : undefined}
                    onClick={
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
        },
    }), [validSrc, goToHeading, navigate]);

    const accent = page ? SECTIONS[page.section].border : 'border-text';

    return (
        <div className="doc-page min-h-screen">
            <Navbar subbar={<DocBar headings={headings} onOpenPages={() => setPagesOpen(true)} onJump={goToHeading} />} />
            {pagesOpen && <PagesPanel current={page} onClose={() => setPagesOpen(false)} />}

            <div className="pt-[6.5rem] lg:pt-16">
                <div className="frame frame-wide lg:grid lg:grid-cols-[16.5rem_minmax(0,1fr)] xl:grid-cols-[16.5rem_minmax(0,1fr)_13.5rem]">
                    <aside className="hidden lg:block sticky top-16 self-start h-[calc(100vh-4rem)] overflow-y-auto py-7 px-5 border-r border-border [scrollbar-width:thin]">
                        <PageList current={page} variant="sidebar" />
                    </aside>

                    <main className="min-w-0 px-4 pt-6 pb-12 lg:px-12 lg:pt-9 lg:pb-16">
                        <Breadcrumb page={page} />

                        {loading && <p className="mt-6 label" role="status">{t('markdown.loading')}</p>}

                        {error && (
                            <div className="mt-6 max-w-[40rem] border-l-2 border-section-plugins pl-4">
                                <p className="font-bold">{t('markdown.error')}</p>
                                <p className="mt-1 text-text-muted">{error}</p>
                            </div>
                        )}

                        {!loading && !error && content && (
                            <>
                                {/* Every size and margin lives in `.markdown-body` in index.css. */}
                                <article className="markdown-body max-w-[52rem]">
                                    <ReactMarkdown
                                        remarkPlugins={REMARK_PLUGINS}
                                        rehypePlugins={REHYPE_PLUGINS}
                                        components={components}
                                    >
                                        {content}
                                    </ReactMarkdown>
                                </article>
                                {page && <PreviousNext page={page} />}
                                {validSrc && <SourceLinks src={validSrc} className="xl:hidden mt-8 flex gap-5 text-sm" />}
                            </>
                        )}
                    </main>

                    {validSrc && (
                        <aside className="hidden xl:block sticky top-16 self-start max-h-[calc(100vh-4rem)] overflow-y-auto py-9 pl-5 pr-6 border-l border-border [scrollbar-width:thin]">
                            <PageAside headings={headings} src={validSrc} accent={accent} onJump={goToHeading} />
                        </aside>
                    )}
                </div>
            </div>

            <Footer />
        </div>
    );
};

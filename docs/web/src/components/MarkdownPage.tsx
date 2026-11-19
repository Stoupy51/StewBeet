import { createContext, memo, useCallback, useContext, useEffect, useEffectEvent, useMemo, useRef, useState, isValidElement } from 'react';
import { flushSync } from 'react-dom';
import { useNavigate, useLocation, useNavigationType } from 'react-router-dom';
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
import { STACK_PALETTES, stackDiagramSvg } from './stackDiagram';
import { savedLanguage, useLanguage, type Language } from '../context/LanguageContext';
import { useTranslation } from '../i18n/useTranslation';
import { useMarkdownContent } from '../context/MarkdownContentContext';
import { PrehighlightedCode } from '../hooks/useShiki';
import { DOC_PAGES, SECTIONS, docHref, docSrc, findDocPage, hrefSrc, pageAt, srcHref } from '../docsPages';
import { markdownPageMeta } from '../utils/pageMeta';
import { headingTextToSlug, slugify } from '../utils/slugify';
import { metaValue, rehypeCodeTabs, rehypeSteps, rehypeTableLabels, remarkCodeMeta, textOf } from '../utils/docMarkdown';
import { readingPosition, restoreReadingPosition, withViewTransition, type TransitionKind } from '../utils/pageTransition';
import mediaSizes from '../generated/mediaSizes.json';

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
        video: ['src', 'poster', 'controls', 'loop', 'muted', 'playsInline', 'preload'],
        div: [...(defaultSchema.attributes?.div ?? []), ['className', 'markdown-alert', ...ALERT_TYPES.map((type) => `markdown-alert-${type}`)]],
        p: [...(defaultSchema.attributes?.p ?? []), ['className', 'markdown-alert-title']],
        code: [...(defaultSchema.attributes?.code ?? []), 'dataMeta'],
    },
};

const REMARK_PLUGINS: Options['remarkPlugins'] = [remarkGfm, remarkAlert, remarkCodeMeta];
const REHYPE_PLUGINS: Options['rehypePlugins'] = [rehypeRaw, [rehypeSanitize, MARKDOWN_SCHEMA], rehypeCodeTabs, rehypeSteps, rehypeTableLabels];

const DOC_SRC_PATTERN = /^(?:[A-Za-z0-9._-]+\/)*[A-Za-z0-9._-]+\.md$/;
const FETCH_TIMEOUT_MS = 7000;
/** How long to keep an anchor aligned while the layout above it settles. */
const SCROLL_SETTLE_MS = 4000;
/** Marks a fenced block: react-markdown puts the language on the <code>. */
const LANGUAGE_CLASS = /language-([A-Za-z0-9_-]+)/;
/** Where a relative link to something other than a page leads: the file in the repository. */
const REPO_DOCS_URL = 'https://github.com/Stoupy51/StewBeet/blob/main/docs/web/public/docs/';
/** The picture of the stack diagram, which a page shows as the live diagram, in its own colours. */
const STACK_PICTURE = /^\/img\/stack\/stewbeet-stack\.[a-z]{2}\.(?:dark|light)\.png$/;
const MEDIA_SIZES: Record<string, number[]> = mediaSizes;

function isValidDocSrc(src: string): boolean {
    return DOC_SRC_PATTERN.test(src) && !src.includes('..');
}

class DocNotFound extends Error {}

/** A page's markdown, and its code as scripts/highlight-docs.ts highlighted it. */
interface Doc {
    content: string;
    highlighted: Record<string, string>;
}

/** Every page asked for in this tab, by its path under public/docs: one seen or hovered once opens at once. */
const docs = new Map<string, Promise<Doc>>();

function loadDoc(src: string): Promise<Doc> {
    const cached = docs.get(src);
    if (cached) return cached;

    const signal = AbortSignal.timeout(FETCH_TIMEOUT_MS);
    const doc = Promise.all([
        fetch(`/docs/${src}`, { signal }).then(async (response) => {
            if (!response.ok) throw new DocNotFound();
            return (await response.text()).replace(/\r\n?/g, '\n');
        }),
        // Missing until the build step has run, and the browser then highlights the code itself
        fetch(`/highlighted/${src}.json`, { signal }).then((response) => (response.ok ? response.json() : {}), () => ({})),
    ]).then(([content, highlighted]) => ({ content, highlighted }));
    docs.set(src, doc);
    // A failed load is asked again next time
    doc.catch(() => docs.delete(src));
    return doc;
}

/** Where the reader left each page, for the back and forward buttons. */
const scrollPositions = new Map<string, number>();

const pageOrder = (src: string) => DOC_PAGES.findIndex((page) => page.src.en === src || page.src.fr === src);

/**
 * A view transition of the page column. The column is one element in both states, so the old
 * picture of it is moved by `--doc-shift`, how far the column moved on screen, and leaves from
 * where the reader saw it.
 */
function transitionDoc(main: HTMLElement | null, kind: TransitionKind, update: () => void): void {
    withViewTransition(kind, () => {
        const before = main?.getBoundingClientRect().top ?? 0;
        update();
        document.documentElement.style.setProperty('--doc-shift', `${before - (main?.getBoundingClientRect().top ?? 0)}px`);
    });
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

/**
 * A bare <a href="#id"> is a same-document jump: it fires hashchange, which the router does not
 * listen to, so useLocation().hash would never update and the page would never scroll. Going
 * through navigate() keeps both in sync.
 */
function useHeadingJump() {
    const navigate = useNavigate();
    const { hash, search } = useLocation();
    return useCallback((id: string) => (event: React.MouseEvent) => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        // Re-clicking the current heading leaves the hash untouched, so nothing else would scroll
        if (hash === `#${id}`) document.getElementById(id)?.scrollIntoView();
        else navigate({ search, hash: `#${id}` });
    }, [hash, navigate, search]);
}

/** The page the article shows, which its links and images resolve against. */
const ShownSrc = createContext('');

const DocLink = ({ href, children }: React.AnchorHTMLAttributes<HTMLAnchorElement>) => {
    const src = useContext(ShownSrc);
    const navigate = useNavigate();
    const jump = useHeadingJump();
    const isAnchor = href?.startsWith('#');
    const isExternal = !href || /^[a-z]+:/i.test(href);
    const target = !isAnchor && !isExternal ? resolveDocSrc(src, href) : null;
    const internalHref = target ? `${srcHref(target.src)}${target.hash ? `#${target.hash}` : ''}` : null;
    // Anything relative that is not a page, like a source file, opens in the repository
    const linkHref = internalHref ?? (!isAnchor && !isExternal ? new URL(href, REPO_DOCS_URL + src).href : href);
    const opensAway = /^https?:/.test(linkHref ?? '');

    return (
        <a
            href={linkHref}
            target={opensAway ? '_blank' : undefined}
            rel={opensAway ? 'noopener noreferrer' : undefined}
            onClick={
                isAnchor && href ? jump(decodeURIComponent(href.slice(1)))
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
};

/** beet, bolt, mecha and StewBeet in the page's colours, building itself up when it appears. A span, since markdown puts it in a paragraph. */
const StackDiagram = () => {
    const { language } = useTranslation();
    const svg = useMemo(() => stackDiagramSvg({ language, palette: STACK_PALETTES.page, autoplay: true }), [language]);
    return <span className="stack-diagram block border border-border [&>svg]:block [&>svg]:w-full [&>svg]:h-auto" dangerouslySetInnerHTML={{ __html: svg }} />;
};

/** Images keep the size of their box from the first frame, read by scripts/build-media-sizes.ts. */
const DocImage = ({ src: imageSrc, alt, width, height }: React.ImgHTMLAttributes<HTMLImageElement>) => {
    const src = useContext(ShownSrc);
    // Relative images are served by this site, beside the page that shows them
    const resolved = imageSrc && !/^https?:/.test(imageSrc) ? new URL(imageSrc, `https://site/docs/${src}`).pathname : imageSrc ?? '';
    if (STACK_PICTURE.test(resolved)) return <StackDiagram />;

    const [knownWidth, knownHeight] = MEDIA_SIZES[resolved] ?? [];
    return (
        <ZoomableImage
            src={resolved}
            alt={alt ?? ''}
            width={width ?? knownWidth}
            height={height ?? knownHeight}
            frameClassName="max-w-full align-top"
            className="max-w-full h-auto"
        />
    );
};

const DocVideo = ({ src, poster, controls, loop, muted, playsInline, preload }: React.VideoHTMLAttributes<HTMLVideoElement>) => {
    const [width, height] = MEDIA_SIZES[src ?? ''] ?? [];
    return <video src={src} poster={poster} controls={controls} loop={loop} muted={muted} playsInline={playsInline} preload={preload} width={width} height={height} />;
};

/** Defined once for every page, so moving to another page never remounts the one still on screen. */
const COMPONENTS: Components = {
    h1: makeHeading('h1'),
    h2: makeHeading('h2'),
    h3: makeHeading('h3'),
    h4: makeHeading('h4'),
    h5: makeHeading('h5'),
    h6: makeHeading('h6'),
    pre: ({ node, style }) => (node ? <CodeBlock {...fencedCode(node)} style={style} /> : null),
    div: ({ node, ...props }) => {
        if (node?.properties.dataTabs === undefined) return <div {...props} />;
        const tabs = node.children
            .filter((child): child is Element => child.type === 'element' && child.tagName === 'pre')
            .map((pre) => {
                const { code, language, meta } = fencedCode(pre);
                return { code, language, label: metaValue(meta, 'tab') ?? language };
            });
        return <CodeTabs tabs={tabs} style={props.style} />;
    },
    img: DocImage,
    video: DocVideo,
    a: DocLink,
};

/** The page's markdown, parsed again only when its text changes. Every size and margin lives in `.markdown-body` in index.css. */
const DocArticle = memo(({ src, content, highlighted }: Doc & { src: string }) => (
    <ShownSrc value={src}>
        <PrehighlightedCode value={highlighted}>
            <article className="markdown-body max-w-[52rem]">
                <ReactMarkdown remarkPlugins={REMARK_PLUGINS} rehypePlugins={REHYPE_PLUGINS} components={COMPONENTS}>
                    {content}
                </ReactMarkdown>
            </article>
        </PrehighlightedCode>
    </ShownSrc>
));
DocArticle.displayName = 'DocArticle';

/** The page on screen. It stays there until the next one is ready, then a view transition swaps them. */
interface ShownDoc extends Doc {
    /** Null until the first page arrives. */
    src: string | null;
    error: 'notFound' | 'unreachable' | null;
}

export const MarkdownPage: React.FC = () => {
    const { pathname, hash } = useLocation();
    const navigate = useNavigate();
    const navigationType = useNavigationType();
    const { language, setLanguage } = useLanguage();
    const { t } = useTranslation();
    const goToHeading = useHeadingJump();
    const main = useRef<HTMLElement>(null);
    const requested = pageAt(pathname);
    const validSrc = requested ? docSrc(requested.page, requested.language) : null;
    const prerendered = useMarkdownContent();
    // Only for the page server.tsx rendered: once the reader moves on, the embedded markdown belongs to another page
    const [shown, setShown] = useState<ShownDoc>(() => prerendered?.src === validSrc
        ? { ...prerendered, error: null }
        : { src: null, content: '', highlighted: {}, error: null });
    const [pagesOpen, setPagesOpen] = useState(false);
    const page = shown.src ? findDocPage(shown.src) : undefined;
    const pending = validSrc !== null && validSrc !== shown.src;

    useEffect(() => {
        if (prerendered) docs.set(prerendered.src, Promise.resolve(prerendered));
    }, [prerendered]);

    // The address follows the reader's language, without a history entry, or Back would switch it back
    const requestedHref = requested && docHref(requested.page, language);
    useEffect(() => {
        if (requestedHref && requestedHref !== pathname) navigate(requestedHref, { replace: true });
    }, [requestedHref, pathname, navigate]);

    const isShown = useEffectEvent((src: string) => src === shown.src);
    const showDoc = useEffectEvent((next: ShownDoc & { src: string }) => {
        const leaving = shown.src;
        if (leaving === null) {
            setShown(next);
            return;
        }

        scrollPositions.set(leaving, window.scrollY);
        const leavingPage = findDocPage(leaving);
        // The same page in another language: the reader stays where they were
        const position = leavingPage && leavingPage === findDocPage(next.src) ? readingPosition() : null;
        const restored = navigationType === 'POP' && !hash ? scrollPositions.get(next.src) : undefined;
        const kind = pagesOpen ? 'panel' : position ? 'language' : pageOrder(next.src) < pageOrder(leaving) ? 'back' : 'forward';

        transitionDoc(main.current, kind, () => {
            flushSync(() => {
                setShown(next);
                setPagesOpen(false);
            });
            if (position) restoreReadingPosition(position);
            else if (restored !== undefined) window.scrollTo({ top: restored, behavior: 'instant' });
            else if (hash) document.getElementById(decodeURIComponent(hash.slice(1)))?.scrollIntoView({ behavior: 'instant' });
            else window.scrollTo({ top: 0, behavior: 'instant' });
        });
    });

    useEffect(() => {
        if (!validSrc || isShown(validSrc)) return;

        let stale = false;
        loadDoc(validSrc).then(
            (doc) => !stale && showDoc({ src: validSrc, ...doc, error: null }),
            (error) => !stale && showDoc({ src: validSrc, content: '', highlighted: {}, error: error instanceof DocNotFound ? 'notFound' : 'unreachable' }),
        );
        return () => {
            stale = true;
        };
    }, [validSrc]);

    // The text, the menus and the address all change in one transition, and the reader keeps their place
    const changeLanguage = async (next: Language) => {
        const nextSrc = page ? docSrc(page, next) : null;
        const doc = nextSrc ? await loadDoc(nextSrc).catch(() => null) : null;
        const position = readingPosition();
        transitionDoc(main.current, 'language', () => {
            flushSync(() => {
                setLanguage(next);
                if (nextSrc && doc) setShown({ src: nextSrc, ...doc, error: null });
            });
            restoreReadingPosition(position);
        });
    };

    // A reader who picked a language and opens the page in the other one, from a link someone posted, is moved to theirs
    const openInReaderLanguage = useEffectEvent(() => {
        const chosen = savedLanguage();
        if (chosen && chosen !== language) changeLanguage(chosen);
    });
    useEffect(() => openInReaderLanguage(), []);

    // A page is fetched when the pointer rests on a link to it, or when the link is pressed or focused
    useEffect(() => {
        let hover = 0;
        const prefetch = (target: EventTarget | null) => {
            const link = target instanceof Element ? target.closest('a') : null;
            const linked = link && link.origin === window.location.origin ? hrefSrc(link.pathname + link.search) : null;
            if (linked && isValidDocSrc(linked)) loadDoc(linked).catch(() => undefined);
        };
        const onOver = (event: Event) => {
            window.clearTimeout(hover);
            hover = window.setTimeout(() => prefetch(event.target), 60);
        };
        const onPress = (event: Event) => prefetch(event.target);

        document.addEventListener('pointerover', onOver, { passive: true });
        document.addEventListener('pointerdown', onPress, { passive: true });
        document.addEventListener('focusin', onPress);
        return () => {
            window.clearTimeout(hover);
            document.removeEventListener('pointerover', onOver);
            document.removeEventListener('pointerdown', onPress);
            document.removeEventListener('focusin', onPress);
        };
    }, []);

    // The browser would scroll the page still on screen to where the next one was left, before it
    // arrives. Leaving the site gives it the job back, so a reload lands where the reader was.
    useEffect(() => {
        const restoreByBrowser = () => {
            history.scrollRestoration = 'auto';
        };
        history.scrollRestoration = 'manual';
        window.addEventListener('pagehide', restoreByBrowser);
        return () => {
            window.removeEventListener('pagehide', restoreByBrowser);
            restoreByBrowser();
        };
    }, []);

    // The H2s, for "On this page": deeper levels would turn a long guide's list into a second page.
    const headings = useMemo<TocHeading[]>(() => {
        const withoutCode = shown.content.replace(/```[\s\S]*?```/g, '');
        return [...withoutCode.matchAll(/^##\s+(.+)$/gm)].map(([, text]) => ({
            id: headingTextToSlug(text.trim()),
            text: text.replace(/<[^>]*>/g, '').replace(/\*\*|`/g, '').trim(),
        }));
    }, [shown.content]);

    // Scroll to the heading targeted by the URL hash (search results, shared links) once its page is shown.
    useEffect(() => {
        if (!hash || shown.src !== validSrc) return;

        const id = decodeURIComponent(hash.slice(1));
        const scroll = () => document.getElementById(id)?.scrollIntoView();
        scroll();

        // Fonts and late images can still change the height above the heading. Re-align on each
        // layout change until it settles, or a deep anchor lands short.
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
    }, [hash, shown.src, validSrc]);

    // Same title as the one server.tsx writes into the head
    useEffect(() => {
        document.title = markdownPageMeta(shown.src, shown.content).title;
        return () => {
            document.title = 'StewBeet';
        };
    }, [shown.src, shown.content]);

    const accent = page ? SECTIONS[page.section].border : 'border-text';
    const error = !validSrc ? t('markdown.noPage') : shown.error && t(`markdown.${shown.error}`);

    return (
        <div className="doc-page min-h-screen">
            <Navbar subbar={<DocBar headings={headings} onOpenPages={() => setPagesOpen(true)} onJump={goToHeading} />} onLanguageChange={changeLanguage} />
            {pagesOpen && <PagesPanel current={page} onClose={() => setPagesOpen(false)} />}
            {pending && <div className="doc-progress" aria-hidden="true" />}

            <div className="pt-[6.5rem] lg:pt-16">
                <div className="frame frame-wide lg:grid lg:grid-cols-[16.5rem_minmax(0,1fr)] xl:grid-cols-[16.5rem_minmax(0,1fr)_13.5rem]">
                    <aside className="hidden lg:block sticky top-16 self-start h-[calc(100vh-4rem)] overflow-y-auto py-7 px-5 border-r border-border [scrollbar-width:thin]">
                        <PageList current={page} variant="sidebar" />
                    </aside>

                    <main ref={main} aria-busy={pending} className="doc-main min-w-0 px-4 pt-6 pb-12 lg:px-12 lg:pt-9 lg:pb-16">
                        <Breadcrumb page={page} />

                        {error ? (
                            <div className="mt-6 max-w-[40rem] border-l-2 border-section-plugins pl-4">
                                <p className="font-bold">{t('markdown.error')}</p>
                                <p className="mt-1 text-text-muted">{error}</p>
                            </div>
                        ) : shown.src === null ? (
                            <p className="mt-6 label" role="status">{t('markdown.loading')}</p>
                        ) : (
                            <>
                                <DocArticle src={shown.src} content={shown.content} highlighted={shown.highlighted} />
                                {page && <PreviousNext page={page} />}
                                <SourceLinks src={shown.src} className="xl:hidden mt-8 flex gap-5 text-sm" />
                            </>
                        )}
                    </main>

                    {shown.src && (
                        <aside className="hidden xl:block sticky top-16 self-start max-h-[calc(100vh-4rem)] overflow-y-auto py-9 pl-5 pr-6 border-l border-border [scrollbar-width:thin]">
                            <PageAside headings={headings} src={shown.src} accent={accent} onJump={goToHeading} />
                        </aside>
                    )}
                </div>
            </div>

            <Footer />
        </div>
    );
};

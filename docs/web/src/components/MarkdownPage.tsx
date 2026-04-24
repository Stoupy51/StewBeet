import { useEffect, useState, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';
import { motion, AnimatePresence } from 'framer-motion';
import { HiArrowLeft, HiExternalLink, HiMenu, HiX } from 'react-icons/hi';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { useLanguage } from '../context/LanguageContext';
import { useMarkdownContent } from '../context/MarkdownContentContext';

interface Heading {
    id: string;
    text: string;
    level: number;
}

export const MarkdownPage: React.FC = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();
    const { language } = useLanguage();
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
    
    const handleBack = () => {
        // Check if there's history to go back to
        if (window.history.length > 1) {
            navigate(-1);
        } else {
            // No history, go to plugins section
            navigate('/#plugins');
        }
    };
    
    // Determine if src is a full URL or a relative path
    const isFullUrl = src?.startsWith('http');
    
    // Construct the full URL
    const fullUrl = isFullUrl 
        ? src 
        : src ? `https://github.com/Stoupy51/StewBeet/blob/main/docs/${src}` : null;
    
    // Convert to raw URL for fetching
    const rawUrl = fullUrl
        ? fullUrl
            .replace('github.com/', 'raw.githubusercontent.com/')
            .replace('/blob/', '/')
            .replace('/raw/refs/heads/', '/')
        : null;
    
    // Extract the base path for relative links (directory containing the markdown file)
    const basePath = rawUrl
        ? rawUrl.substring(0, rawUrl.lastIndexOf('/'))
        : null;

    // Extract headings for table of contents
    const headings = useMemo(() => {
        if (!content) return [];
        
        // Remove code blocks first to avoid matching # inside them
        const contentWithoutCodeBlocks = content.replace(/```[\s\S]*?```/g, '');
        
        const headingRegex = /^(#{1,6})\s+(.+)$/gm;
        const matches: Heading[] = [];
        let match;
        const pluginName = src ? src.replace('.md', '') : 'Plugin';
        
        while ((match = headingRegex.exec(contentWithoutCodeBlocks)) !== null) {
            const level = match[1].length;
            let text = match[2].trim();
            
            // Remove HTML tags from text
            text = text.replace(/<[^>]*>/g, '');
            
            // Remove markdown bold markers
            text = text.replace(/\*\*/g, '');
            
            // Replace first heading (plugin name) with shorter version but keep emoji
            if (matches.length === 0 && level === 1) {
                // Extract emoji from the beginning (if exists)
                const emojiMatch = text.match(/^(\p{Emoji_Presentation}|\p{Extended_Pictographic})\s*/u);
                const emoji = emojiMatch ? emojiMatch[0] : '';
                text = emoji + pluginName;
            }
            
            const id = text
                .toLowerCase()
                .replace(/[^\w\s-]/g, '')
                .replace(/\s+/g, '-');
            
            matches.push({ id, text, level });
        }
        
        return matches;
    }, [content, src]);

    useEffect(() => {
        if (!src) {
            setError('No plugin specified. Please provide a "src" parameter.');
            setLoading(false);
            return;
        }

        const fetchMarkdown = async () => {
            setLoading(true);
            setError(null);
            
            try {
                if (!rawUrl) {
                    throw new Error('Invalid source URL');
                }
                    
                const response = await fetch(rawUrl);
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch plugin documentation (${response.status})`);
                }
                
                const text = await response.text();
                setContent(text);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load plugin documentation');
            } finally {
                setLoading(false);
            }
        };

        fetchMarkdown();
    }, [src, rawUrl]);

    // Set page title
    useEffect(() => {
        let pluginName = 'Plugin';
        
        if (src) {
            if (isFullUrl) {
                // Extract filename from URL
                const filename = src.split('/').pop() || 'Plugin';
                pluginName = filename.replace('.md', '');
            } else {
                pluginName = src.replace('.md', '');
            }
        }
        
        document.title = `${pluginName} | StewBeet`;
        
        // Reset title when component unmounts
        return () => {
            document.title = 'StewBeet';
        };
    }, [src, isFullUrl]);

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-indigo-500/30">
            <Navbar />
            
            {/* Background decoration */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-20 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-[120px]" />
                <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-[120px]" />
            </div>

            {/* Header with back button */}
            <div className="sticky top-16 z-30 border-b border-white/10 bg-slate-950/80 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-4 py-6 flex items-center justify-between">
                    <button
                        onClick={handleBack}
                        className="flex items-center gap-2 text-indigo-400 hover:text-indigo-300 transition-colors group"
                    >
                        <HiArrowLeft className="text-xl group-hover:-translate-x-1 transition-transform" />
                        <span className="font-medium">Back</span>
                    </button>
                    
                    <div className="flex items-center gap-4">
                        {headings.length > 0 && (
                            <button
                                onClick={() => setTocOpen(!tocOpen)}
                                className="flex items-center gap-2 px-4 py-2 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 hover:text-indigo-300 rounded-lg transition-all border border-indigo-500/30 lg:hidden"
                            >
                                <HiMenu className="text-xl" />
                                <span className="text-sm font-medium">Contents</span>
                            </button>
                        )}
                        {fullUrl && (
                            <a
                                href={fullUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 text-slate-400 hover:text-slate-200 transition-colors text-sm group"
                            >
                                <span>View on GitHub</span>
                                <HiExternalLink className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                            </a>
                        )}
                    </div>
                </div>
            </div>

            {/* Content */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="relative z-10 max-w-7xl mx-auto px-4 py-16"
            >
                <div className="flex gap-8 items-start">
                    {/* Table of Contents - Desktop */}
                    {headings.length > 0 && (
                        <aside className="hidden lg:block sticky top-24 w-64 shrink-0 self-start max-h-[calc(100vh-7rem)] overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
                            <div className="bg-slate-900/30 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                                <h3 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2 sticky top-0 bg-slate-900/30 backdrop-blur-sm -mx-6 px-6 pb-4">
                                    <HiMenu className="text-indigo-400" />
                                    Contents
                                </h3>
                                <nav className="space-y-2">
                                    {headings.map((heading, idx) => (
                                        <a
                                            key={idx}
                                            href={`#${heading.id}`}
                                            className={`block text-sm hover:text-indigo-400 transition-colors ${
                                                heading.level === 1 ? 'font-semibold text-slate-300' :
                                                heading.level === 2 ? 'pl-4 text-slate-400' :
                                                'pl-8 text-slate-500'
                                            }`}
                                            onClick={() => setTocOpen(false)}
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
                        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
                    </div>
                )}

                {error && (
                    <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-8 text-center backdrop-blur-sm">
                        <p className="text-red-400 text-xl font-bold mb-3">Error</p>
                        <p className="text-slate-300 text-lg">{error}</p>
                    </div>
                )}

                {!loading && !error && content && (
                    <div className="bg-slate-900/30 backdrop-blur-sm border border-white/10 rounded-2xl p-8 md:p-12 shadow-2xl">
                        <article className="prose prose-invert prose-slate prose-lg max-w-none
                            prose-headings:font-bold prose-headings:scroll-mt-32
                            prose-h1:text-3xl prose-h1:mb-6 prose-h1:bg-clip-text prose-h1:text-transparent prose-h1:bg-gradient-to-r prose-h1:from-indigo-200 prose-h1:to-purple-200 prose-h1:border-b-2 prose-h1:border-white/20 prose-h1:pb-4
                            prose-h2:text-2xl prose-h2:mt-12 prose-h2:mb-5 prose-h2:text-indigo-100 prose-h2:border-b prose-h2:border-white/10 prose-h2:pb-2
                            prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-3 prose-h3:text-slate-200
                            prose-h4:text-xl prose-h4:mt-8 prose-h4:mb-3 prose-h4:text-slate-300
                            prose-h5:text-lg prose-h5:mt-6 prose-h5:mb-2 prose-h5:text-slate-300
                            prose-h6:text-base prose-h6:mt-4 prose-h6:mb-2 prose-h6:text-slate-400
                            prose-p:text-slate-300 prose-p:leading-relaxed prose-p:my-4
                            prose-a:text-indigo-400 prose-a:no-underline hover:prose-a:text-indigo-300 hover:prose-a:underline prose-a:underline-offset-4 prose-a:transition-colors
                            prose-code:text-indigo-300 prose-code:bg-slate-800/50 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-sm prose-code:font-medium prose-code:before:content-none prose-code:after:content-none
                            prose-pre:bg-slate-900/90 prose-pre:border prose-pre:border-white/10 prose-pre:rounded-xl prose-pre:shadow-xl prose-pre:my-6
                            prose-strong:text-slate-100 prose-strong:font-bold
                            prose-em:text-slate-300 prose-em:italic
                            prose-ul:my-6 prose-ul:text-slate-300 prose-ol:my-6 prose-ol:text-slate-300
                            prose-li:my-2 prose-li:marker:text-indigo-400
                            prose-blockquote:border-l-4 prose-blockquote:border-l-indigo-500 prose-blockquote:bg-indigo-500/5 prose-blockquote:py-2 prose-blockquote:px-6 prose-blockquote:my-6 prose-blockquote:rounded-r-lg prose-blockquote:text-slate-300 prose-blockquote:italic
                            prose-img:rounded-xl prose-img:border prose-img:border-white/20 prose-img:shadow-2xl prose-img:my-8
                            prose-table:border prose-table:border-white/10 prose-table:rounded-lg prose-table:overflow-hidden prose-table:my-8
                            prose-thead:bg-slate-800/50 prose-thead:border-b-2 prose-thead:border-white/20
                            prose-th:text-slate-200 prose-th:font-bold prose-th:px-6 prose-th:py-4 prose-th:text-left
                            prose-td:text-slate-300 prose-td:px-6 prose-td:py-4 prose-td:border-t prose-td:border-white/10
                            prose-hr:border-white/20 prose-hr:border-t-2 prose-hr:my-12"
                        >
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            rehypePlugins={[rehypeRaw, rehypeSanitize]}
                            components={{
                                code({ inline, className, children, style: _style, ...props }: React.HTMLAttributes<HTMLElement> & { inline?: boolean }) {
                                    const match = /language-(\w+)/.exec(className || '');
                                    const language = match ? match[1] : '';
                                    
                                    return !inline && language ? (
                                        <SyntaxHighlighter
                                            style={vscDarkPlus}
                                            language={language}
                                            PreTag="div"
                                            {...props}
                                        >
                                            {String(children).replace(/\n$/, '')}
                                        </SyntaxHighlighter>
                                    ) : (
                                        <code className={className} {...props}>
                                            {children}
                                        </code>
                                    );
                                },
                                h1: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => {
                                    const id = String(children)
                                        .toLowerCase()
                                        .replace(/[^\w\s-]/g, '')
                                        .replace(/\s+/g, '-');
                                    return <h1 id={id} {...props}>{children}</h1>;
                                },
                                h2: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => {
                                    const id = String(children)
                                        .toLowerCase()
                                        .replace(/[^\w\s-]/g, '')
                                        .replace(/\s+/g, '-');
                                    return <h2 id={id} {...props}>{children}</h2>;
                                },
                                h3: ({ children, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => {
                                    const id = String(children)
                                        .toLowerCase()
                                        .replace(/[^\w\s-]/g, '')
                                        .replace(/\s+/g, '-');
                                    return <h3 id={id} {...props}>{children}</h3>;
                                },
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
                                    let linkHref = href;
                                    
                                    if (!isAnchor && !isExternal && href && basePath) {
                                        // Convert basePath from raw.githubusercontent to github.com/blob format
                                        const viewBasePath = basePath.replace(
                                            'https://raw.githubusercontent.com/',
                                            'https://github.com/'
                                        ).replace('/main/', '/blob/main/');
                                        
                                        linkHref = `${viewBasePath}/${href}`;
                                    }
                                    
                                    return (
                                        <a
                                            href={linkHref}
                                            target={isExternal ? '_blank' : undefined}
                                            rel={isExternal ? 'noopener noreferrer' : undefined}
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
                                        <HiMenu className="text-indigo-400" />
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
                                            className={`block text-sm hover:text-indigo-400 transition-colors ${
                                                heading.level === 1 ? 'font-semibold text-slate-300' :
                                                heading.level === 2 ? 'pl-4 text-slate-400' :
                                                'pl-8 text-slate-500'
                                            }`}
                                            onClick={() => setTocOpen(false)}
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

import { EYEBROW } from '../theme';

/**
 * The top of every page that is not the home page: a mono label, the title, one lead paragraph.
 * `width` is the container of the page below it, so the header's left edge lines up with the content.
 */
export const PageHeader = ({ eyebrow, title, lead, width = 'max-w-page' }: {
    eyebrow: string;
    title: string;
    lead?: React.ReactNode;
    width?: string;
}) => (
    <header className={`${width} mx-auto px-4 sm:px-6 pt-28 md:pt-32 pb-10`}>
        <p className={EYEBROW}>{eyebrow}</p>
        <h1 className="mt-4 text-4xl md:text-5xl font-semibold tracking-tight text-ink-50 text-balance">{title}</h1>
        {lead && <p className="mt-4 max-w-2xl text-base md:text-lg text-ink-300 leading-relaxed text-pretty">{lead}</p>}
    </header>
);

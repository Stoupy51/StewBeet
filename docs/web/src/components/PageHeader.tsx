/**
 * The top of every page that is not the home page: the title and one lead paragraph.
 * `width` is the container of the page below it, so the header's left edge lines up with the content.
 */
export const PageHeader = ({ title, lead, width = 'max-w-page' }: {
    title: string;
    lead?: React.ReactNode;
    width?: string;
}) => (
    <header className={`${width} mx-auto px-4 sm:px-6 pt-28 md:pt-32 pb-10`}>
        <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-ink-50 text-balance">{title}</h1>
        {lead && <p className="mt-4 max-w-2xl text-base md:text-lg text-ink-300 leading-relaxed text-pretty">{lead}</p>}
    </header>
);

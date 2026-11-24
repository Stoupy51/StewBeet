/**
 * The top of every page that is not the home page or a doc page: the title and one lead paragraph,
 * in the frame the sections below it continue. `wide` matches the frame of the tool pages.
 */
export const PageHeader = ({ title, lead, wide = false }: {
    title: string;
    lead?: React.ReactNode;
    wide?: boolean;
}) => (
    <header className={`frame ${wide ? 'frame-wide' : ''} px-4 pt-[5.5rem] pb-10 lg:px-12 lg:pt-32`}>
        <h1 className="text-[2.25rem] lg:text-[3.25rem] leading-[1.12] font-bold text-balance">{title}</h1>
        {lead && <p className="mt-4 max-w-[40rem] text-text-muted text-pretty">{lead}</p>}
    </header>
);

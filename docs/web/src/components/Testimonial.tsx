import { useTranslation } from '../i18n/useTranslation';

/** A user's own words, trimmed and never rewritten, placed right after the "New to Python?" worry it answers. */
export const Testimonial = () => {
    const { t } = useTranslation();
    const translated = t('testimonial.translated');

    return (
        <section className="frame px-4 pt-2 pb-12 lg:px-12 lg:pt-0 lg:pb-16">
            <figure className="pt-5 border-t border-border max-w-[40rem]">
                <blockquote className="text-[1.0625rem] lg:text-[1.1875rem] leading-normal text-pretty">{t('testimonial.casperQuote')}</blockquote>
                <figcaption className="mt-3.5 flex items-center gap-2.5 text-sm text-text-muted">
                    <img src="/testimonials/casper2137.webp" alt="" width={36} height={36} className="w-9 h-9 rounded-full flex-shrink-0" />
                    <span>
                        <strong className="font-semibold text-text">Casper2137</strong>, {t('testimonial.casperCaption')}
                        {translated && <span> ({translated})</span>}
                    </span>
                </figcaption>
            </figure>
        </section>
    );
};

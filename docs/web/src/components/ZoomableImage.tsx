import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { HiX } from 'react-icons/hi';

export interface LightboxImage {
    src: string;
    alt: string;
    /** Scales with nearest-neighbour, for pixel art. */
    pixelated?: boolean;
}

/**
 * The image blown up to fill the screen. Closes on a click anywhere or on Escape.
 * Portalled to <body>, since a card that clips or transforms its content would trap a fixed overlay.
 */
export const ImageLightbox = ({ image, onClose }: { image: LightboxImage | null; onClose: () => void }) => {
    useEffect(() => {
        if (!image) return;
        const closeOnEscape = (event: KeyboardEvent) => {
            if (event.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', closeOnEscape);
        return () => window.removeEventListener('keydown', closeOnEscape);
    }, [image, onClose]);

    // No document while prerendering, and nothing to show until a click anyway
    if (typeof document === 'undefined') return null;

    return createPortal(
        <AnimatePresence>
            {image && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.1 }}
                    onClick={onClose}
                    role="dialog"
                    aria-modal="true"
                    aria-label={image.alt}
                    className="fixed inset-0 z-[70] flex items-center justify-center bg-black/85 p-4 cursor-zoom-out"
                >
                    <button
                        onClick={onClose}
                        autoFocus
                        className="absolute top-4 right-4 p-2 rounded-control bg-ink-900 border border-ink-700 hover:border-ink-500 text-ink-100 transition-colors"
                        aria-label="Close"
                    >
                        <HiX className="text-2xl" />
                    </button>
                    <motion.img
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        transition={{ duration: 0.15, ease: 'easeOut' }}
                        src={image.src}
                        alt={image.alt}
                        // Width and height both at the limit, so a small image is scaled up and not only centred
                        className={`w-full h-full max-w-7xl max-h-[90vh] object-contain rounded-panel ${image.pixelated ? 'pixelated' : ''}`}
                    />
                </motion.div>
            )}
        </AnimatePresence>,
        document.body,
    );
};

interface ZoomableImageProps extends LightboxImage {
    /** On the button wrapping the image, which takes the image's place in the layout. */
    frameClassName?: string;
    className?: string;
    loading?: 'lazy' | 'eager';
}

/** An image that opens in the lightbox when clicked. */
export const ZoomableImage = ({ src, alt, pixelated, frameClassName = '', className = '', loading }: ZoomableImageProps) => {
    const [open, setOpen] = useState(false);
    return (
        <>
            <button type="button" onClick={() => setOpen(true)} aria-label={alt} className={`cursor-zoom-in ${frameClassName}`}>
                <img src={src} alt={alt} loading={loading} decoding="async" className={className} />
            </button>
            <ImageLightbox image={open ? { src, alt, pixelated } : null} onClose={() => setOpen(false)} />
        </>
    );
};

/**
 * One pane of highlighted source, with a way back to the tree it was picked from.
 *
 * Shared by /playground and /auto_headers: both show a file tree on one side and one file at a
 * time on the other, and a reader moving between the two tools should not find the same pane
 * behaving differently in each.
 */
import { HiArrowLeft } from 'react-icons/hi';
import { useShiki } from '../hooks/useShiki';

/** Checkerboard behind transparent PNGs, drawn with a gradient so it costs no request. */
const CHECKERBOARD =
    'bg-[linear-gradient(45deg,#1a1a1a_25%,transparent_25%),linear-gradient(-45deg,#1a1a1a_25%,transparent_25%),linear-gradient(45deg,transparent_75%,#1a1a1a_75%),linear-gradient(-45deg,transparent_75%,#1a1a1a_75%)] bg-[length:16px_16px] bg-[position:0_0,0_8px,8px_-8px,-8px_0]';

interface SourceViewProps {
    /** Full path of the file, shown on the right of the bar. */
    label: string;
    body: string;
    language: string;
    /** Base64 PNG. When present the body is ignored and the image is shown instead. */
    image?: string;
    alt?: string;
    onBack: () => void;
    backLabel: string;
}

export const SourceView: React.FC<SourceViewProps> = ({ label, body, language, image, alt, onBack, backLabel }) => {
    const html = useShiki(image ? '' : body, language);

    return (
        <div className="flex-1 flex flex-col min-h-0">
            <div className="flex items-center gap-2 px-4 py-2 border-b border-white/5">
                <button
                    onClick={onBack}
                    className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 transition-colors"
                >
                    <HiArrowLeft className="w-3 h-3" /> {backLabel}
                </button>
                <code className="ml-auto text-[0.7rem] text-slate-500 truncate">{label}</code>
            </div>

            <div className="flex-1 overflow-auto custom-scrollbar p-4">
                {image ? (
                    <div className={`inline-block p-4 rounded ${CHECKERBOARD}`}>
                        <img
                            src={`data:image/png;base64,${image}`}
                            alt={alt ?? label}
                            className="w-32 h-32 object-contain [image-rendering:pixelated]"
                        />
                    </div>
                ) : (
                    <div
                        className="text-[0.75rem] leading-[1.55] [&_pre]:!bg-transparent [&_pre]:whitespace-pre"
                        dangerouslySetInnerHTML={{ __html: html }}
                    />
                )}
            </div>
        </div>
    );
};

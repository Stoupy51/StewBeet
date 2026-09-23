import { useState } from 'react';

/** Copies text and reports `copied` for two seconds, long enough to confirm without lingering. */
export function useClipboard(): [boolean, (text: string) => void] {
    const [copied, setCopied] = useState(false);
    const copy = (text: string) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };
    return [copied, copy];
}

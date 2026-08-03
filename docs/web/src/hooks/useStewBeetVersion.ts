import { useState, useEffect } from 'react';

interface GitHubTag {
    name: string;
}

/** Shown when the unauthenticated GitHub tags API is unreachable or rate-limited. Keep in sync with python_package/pyproject.toml. */
const FALLBACK_VERSION = '3.5.8';

// Module-level cache so only one fetch is made regardless of how many components call the hook
let cachedVersion: string | null = null;
let pendingFetch: Promise<string> | null = null;

const fetchOnce = (): Promise<string> => {
    if (cachedVersion !== null) return Promise.resolve(cachedVersion);
    if (pendingFetch) return pendingFetch;
    pendingFetch = fetch('https://api.github.com/repos/Stoupy51/StewBeet/tags')
        .then(r => r.json() as Promise<GitHubTag[]>)
        .then(data => {
            if (data && data.length > 0) {
                const tagName = data[0].name;
                cachedVersion = tagName.startsWith('v') ? tagName.slice(1) : tagName;
            } else {
                cachedVersion = FALLBACK_VERSION;
            }
            return cachedVersion;
        })
        .catch(() => {
            cachedVersion = FALLBACK_VERSION;
            return cachedVersion;
        });
    return pendingFetch;
};

export const useStewBeetVersion = () => {
    const [version, setVersion] = useState<string>(cachedVersion ?? FALLBACK_VERSION);
    const [loading, setLoading] = useState<boolean>(cachedVersion === null);

    useEffect(() => {
        if (cachedVersion !== null) return;
        fetchOnce().then(v => {
            setVersion(v);
            setLoading(false);
        });
    }, []);

    return { version, loading };
};

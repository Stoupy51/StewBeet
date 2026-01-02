import { useState, useEffect } from 'react';

interface GitHubTag {
    name: string;
}

export const useStewBeetVersion = () => {
    const [version, setVersion] = useState<string>('3.0.0'); // Fallback version
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchVersion = async () => {
            try {
                const response = await fetch('https://api.github.com/repos/Stoupy51/StewBeet/tags');
                const data: GitHubTag[] = await response.json();
                if (data && data.length > 0) {
                    // Remove 'v' prefix if present
                    const tagName = data[0].name;
                    setVersion(tagName.startsWith('v') ? tagName.slice(1) : tagName);
                }
            } catch (error) {
                console.error('Failed to fetch StewBeet version:', error);
                // Keep fallback version
            } finally {
                setLoading(false);
            }
        };

        fetchVersion();
    }, []);

    return { version, loading };
};

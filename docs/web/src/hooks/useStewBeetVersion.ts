import { useState, useEffect } from 'react';

interface PyPIResponse {
    info: {
        version: string;
    };
}

export const useStewBeetVersion = () => {
    const [version, setVersion] = useState<string>('3.0.0'); // Fallback version
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        const fetchVersion = async () => {
            try {
                const response = await fetch('https://pypi.org/pypi/stewbeet/json');
                const data: PyPIResponse = await response.json();
                setVersion(data.info.version);
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

import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

const HomePage = lazy(() => import('./components/HomePage'));
const MarkdownPage = lazy(() => import('./components/MarkdownPage').then(m => ({ default: m.MarkdownPage })));
const DocumentationPage = lazy(() => import('./components/DocumentationPage').then(m => ({ default: m.DocumentationPage })));
const MarkdownToBBCodePage = lazy(() => import('./components/MarkdownToBBCodePage').then(m => ({ default: m.MarkdownToBBCodePage })));
const ToolsPage = lazy(() => import('./components/ToolsPage').then(m => ({ default: m.ToolsPage })));

export function AppRoutes() {
    return (
        <Suspense fallback={null}>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/documentation" element={<DocumentationPage />} />
                <Route path="/markdown" element={<MarkdownPage />} />
                <Route path="/markdown_to_pmc_bbcode" element={<MarkdownToBBCodePage />} />
                <Route path="/tools" element={<ToolsPage />} />
            </Routes>
        </Suspense>
    );
}

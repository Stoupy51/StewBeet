import { Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import { MarkdownPage } from './components/MarkdownPage';
import { DocumentationPage } from './components/DocumentationPage';
import { MarkdownToBBCodePage } from './components/MarkdownToBBCodePage';

export function AppRoutes() {
    return (
        <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/documentation" element={<DocumentationPage />} />
            <Route path="/markdown" element={<MarkdownPage />} />
            <Route path="/markdown_to_pmc_bbcode" element={<MarkdownToBBCodePage />} />
        </Routes>
    );
}

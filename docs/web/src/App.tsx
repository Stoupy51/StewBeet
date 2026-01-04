import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import { MarkdownPage } from './components/MarkdownPage';
import { DocumentationPage } from './components/DocumentationPage';
import { LanguageProvider } from './context/LanguageContext';

function App() {
  return (
    <Router>
      <LanguageProvider>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/documentation" element={<DocumentationPage />} />
          <Route path="/markdown" element={<MarkdownPage />} />
        </Routes>
      </LanguageProvider>
    </Router>
  );
}

export default App;

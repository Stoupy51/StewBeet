import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import { MarkdownPage } from './components/MarkdownPage';
import { DocumentationPage } from './components/DocumentationPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/documentation" element={<DocumentationPage />} />
        <Route path="/markdown" element={<MarkdownPage />} />
      </Routes>
    </Router>
  );
}

export default App;

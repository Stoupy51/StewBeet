import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/HomePage';
import { MarkdownPage } from './components/MarkdownPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/markdown" element={<MarkdownPage />} />
      </Routes>
    </Router>
  );
}

export default App;

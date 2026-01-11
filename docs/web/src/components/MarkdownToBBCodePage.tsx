import { useState } from 'react';
import { motion } from 'framer-motion';
import { HiClipboardCopy, HiRefresh } from 'react-icons/hi';
import { convertMarkdownToBBCode } from '../utils/markdownToBBCode';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { useTranslation } from '../i18n/useTranslation';

export function MarkdownToBBCodePage() {
  const [markdownInput, setMarkdownInput] = useState('');
  const [bbcodeOutput, setBbcodeOutput] = useState('');
  const { language } = useTranslation();

  const handleConvert = () => {
    const converted = convertMarkdownToBBCode(markdownInput);
    setBbcodeOutput(converted);
  };

  const handleCopyOutput = async () => {
    try {
      await navigator.clipboard.writeText(bbcodeOutput);
      alert(language === 'fr' ? 'BBCode copié dans le presse-papiers !' : 'BBCode copied to clipboard!');
    } catch (err) {
      console.error('Erreur lors de la copie:', err);
      alert(language === 'fr' ? 'Erreur lors de la copie' : 'Copy error');
    }
  };

  const handleClearAll = () => {
    setMarkdownInput('');
    setBbcodeOutput('');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />

      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-[120px]" />
      </div>

      <main className="relative pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-4xl sm:text-5xl font-bold text-center mb-4 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              {language === 'fr' ? 'Convertisseur Markdown vers BBCode' : 'Markdown to BBCode Converter'}
            </h1>
            <p className="text-center text-slate-400 mb-12">
              {language === 'fr' ? 'Pour PlanetMinecraft' : 'For PlanetMinecraft'}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
          >
            {/* Input Section */}
            <div className="bg-slate-900/50 backdrop-blur-sm rounded-xl shadow-xl border border-white/10 p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-slate-200">
                  {language === 'fr' ? 'Markdown (Entrée)' : 'Markdown (Input)'}
                </h2>
                <button
                  onClick={() => setMarkdownInput('')}
                  className="px-3 py-1.5 text-sm bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors border border-white/10"
                >
                  {language === 'fr' ? 'Effacer' : 'Clear'}
                </button>
              </div>
              <textarea
                value={markdownInput}
                onChange={(e) => setMarkdownInput(e.target.value)}
                placeholder={language === 'fr' ? 'Collez votre texte Markdown ici...' : 'Paste your Markdown text here...'}
                className="w-full h-96 p-4 bg-slate-950 border border-white/10 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-mono text-sm text-slate-200 placeholder-slate-600 resize-none"
              />
            </div>

            {/* Output Section */}
            <div className="bg-slate-900/50 backdrop-blur-sm rounded-xl shadow-xl border border-white/10 p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-slate-200">
                  {language === 'fr' ? 'BBCode (Sortie)' : 'BBCode (Output)'}
                </h2>
                <button
                  onClick={handleCopyOutput}
                  disabled={!bbcodeOutput}
                  className="px-3 py-1.5 text-sm bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:bg-slate-800 disabled:text-slate-600 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <HiClipboardCopy className="w-4 h-4" />
                  {language === 'fr' ? 'Copier' : 'Copy'}
                </button>
              </div>
              <textarea
                value={bbcodeOutput}
                readOnly
                placeholder={language === 'fr' ? 'Le BBCode apparaîtra ici...' : 'BBCode will appear here...'}
                className="w-full h-96 p-4 bg-slate-950 border border-white/10 rounded-lg font-mono text-sm text-slate-200 placeholder-slate-600 resize-none"
              />
            </div>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex justify-center gap-4 mb-12"
          >
            <button
              onClick={handleConvert}
              disabled={!markdownInput}
              className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold rounded-lg shadow-lg shadow-indigo-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none flex items-center gap-2"
            >
              {language === 'fr' ? 'Convertir' : 'Convert'} →
            </button>
            <button
              onClick={handleClearAll}
              className="px-8 py-3 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-lg border border-white/10 transition-colors flex items-center gap-2"
            >
              <HiRefresh className="w-5 h-5" />
              {language === 'fr' ? 'Tout effacer' : 'Clear All'}
            </button>
          </motion.div>

          {/* Example Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="bg-slate-900/50 backdrop-blur-sm rounded-xl shadow-xl border border-white/10 p-6"
          >
            <h3 className="text-lg font-semibold text-slate-200 mb-6">
              {language === 'fr' ? 'Exemple de conversion' : 'Conversion Example'}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-indigo-400 mb-3">Markdown:</h4>
                <pre className="bg-slate-950 p-4 rounded-lg text-xs overflow-x-auto text-slate-300 border border-white/10">
{`## Changelog

### Build System
- 🚀 Bump version to v1.2.3

### Features
- ✨ Added new feature

**Full Changelog**: https://github.com/...`}
                </pre>
              </div>
              <div>
                <h4 className="font-medium text-purple-400 mb-3">BBCode:</h4>
                <pre className="bg-slate-950 p-4 rounded-lg text-xs overflow-x-auto text-slate-300 border border-white/10">
{`[h2]Changelog[/h2][h4]Build System[/h4][list]
[*]🚀 Bump version to v1.2.3[/*]
[/list][h4]Features[/h4][list]
[*]✨ Added new feature[/*]
[/list]
[b]Full Changelog[/b]: [url]https://github.com/...[/url]`}
                </pre>
              </div>
            </div>
          </motion.div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

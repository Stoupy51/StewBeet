import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { HiClipboardCopy, HiRefresh } from 'react-icons/hi';
import { convertMarkdownToBBCode } from '../utils/markdownToBBCode';
import { inputSizeBucket } from '../api/telemetry/streams';
import { reportToolUse } from '../utils/reportToolUse';
import { Navbar } from './Navbar';
import { PageHeader } from './PageHeader';
import { Footer } from './Footer';
import { useTranslation } from '../i18n/useTranslation';
import { useMotionSafe } from '../hooks/useMotionSafe';
import { BTN_PRIMARY, TEXT_ACCENT, TOGGLE_ACTIVE } from '../theme';

type DiffLine = { type: 'unchanged' | 'removed' | 'added'; text: string };

function computeDiff(oldText: string, newText: string): DiffLine[] {
  const a = oldText.split('\n');
  const b = newText.split('\n');
  const m = a.length, n = b.length;
  // LCS table
  const dp: number[][] = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = m - 1; i >= 0; i--)
    for (let j = n - 1; j >= 0; j--)
      dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const result: DiffLine[] = [];
  let i = 0, j = 0;
  while (i < m || j < n) {
    if (i < m && j < n && a[i] === b[j]) {
      result.push({ type: 'unchanged', text: a[i++] });
      j++;
    } else if (j < n && (i >= m || dp[i + 1][j] <= dp[i][j + 1])) {
      result.push({ type: 'added', text: b[j++] });
    } else {
      result.push({ type: 'removed', text: a[i++] });
    }
  }
  return result;
}

function DiffView({ diff, wrapClass }: { diff: DiffLine[]; wrapClass: string }) {
  return (
    <pre className={`w-full h-96 p-4 bg-ink-950 border border-ink-800 rounded-control font-mono text-sm overflow-auto ${wrapClass}`}>
      {diff.map((line, idx) => (
        <div
          key={idx}
          className={`px-1 ${
            line.type === 'added'
              ? 'bg-green-900/40 text-green-300'
              : line.type === 'removed'
              ? 'bg-red-900/40 text-red-300 line-through'
              : 'text-ink-300'
          }`}
        >
          <span className="select-none mr-2 opacity-50">
            {line.type === 'added' ? '+' : line.type === 'removed' ? '-' : ' '}
          </span>
          {line.text || '\u200b'}
        </div>
      ))}
    </pre>
  );
}

export function MarkdownToBBCodePage() {
  const [markdownInput, setMarkdownInput] = useState('');
  const [manualBbcodeOutput, setManualBbcodeOutput] = useState('');
  const [autoUpdate, setAutoUpdate] = useState(true);
  const [showDiff, setShowDiff] = useState(false);
  const [noWrap, setNoWrap] = useState(true);
  const { t, language } = useTranslation();
  const motionSafe = useMotionSafe();

  const bbcodeOutput = useMemo(
    () => (autoUpdate ? convertMarkdownToBBCode(markdownInput) : manualBbcodeOutput),
    [autoUpdate, markdownInput, manualBbcodeOutput],
  );

  const diff = useMemo(() => {
    const aLines = markdownInput.split('\n').length;
    const bLines = bbcodeOutput.split('\n').length;
    if (aLines > 500 || bLines > 500) return [] as DiffLine[];
    return computeDiff(markdownInput, bbcodeOutput);
  }, [markdownInput, bbcodeOutput]);
  const wrapClass = noWrap ? 'whitespace-pre overflow-x-auto' : 'whitespace-pre-wrap';

  // Counted on the two things a reader does on purpose, never on typing: with auto update on, the
  // output is recomputed on every keystroke, and counting that would measure the keyboard.
  const countUse = (action: string) => {
    if (markdownInput.length === 0) return;
    reportToolUse('markdown_to_bbcode', { actions: action, inputSizes: inputSizeBucket(markdownInput.length) });
  };

  const handleConvert = () => {
    const converted = convertMarkdownToBBCode(markdownInput);
    setManualBbcodeOutput(converted);
    countUse('convert');
  };

  const handleCopyOutput = async () => {
    try {
      await navigator.clipboard.writeText(bbcodeOutput);
      countUse('copy');
      alert(language === 'fr' ? 'BBCode copié dans le presse-papiers !' : 'BBCode copied to clipboard!');
    } catch (err) {
      console.error('Erreur lors de la copie:', err);
      alert(language === 'fr' ? 'Erreur lors de la copie' : 'Copy error');
    }
  };

  const handleClearAll = () => {
    setMarkdownInput('');
    setManualBbcodeOutput('');
  };

  return (
    <div className="min-h-screen bg-ink-950 text-ink-100">
      <Navbar />

      <PageHeader eyebrow={t('tools.eyebrow')} title={t('tools.markdownToBBCode')} lead={t('tools.markdownToBBCodeDesc')} width="max-w-7xl" />

      <main className="relative pb-16 px-4 sm:px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            {...motionSafe({
                initial: { y: 20 },
                animate: { y: 0 },
                transition: { duration: 0.5, delay: 0.1 },
            })}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
          >
            {/* Input Section */}
            <div className="bg-ink-900 rounded-panel border border-ink-800 p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-ink-200">
                  {language === 'fr' ? 'Markdown (Entrée)' : 'Markdown (Input)'}
                </h2>
                <button
                  onClick={() => setMarkdownInput('')}
                  className="px-3 py-1.5 text-sm bg-ink-800 hover:bg-ink-700 text-ink-200 rounded-control transition-colors border border-ink-800"
                >
                  {language === 'fr' ? 'Effacer' : 'Clear'}
                </button>
              </div>
              <textarea
                value={markdownInput}
                onChange={(e) => setMarkdownInput(e.target.value)}
                placeholder={language === 'fr' ? 'Collez votre texte Markdown ici...' : 'Paste your Markdown text here...'}
                className={`w-full h-96 p-4 bg-ink-950 border border-ink-800 rounded-control focus:ring-2 focus:ring-beet-400 focus:border-transparent font-mono text-sm text-ink-200 placeholder-ink-600 resize-none ${wrapClass}`}
              />
            </div>

            {/* Output Section */}
            <div className="bg-ink-900 rounded-panel border border-ink-800 p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-ink-200">
                  {language === 'fr' ? 'BBCode (Sortie)' : 'BBCode (Output)'}
                </h2>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCopyOutput}
                    disabled={!bbcodeOutput}
                    className={`px-3 py-1.5 text-sm ${BTN_PRIMARY} text-white rounded-control transition-colors disabled:bg-ink-800 disabled:text-ink-400 disabled:cursor-not-allowed flex items-center gap-2`}
                  >
                    <HiClipboardCopy className="w-4 h-4" />
                    {language === 'fr' ? 'Copier' : 'Copy'}
                  </button>
                </div>
              </div>
              {showDiff
                ? <DiffView diff={diff} wrapClass={wrapClass} />
                : (
                  <textarea
                    value={bbcodeOutput}
                    readOnly
                    placeholder={language === 'fr' ? 'Le BBCode apparaîtra ici...' : 'BBCode will appear here...'}
                    className={`w-full h-96 p-4 bg-ink-950 border border-ink-800 rounded-control font-mono text-sm text-ink-200 placeholder-ink-600 resize-none ${wrapClass}`}
                  />
                )}
            </div>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            {...motionSafe({
                initial: { y: 20 },
                animate: { y: 0 },
                transition: { duration: 0.5, delay: 0.2 },
            })}
            className="flex flex-wrap justify-center gap-2 mb-12"
          >
            {!autoUpdate && (
              <button
                onClick={handleConvert}
                disabled={!markdownInput}
                className={`h-10 px-5 text-sm ${BTN_PRIMARY} disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {language === 'fr' ? 'Convertir ->' : 'Convert ->'}
              </button>
            )}
            <button
              onClick={() => setNoWrap(v => !v)}
              className={`h-10 px-4 text-sm rounded-control border transition-colors flex items-center gap-2 ${
                noWrap
                  ? TOGGLE_ACTIVE
                  : 'bg-ink-900 border-ink-800 text-ink-400 hover:text-ink-100'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${noWrap ? 'bg-beet-400' : 'bg-ink-500'}`} />
              {noWrap
                ? (language === 'fr' ? 'Retour ligne : OFF' : 'Wrap: OFF')
                : (language === 'fr' ? 'Retour ligne : ON' : 'Wrap: ON')}
            </button>
            <button
              onClick={() => setShowDiff(v => !v)}
              className={`h-10 px-4 text-sm rounded-control border transition-colors flex items-center gap-2 ${
                showDiff
                  ? TOGGLE_ACTIVE
                  : 'bg-ink-900 border-ink-800 text-ink-400 hover:text-ink-100'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${showDiff ? 'bg-beet-400' : 'bg-ink-500'}`} />
              {showDiff
                ? (language === 'fr' ? 'Diff : ON' : 'Diff: ON')
                : (language === 'fr' ? 'Diff : OFF' : 'Diff: OFF')}
            </button>
            <button
              onClick={() => setAutoUpdate(v => !v)}
              className={`h-10 px-4 text-sm rounded-control border transition-colors flex items-center gap-2 ${
                autoUpdate
                  ? TOGGLE_ACTIVE
                  : 'bg-ink-900 border-ink-800 text-ink-400 hover:text-ink-100'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${autoUpdate ? 'bg-beet-400' : 'bg-ink-500'}`} />
              {autoUpdate
                ? (language === 'fr' ? 'Mise à jour auto : ON' : 'Auto-update: ON')
                : (language === 'fr' ? 'Mise à jour auto : OFF' : 'Auto-update: OFF')}
            </button>
            <button
              onClick={handleClearAll}
              className="h-10 px-4 text-sm rounded-control border border-ink-800 bg-ink-900 text-ink-300 hover:text-ink-50 hover:border-ink-600 transition-colors flex items-center gap-2"
            >
              <HiRefresh className="w-4 h-4" />
              {language === 'fr' ? 'Tout effacer' : 'Clear All'}
            </button>
          </motion.div>

          {/* Example Section */}
          <motion.div
            {...motionSafe({
                initial: { y: 20 },
                animate: { y: 0 },
                transition: { duration: 0.5, delay: 0.3 },
            })}
            className="bg-ink-900 rounded-panel border border-ink-800 p-6"
          >
            <h3 className="text-lg font-semibold text-ink-200 mb-6">
              {language === 'fr' ? 'Exemple de conversion' : 'Conversion Example'}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className={`font-medium ${TEXT_ACCENT} mb-3`}>Markdown:</h4>
                <pre className="bg-ink-950 p-4 rounded-control text-xs overflow-x-auto text-ink-300 border border-ink-800">
{`## Changelog

### Build System
- 🚀 Bump version to v1.2.3

### Features
- ✨ Added new feature

**Full Changelog**: https://github.com/...`}
                </pre>
              </div>
              <div>
                <h4 className={`font-medium ${TEXT_ACCENT} mb-3`}>BBCode:</h4>
                <pre className="bg-ink-950 p-4 rounded-control text-xs overflow-x-auto text-ink-300 border border-ink-800">
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

function isUnordered(line: string): boolean {
  const s = line.trimStart();
  return s.startsWith('- ') || s.startsWith('* ');
}

function orderedType(line: string): string | null {
  const s = line.trimStart();
  if (/^\d+\.\s/.test(s)) return '1';
  if (/^[a-z]\.\s/.test(s)) return 'a';
  return null;
}

function isOrdered(line: string): boolean {
  return orderedType(line) !== null;
}

function collectBlock(textLines: string[], start: number, predicate: (ln: string) => boolean): [string[], number] {
  const block: string[] = [];
  let j = start;
  while (j < textLines.length) {
    if (predicate(textLines[j])) {
      block.push(textLines[j]);
      j++;
    } else if (textLines[j].trim() === '') {
      let k = j + 1;
      while (k < textLines.length && textLines[k].trim() === '') k++;
      if (k < textLines.length && predicate(textLines[k])) {
        j = k;
      } else {
        break;
      }
    } else {
      break;
    }
  }
  return [block, j];
}

/**
 * Convert a block of markdown list lines (with possible nesting) to BBCode
 */
function convertListBlock(blockLines: string[], listType: string = ''): string {
  const openTag = listType ? `[list=${listType}]` : '[list]';
  const result: string[] = [];
  const levelStack: number[] = [];

  for (const line of blockLines) {
    const stripped = line.replace(/^[ \t]+/, '');
    const indent = line.length - stripped.length;
    const itemText = stripped.replace(/^(?:[a-zA-Z0-9]+\.|-|\*)\s+/, '').trim();

    if (levelStack.length === 0) {
      levelStack.push(indent);
      result.push(openTag);
    } else if (indent > levelStack[levelStack.length - 1]) {
      levelStack.push(indent);
      if (result.length > 0 && result[result.length - 1].endsWith('[/*]')) {
        result[result.length - 1] = result[result.length - 1].slice(0, -4) + openTag;
      } else {
        result.push(openTag);
      }
    } else if (indent < levelStack[levelStack.length - 1]) {
      while (levelStack.length > 1 && levelStack[levelStack.length - 1] > indent) {
        levelStack.pop();
        result.push('[/list][/*]');
      }
    }
    result.push(`[*]${itemText}[/*]`);
  }

  while (levelStack.length > 0) {
    levelStack.pop();
    result.push(levelStack.length > 0 ? '[/list][/*]' : '[/list]');
  }

  return result.join('\n');
}

/**
 * Convert markdown to BBCode for PlanetMinecraft
 * 
 * @param markdown - Markdown text to convert
 * @returns BBCode formatted text
 */
export function convertMarkdownToBBCode(markdown: string): string {
  // Make a copy of the original markdown text
  let bbcode: string = markdown;

  // Step 0: Convert <br> tags to newlines
  bbcode = bbcode.replace(/<br\s*\/>/g, '\n');
  bbcode = bbcode.replace(/<br>/g, '\n');

  // Step 1: Convert headers (# -> [h1], ## -> [h2], ### -> [h4])
  bbcode = bbcode.replace(/^# ([^\n]+)/gm, '[h1]$1[/h1]');
  bbcode = bbcode.replace(/^## ([^\n]+)/gm, '[h2]$1[/h2]');
  bbcode = bbcode.replace(/^### ([^\n]+)/gm, '[h4]$1[/h4]');

  // Step 1b: Convert markdown tables to BBCode tables
  bbcode = bbcode.replace(
    /^[ \t]*\|[^\n]*(?:\n[ \t]*\|[^\n]*)*/gm,
    (match) => {
      const rows = match.split('\n').filter(r => r.trim());
      let result = '[table][tbody]';
      for (const row of rows) {
        const cells = row.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
        // Skip separator row (cells like ---, :---, ---:)
        if (cells.filter(c => c.trim()).every(c => /^[-:]+$/.test(c))) continue;
        result += '[tr]' + cells.map(c => `[td]${c}[/td]`).join('') + '[/tr]';
      }
      result += '[/tbody][/table]';
      return result;
    },
  );

  // Step 2-3: Process lists with nested support using line-by-line traversal
  const textLines = bbcode.split('\n');
  const resultLines: string[] = [];
  let i = 0;
  while (i < textLines.length) {
    const line = textLines[i];
    if (isUnordered(line)) {
      const [blockLines, next] = collectBlock(textLines, i, isUnordered);
      resultLines.push(convertListBlock(blockLines));
      i = next;
    } else if (isOrdered(line)) {
      const oType = orderedType(line)!;
      const [blockLines, next] = collectBlock(textLines, i, isOrdered);
      resultLines.push(convertListBlock(blockLines, oType));
      i = next;
    } else {
      resultLines.push(line);
      i++;
    }
  }
  bbcode = resultLines.join('\n');

  // Step 3b: Convert spoiler/details blocks
  // Format: <details><summary>X</summary>content</details> -> [spoiler=X]content[/spoiler]
  bbcode = bbcode.replace(
    /<details>\s*<summary>([^<]+)<\/summary>([\s\S]*?)<\/details>/g,
    (_, title, content) => `[spoiler=${title.trim()}]${content.trim()}[/spoiler]`,
  );

  // Step 3c: Convert fenced code blocks
  // Format: ```\ncode\n``` -> [code]code[/code]
  bbcode = bbcode.replace(/```[^\n]*\n([\s\S]*?)```/g, (_, code) => `[code]${code.trimEnd()}[/code]`);

  // Step 3e: Convert blockquotes (group consecutive > lines)
  // Format: > text -> [quote]text[/quote]
  bbcode = bbcode.replace(
    /(?:^> ?[^\n]*(?:\n> ?[^\n]*)*)/gm,
    (match) => '[quote]' + match.replace(/^> ?/gm, '') + '[/quote]',
  );

  // Step 3f: Convert horizontal rules
  // Format: --- or *** (alone on a line) -> [hr]
  bbcode = bbcode.replace(/^[-*]{3,}$/gm, '[hr]');

  // Step 4: Convert clickable images (must be done before regular links and images)
  // Format: [![alt](img_url)](link_url) -> [url=link_url][img]img_url[/img][/url]
  bbcode = bbcode.replace(/\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)/g, '[url=$3][img]$2[/img][/url]');

  // Step 5: Convert regular images
  // Format: ![alt](img_url) -> [img]img_url[/img]
  bbcode = bbcode.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '[img]$2[/img]');

  // Step 6: Convert markdown links to BBCode links
  // Format: [text](url) -> [url=url]text[/url]
  bbcode = bbcode.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '[url=$2]$1[/url]');

  // Step 6b: Join consecutive images on the same line (separated by only a single newline)
  const imgBbPattern = /((?:\[url=[^\]]+\])?\[img\][^\n]+\[\/img\](?:\[\/url\])?)\n((?:\[url=[^\]]+\])?\[img\])/g;
  let prevBbcode: string;
  do {
    prevBbcode = bbcode;
    bbcode = bbcode.replace(imgBbPattern, '$1 $2');
    imgBbPattern.lastIndex = 0;
  } while (prevBbcode !== bbcode);

  // Step 6c: Convert inline code (after links so backtick-wrapped link text is handled correctly)
  // Format: `code` -> [color=#34495e]code[/color]
  bbcode = bbcode.replace(/`([^`\n]+)`/g, '[color=#34495e]$1[/color]');

  // Step 7: Convert bold text
  // Format: **text** -> [b]text[/b]
  bbcode = bbcode.replace(/\*\*([^*]+)\*\*/g, '[b]$1[/b]');

  // Step 7b: Convert strikethrough text
  // Format: ~~text~~ -> [s]text[/s]
  bbcode = bbcode.replace(/~~([^~]+)~~/g, '[s]$1[/s]');

  // Step 7c: Convert italic text (single * or _)
  // Format: *text* or _text_ -> [i]text[/i]
  // Exclude [*] and [/*] list tags by checking for [ and / before *
  bbcode = bbcode.replace(/(?<![[/])\*(?![*\]])([^*\n]+)(?<![[/])\*(?![*\]])/g, '[i]$1[/i]');
  bbcode = bbcode.replace(/(?<![_\w[])_([^_\n]+)_(?![_\w\]])/g, '[i]$1[/i]');

  // Step 8: Convert plain URLs (not already in BBCode)
  // Look for URLs not already inside [url] or [img] tags
  // Note: [^\s\[\]]+ excludes '[' to avoid consuming BBCode list tags like [/*]
  const urlPattern = /(?<!\[url=|\[url\]|\[img\])(https?:\/\/[^\s\[\]]+)(?!\[\/url\]|\[\/img\])/g;
  bbcode = bbcode.replace(urlPattern, '[url]$1[/url]');

  // Step 9: Remove blank lines between sections to create compact format
  bbcode = bbcode.replace(/\n{3,}/g, '\n\n'); // Collapse 3+ newlines to 2 (i.e. one blank line max)
  bbcode = bbcode.replace(/\[\/h2\]\n+\[h4\]/g, '[/h2][h4]');
  bbcode = bbcode.replace(/\[\/h4\]\n+\[list\]/g, '[/h4][list]');
  bbcode = bbcode.replace(/\[\/list\]\n+\[h4\]/g, '[/list][h4]');
  bbcode = bbcode.replace(/\[\/list\]\n+\[b\]/g, '[/list]\n[b]');
  bbcode = bbcode.replace(/:\n\n\[list\]/g, ':\n[list]'); // Remove blank line between colon and list

  return bbcode;
}

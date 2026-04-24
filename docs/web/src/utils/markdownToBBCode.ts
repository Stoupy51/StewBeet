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

  // Step 2: Process lists (group list items by sections)
  const listSections: string[][] = [];
  let currentList: string[] = [];

  const lines = bbcode.split('\n');
  for (const line of lines) {
    if (line.trim().startsWith('- ')) {
      // Remove the "- " prefix and add to current list
      const listItem = line.trim().substring(2);
      currentList.push(listItem);
    } else if (line.trim() === '' && currentList.length > 0) {
      // Empty line within a list, continue (don't break the list)
      continue;
    } else if (currentList.length > 0) {
      // If we have list items and found a non-list, non-empty line,
      // add the current list to our sections and reset
      listSections.push(currentList);
      currentList = [];
    }
  }

  // Add any remaining list items
  if (currentList.length > 0) {
    listSections.push(currentList);
  }

  // Step 3: Convert each list section to BBCode format
  for (const items of listSections) {
    const listBb = '[list]\n' + items.map(item => `[*]${item.trim()}[/*]`).join('\n') + '\n[/list]';
    
    // Create regex pattern that allows for multiple newlines between items
    const escapeRegex = (str: string) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pattern = items.map(item => escapeRegex(`- ${item}`)).join('\\n+');
    bbcode = bbcode.replace(new RegExp(pattern), listBb);
  }

  // Step 3b: Convert spoiler/details blocks
  // Format: <details><summary>X</summary>content</details> -> [spoiler=X]content[/spoiler]
  bbcode = bbcode.replace(
    /<details>\s*<summary>([^<]+)<\/summary>([\s\S]*?)<\/details>/g,
    (_, title, content) => `[spoiler=${title.trim()}]${content.trim()}[/spoiler]`,
  );

  // Step 3c: Convert fenced code blocks
  // Format: ```\ncode\n``` -> [code]code[/code]
  bbcode = bbcode.replace(/```[^\n]*\n([\s\S]*?)```/g, (_, code) => `[code]${code.trimEnd()}[/code]`);

  // Step 3d: Convert inline code
  // Format: `code` -> [inlinecode]code[/inlinecode]
  bbcode = bbcode.replace(/`([^`\n]+)`/g, '[inlinecode]$1[/inlinecode]');

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
  const urlPattern = /(?<!\[url=|\[url\]|\[img\])(https?:\/\/[^\s\]]+)(?!\[\/url\]|\[\/img\])/g;
  bbcode = bbcode.replace(urlPattern, '[url]$1[/url]');

  // Step 9: Remove blank lines between sections to create compact format
  bbcode = bbcode.replace(/\[\/h2\]\n+\[h4\]/g, '[/h2][h4]');
  bbcode = bbcode.replace(/\[\/h4\]\n+\[list\]/g, '[/h4][list]');
  bbcode = bbcode.replace(/\[\/list\]\n+\[h4\]/g, '[/list][h4]');
  bbcode = bbcode.replace(/\[\/list\]\n+\[b\]/g, '[/list]\n[b]');

  return bbcode;
}

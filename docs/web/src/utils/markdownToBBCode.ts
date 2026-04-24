/**
 * Convert markdown to BBCode for PlanetMinecraft
 * 
 * @param markdown - Markdown text to convert
 * @returns BBCode formatted text
 */
export function convertMarkdownToBBCode(markdown: string): string {
  // Make a copy of the original markdown text
  let bbcode: string = markdown;

  // Step 1: Convert headers (# -> [h1], ## -> [h2], ### -> [h4])
  bbcode = bbcode.replace(/^# ([^\n]+)/gm, '[h1]$1[/h1]');
  bbcode = bbcode.replace(/^## ([^\n]+)/gm, '[h2]$1[/h2]');
  bbcode = bbcode.replace(/^### ([^\n]+)/gm, '[h4]$1[/h4]');

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

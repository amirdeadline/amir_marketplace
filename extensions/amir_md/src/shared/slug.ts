/** GitHub-style heading slugs, with -1, -2 suffixes for repeats (FR-LINK-03). */
export function slugger(): (text: string) => string {
  const used = new Map<string, number>();
  return (text: string) => {
    const base = text
      .toLowerCase()
      .trim()
      .replace(/<[^>]*>/g, '')
      .replace(/[^\p{L}\p{M}\p{N}\p{Pc}\- ]/gu, '')
      .replace(/ /g, '-');
    const n = used.get(base);
    used.set(base, (n ?? -1) + 1);
    return n === undefined ? base : `${base}-${n + 1}`;
  };
}

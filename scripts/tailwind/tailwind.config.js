/** Tailwind config for the standalone CLI. Run from the repo root via
 *  scripts/build_css.py, which is why the content globs are repo-relative.
 */
module.exports = {
  content: [
    // Templates catch classes in branches the current content never renders,
    // e.g. the "No posts yet" fallback on the home page.
    'theme/templates/**/*.html',
    // The built site catches anything Pelican or Markdown generates that no
    // template mentions literally. build_css.py writes it here first.
    '.cache/css-scan/**/*.html',
  ],
  theme: {
    extend: {
      // base.html defines .font-slab in its inline <style> too. Registering it
      // here as well is what makes `font-slab` a real utility, so modifiers
      // like `prose-headings:font-slab` in article.html actually generate a
      // rule instead of silently doing nothing.
      fontFamily: {
        slab: ["'Roboto Slab'", 'Georgia', 'serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}

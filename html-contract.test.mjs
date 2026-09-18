import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import test from "node:test";

const root = new URL("./", import.meta.url);
const index = await readFile(new URL("index.html", root), "utf8");
const script = await readFile(new URL("flipbook.js", root), "utf8");
const styles = await readFile(new URL("styles.css", root), "utf8");
const pages = [...index.matchAll(/<article\b[^>]*class="[^"]*\bbook-page\b[^"]*"[^>]*>/g)].map(
  ([tag]) => tag,
);

test("template is vanilla HTML", () => {
  assert.doesNotMatch(`${index}\n${script}\n${styles}`, /react|jsx|vite/i);
  assert.match(index, /id="book"/);
  assert.match(index, /data-page-width="\d+"/);
  assert.match(index, /data-page-height="\d+"/);
  assert.match(index, /vendor\/page-flip\.browser\.js/);
  assert.match(script, /new St\.PageFlip/);
  assert.match(script, /loadFromHTML\(pages\)/);
  assert.match(script, /bookElement\.dataset\.pageWidth/);
  assert.match(script, /bookElement\.dataset\.pageHeight/);
  assert.match(styles, /\.book-page\.\--left::before/);
  assert.match(styles, /\.book-page\.\--right::before/);
  assert.match(styles, /z-index:\s*3/);
  assert.match(styles, /linear-gradient\(to (?:left|right)/);
  assert.doesNotMatch(styles, /box-shadow:\s*inset/);
  assert.doesNotMatch(styles, /book-gutter|data-orientation="landscape"/);
});

test("cover and page density contract is valid", () => {
  assert.ok(pages.length >= 2);
  assert.match(pages[0], /data-density="hard"/);
  assert.match(pages.at(-1), /data-density="hard"/);
  for (const page of pages.slice(1, -1)) assert.doesNotMatch(page, /data-density="hard"/);
});

test("default page size stays inside the UI envelope", () => {
  const width = Number(index.match(/data-page-width="(\d+)"/)?.[1]);
  const height = Number(index.match(/data-page-height="(\d+)"/)?.[1]);
  assert.ok(Math.max(width, height) <= 640);
});

test("vendored runtime and photo directory exist", async () => {
  assert.equal((await stat(new URL("vendor/page-flip.browser.js", root))).isFile(), true);
  assert.equal((await stat(new URL("assets/photos/", root))).isDirectory(), true);
});

test("theme picker interaction is persistent and keyboard accessible", () => {
  assert.match(index, /id="theme-toggle"[^>]*aria-expanded="false"/);
  assert.match(index, /id="theme-popover"[^>]*role="dialog"/);
  assert.match(index, /class="theme-options"/);
  assert.match(script, /storedTheme/);
  assert.match(script, /applyTheme/);
  assert.match(script, /aria-expanded/);
  assert.match(script, /aria-pressed/);
  assert.match(script, /Escape/);
  assert.match(script, /document\.addEventListener\("click"/);
  assert.match(script, /themeToggle\.focus/);
  assert.match(script, /tapAction/);
  assert.match(script, /isInteractiveTarget/);
  assert.match(script, /disableFlipByClick:\s*true/);
  assert.match(script, /pointerup/);
  assert.match(script, /capture:\s*true/);
  assert.match(script, /flippingTime:\s*460/);
  assert.match(script, /drawShadow:\s*false/);
  assert.match(script, /setThemePopover\(false/);
  assert.match(script, /close-popover/);
  assert.match(script, /if \(orientationStatus\) orientationStatus\.textContent/);
  assert.doesNotMatch(script, /orientationStatus\?\.textContent/);
  assert.doesNotMatch(index, /class="book-header"/);
  assert.match(index, /class="book-theme-overlay"/);
});

test("month timeline is accessible and photo folios stay outside artwork", () => {
  assert.match(index, /id="month-timeline"/);
  assert.ok(script.includes('querySelectorAll(".month-jump")'));
  assert.doesNotMatch(index, /class="folio"/);
  assert.match(index, /month-timeline.js/);
});

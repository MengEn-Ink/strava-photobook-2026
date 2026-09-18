import assert from "node:assert/strict";
import test from "node:test";

import { THEMES, DEFAULT_THEME_ID, accentInk, resolveThemeId, applyTheme } from "./theme-catalog.js";

const expected = [
  ["editorial", "黑白橙（默认）", "#0A0A0A", "#FF5A36"],
  ["klein-neon", "克莱因蓝 + 荧光绿", "#022A99", "#B7F800"],
  ["lapis-magenta", "青金石 + 洋红", "#01008A", "#FF0086"],
  ["deep-green-lava", "深灰绿 + 熔岩", "#003D37", "#EB4743"],
  ["navy-hermes", "藏蓝色 + 爱马仕橙", "#000035", "#FC8416"],
  ["mars-rose", "马尔斯绿 + 玫瑰粉", "#01847F", "#F9D2E4"],
  ["sea-lemon", "海蓝 + 柠檬黄", "#0084D6", "#FFFF00"],
  ["klein-pine", "克莱因蓝 + 松花黄", "#022A99", "#FFE76F"],
  ["navy-crimson", "藏蓝色 + 绯红", "#000035", "#E41726"],
  ["marine-sage", "海军蓝 + 鼠尾草绿", "#29436E", "#A1CD6A"],
  ["smoke-rice", "烟雾蓝 + 稻香黄", "#2F4058", "#D89F3E"],
  ["burgundy-stone", "绛红 + 石绿", "#950F16", "#56C4C3"],
  ["china-red-white", "中国红 + 鱼肚白", "#D7000F", "#F1F2E5"],
  ["vandyke-khaki", "凡戴克棕 + 浅卡其", "#492D22", "#D8C7B5"],
  ["deepblue-mist", "深灰蓝 + 雾蓝", "#28517F", "#C7E1FA"],
  ["royal-mint", "宝蓝色 + 薄荷绿", "#012696", "#A4E2C6"],
  ["dai-lotus", "黛蓝 + 藕粉", "#425066", "#E4C6D0"],
  ["indigo-chixiang", "靛蓝 + 赤香", "#0C567D", "#EDB79C"],
  ["hidden-green-spring", "幽绿 + 春辰", "#56765E", "#CBDA99"],
];

test("catalog preserves all approved themes in order", () => {
  assert.equal(DEFAULT_THEME_ID, "editorial");
  assert.deepEqual(THEMES.map(({ id, name, primary, accent }) => [id, name, primary, accent]), expected);
});

test("accent ink chooses readable black or white", () => {
  assert.equal(accentInk("#B7F800"), "#0A0A0A");
  assert.equal(accentInk("#E41726"), "#FFFFFF");
});

test("invalid IDs fall back and applying a theme updates root and storage", () => {
  assert.equal(resolveThemeId("missing"), DEFAULT_THEME_ID);
  const values = {};
  const root = { dataset: {}, style: { setProperty: (key, value) => { values[key] = value; } } };
  const writes = [];
  const storage = { setItem: (...args) => writes.push(args) };
  const theme = applyTheme("klein-neon", root, storage);
  assert.equal(theme.id, "klein-neon");
  assert.equal(root.dataset.theme, "klein-neon");
  assert.equal(values["--theme-primary"], "#022A99");
  assert.equal(values["--theme-accent"], "#B7F800");
  assert.equal(values["--theme-accent-ink"], "#0A0A0A");
  assert.deepEqual(writes, [["strava-photobook.theme", "klein-neon"]]);
});

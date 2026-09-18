export const DEFAULT_THEME_ID = "editorial";
export const THEME_STORAGE_KEY = "strava-photobook.theme";

export const THEMES = Object.freeze([
  { id: "editorial", name: "黑白橙（默认）", primary: "#0A0A0A", accent: "#FF5A36" },
  { id: "klein-neon", name: "克莱因蓝 + 荧光绿", primary: "#022A99", accent: "#B7F800" },
  { id: "lapis-magenta", name: "青金石 + 洋红", primary: "#01008A", accent: "#FF0086" },
  { id: "deep-green-lava", name: "深灰绿 + 熔岩", primary: "#003D37", accent: "#EB4743" },
  { id: "navy-hermes", name: "藏蓝色 + 爱马仕橙", primary: "#000035", accent: "#FC8416" },
  { id: "mars-rose", name: "马尔斯绿 + 玫瑰粉", primary: "#01847F", accent: "#F9D2E4" },
  { id: "sea-lemon", name: "海蓝 + 柠檬黄", primary: "#0084D6", accent: "#FFFF00" },
  { id: "klein-pine", name: "克莱因蓝 + 松花黄", primary: "#022A99", accent: "#FFE76F" },
  { id: "navy-crimson", name: "藏蓝色 + 绯红", primary: "#000035", accent: "#E41726" },
  { id: "marine-sage", name: "海军蓝 + 鼠尾草绿", primary: "#29436E", accent: "#A1CD6A" },
  { id: "smoke-rice", name: "烟雾蓝 + 稻香黄", primary: "#2F4058", accent: "#D89F3E" },
  { id: "burgundy-stone", name: "绛红 + 石绿", primary: "#950F16", accent: "#56C4C3" },
  { id: "china-red-white", name: "中国红 + 鱼肚白", primary: "#D7000F", accent: "#F1F2E5" },
  { id: "vandyke-khaki", name: "凡戴克棕 + 浅卡其", primary: "#492D22", accent: "#D8C7B5" },
  { id: "deepblue-mist", name: "深灰蓝 + 雾蓝", primary: "#28517F", accent: "#C7E1FA" },
  { id: "royal-mint", name: "宝蓝色 + 薄荷绿", primary: "#012696", accent: "#A4E2C6" },
  { id: "dai-lotus", name: "黛蓝 + 藕粉", primary: "#425066", accent: "#E4C6D0" },
  { id: "indigo-chixiang", name: "靛蓝 + 赤香", primary: "#0C567D", accent: "#EDB79C" },
  { id: "hidden-green-spring", name: "幽绿 + 春辰", primary: "#56765E", accent: "#CBDA99" },
]);

const byId = new Map(THEMES.map((theme) => [theme.id, theme]));

function channels(hex) {
  const normalized = hex.replace("#", "");
  return [0, 2, 4].map((offset) => Number.parseInt(normalized.slice(offset, offset + 2), 16));
}

export function accentInk(hex) {
  const [r, g, b] = channels(hex);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness >= 150 ? "#0A0A0A" : "#FFFFFF";
}

export function resolveThemeId(id) {
  return byId.has(id) ? id : DEFAULT_THEME_ID;
}

export function applyTheme(id, root = document.documentElement, storage = window.localStorage) {
  const theme = byId.get(resolveThemeId(id));
  root.dataset.theme = theme.id;
  root.style.setProperty("--theme-primary", theme.primary);
  root.style.setProperty("--theme-accent", theme.accent);
  root.style.setProperty("--theme-accent-ink", accentInk(theme.accent));
  try { storage?.setItem(THEME_STORAGE_KEY, theme.id); } catch (_) { /* storage is optional */ }
  return theme;
}

export function storedTheme(storage = window.localStorage) {
  try { return resolveThemeId(storage?.getItem(THEME_STORAGE_KEY)); } catch (_) { return DEFAULT_THEME_ID; }
}

if (typeof window !== "undefined") {
  window.StravaPhotobookThemes = { THEMES, DEFAULT_THEME_ID, THEME_STORAGE_KEY, accentInk, resolveThemeId, applyTheme, storedTheme };
}

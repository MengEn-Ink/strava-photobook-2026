export function clickDirection(clientX, bounds) {
  if (!bounds || bounds.width <= 0 || clientX < bounds.left || clientX > bounds.right) return null;
  return clientX < bounds.left + bounds.width / 2 ? "previous" : "next";
}

export function isInteractiveTarget(target) {
  return Boolean(target?.closest?.("a,button,input,select,textarea,[role='button'],[data-no-page-click]"));
}

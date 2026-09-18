import assert from "node:assert/strict";
import test from "node:test";
import { clickDirection, isInteractiveTarget } from "./click-navigation.js";

test("clickDirection maps the visible left and right halves", () => {
  const bounds = { left: 100, right: 900, width: 800 };
  assert.equal(clickDirection(200, bounds), "previous");
  assert.equal(clickDirection(800, bounds), "next");
  assert.equal(clickDirection(50, bounds), null);
});

test("interactive controls never trigger page navigation", () => {
  assert.equal(isInteractiveTarget({ closest: () => ({ tagName: "BUTTON" }) }), true);
  assert.equal(isInteractiveTarget({ closest: () => null }), false);
});

import assert from "node:assert/strict";
import test from "node:test";
import { renderToStaticMarkup } from "react-dom/server";

import { hasTextSelectionIn, isNestedControlClick } from "../lib/nestedControl";
import { StyleCardTitle } from "./StyleCardTitle";

// Stands in for a DOM element: closest() returns a marker node when the
// element itself, or one of the ancestors listed in `path`, matches one of the
// selector's parts (a tag name such as "button" or an attribute selector such
// as '[role="switch"]').
const controlNode = {};
function targetInside(...path: string[]) {
  return {
    closest: (selector: string) => {
      const parts = selector.split(",").map((part) => part.trim());
      return path.some((node) => parts.includes(node)) ? controlNode : null;
    },
  } as unknown as EventTarget;
}

// A card that contains only the nodes it is given.
function cardContaining(...nodes: unknown[]) {
  return { contains: (node: unknown) => nodes.includes(node) } as Pick<Node, "contains">;
}
const card = cardContaining(controlNode);

test("style card title is a keyboard-reachable button that opens the detail dialog", () => {
  const markup = renderToStaticMarkup(
    <StyleCardTitle name="Minimalism" onOpen={() => undefined} />,
  );
  const button = markup.match(/^<h3[^>]*>(<button[^>]*>)Minimalism<\/button><\/h3>$/);

  assert.ok(button, `title is not a button inside the heading: ${markup}`);
  assert.match(button[1], /\stype="button"/);
  assert.match(button[1], /\saria-haspopup="dialog"/);
});

test("style card title is plain text when nothing can be opened", () => {
  const markup = renderToStaticMarkup(<StyleCardTitle name="Minimalism" />);

  assert.match(markup, /^<h3[^>]*>Minimalism<\/h3>$/);
});

test("clicks on the card's own controls do not open the detail dialog", () => {
  assert.equal(isNestedControlClick(targetInside("button"), card), true);
  assert.equal(isNestedControlClick(targetInside("svg", "button"), card), true);
  assert.equal(isNestedControlClick(targetInside("input"), card), true);
  assert.equal(isNestedControlClick(targetInside("span", "label"), card), true);
  assert.equal(isNestedControlClick(targetInside("summary"), card), true);
  assert.equal(isNestedControlClick(targetInside('[role="switch"]'), card), true);

  assert.equal(isNestedControlClick(targetInside("div"), card), false);
  assert.equal(isNestedControlClick(targetInside("pre", "div"), card), false);
  assert.equal(isNestedControlClick(null, card), false);
  assert.equal(isNestedControlClick({} as EventTarget, card), false);
});

test("a control wrapped around the whole card does not block opening it", () => {
  assert.equal(isNestedControlClick(targetInside("div", "a"), cardContaining()), false);
});

test("a click that ends a text selection does not open the detail dialog", () => {
  const inside = {} as Node;
  const elsewhere = {} as Node;
  const card = cardContaining(inside);

  assert.equal(hasTextSelectionIn({ isCollapsed: false, anchorNode: inside }, card), true);
  assert.equal(hasTextSelectionIn({ isCollapsed: true, anchorNode: inside }, card), false);
  assert.equal(hasTextSelectionIn({ isCollapsed: false, anchorNode: elsewhere }, card), false);
  assert.equal(hasTextSelectionIn(null, card), false);
});

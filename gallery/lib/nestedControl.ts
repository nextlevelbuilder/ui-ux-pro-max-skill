// A style card holds its own controls (section toggles, copy buttons, color
// swatches, checklist items). A click on one of them must only do that
// control's job instead of bubbling up and opening the detail modal.
const NESTED_CONTROL_SELECTOR = [
  "a",
  "button",
  "input",
  "label",
  "select",
  "textarea",
  "summary",
  '[role="button"]',
  '[role="checkbox"]',
  '[role="switch"]',
  '[role="link"]',
  '[role="tab"]',
  '[role="menuitem"]',
  '[role="option"]',
  "[contenteditable]",
  '[tabindex]:not([tabindex="-1"])',
].join(", ");

// Duck-typed rather than `instanceof Element` so the gallery's DOM-free unit
// tests can exercise it. Only a control inside `card` counts, so a card that
// is itself wrapped in a link or label still opens.
export function isNestedControlClick(
  target: EventTarget | null,
  card: Pick<Node, "contains">,
): boolean {
  const element = target as Element | null;
  if (typeof element?.closest !== "function") return false;
  const control = element.closest(NESTED_CONTROL_SELECTOR);
  return control !== null && card.contains(control);
}

// A drag that selects text inside the card (for example in an open "CSS Code"
// section) ends in a click on the card; it should leave the selection alone.
// A selection elsewhere on the page does not block opening the card.
export function hasTextSelectionIn(
  selection: Pick<Selection, "isCollapsed" | "anchorNode"> | null,
  card: Pick<Node, "contains">,
): boolean {
  return (
    selection !== null &&
    !selection.isCollapsed &&
    card.contains(selection.anchorNode)
  );
}

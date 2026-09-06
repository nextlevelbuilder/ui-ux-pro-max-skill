import assert from "node:assert/strict";
import test from "node:test";
import { renderToStaticMarkup } from "react-dom/server";

import type { StyleData } from "../lib/types";
import {
  getLevelVariant,
  getTaxonomyValue,
  MetadataBadges,
} from "./MetadataBadges";
import { FilterBar } from "./FilterBar";
import { DEFAULT_FILTERS } from "../lib/filterStyles";

const baseStyle: StyleData = {
  no: 1,
  styleId: "minimalism",
  styleCategory: "Minimalism",
  aliases: [],
  status: "active",
  parentStyleId: "",
  replacementDomain: "",
  replacementId: "",
  preferredMode: "auto",
  type: "General",
  keywords: "",
  primaryColors: "",
  secondaryColors: "",
  effectsAnimation: "",
  bestFor: "",
  doNotUseFor: "",
  lightMode: "supported",
  darkMode: "conditional",
  performance: "cost:moderate|drivers:animation,blur",
  accessibility: "risk:high|requires:contrast-text-4.5,keyboard",
  mobileFriendly: "adaptable",
  conversionFocused: "",
  frameworkCompatibility: "tailwind",
  eraOrigin: "",
  complexity: "Medium",
  aiPromptKeywords: "",
  cssTechnicalKeywords: "",
  implementationChecklist: "",
  designSystemVariables: "",
  extractedColors: [],
  cssProperties: {},
};

test("extracts only the requested controlled taxonomy value", () => {
  assert.equal(getTaxonomyValue(baseStyle.performance, "cost"), "moderate");
  assert.equal(getTaxonomyValue(baseStyle.accessibility, "risk"), "high");
  assert.equal(getTaxonomyValue(baseStyle.performance, "risk"), "unknown");
});

test("maps cost, risk, and mode support levels to semantic variants", () => {
  assert.equal(getLevelVariant("low"), "green");
  assert.equal(getLevelVariant("supported"), "green");
  assert.equal(getLevelVariant("moderate"), "yellow");
  assert.equal(getLevelVariant("conditional"), "yellow");
  assert.equal(getLevelVariant("high"), "red");
  assert.equal(getLevelVariant("not-recommended"), "red");
  assert.equal(getLevelVariant("unknown"), "gray");
});

test("renders concise labels with explicit accessible meaning", () => {
  const markup = renderToStaticMarkup(<MetadataBadges style={baseStyle} />);

  assert.match(markup, /aria-label="Style metadata"/);
  assert.match(markup, /class="sr-only">Performance cost: Moderate<\/span>/);
  assert.match(markup, /class="sr-only">Accessibility risk: High<\/span>/);
  assert.match(markup, /class="sr-only">Light mode support: Supported<\/span>/);
  assert.match(markup, /class="sr-only">Dark mode support: Conditional<\/span>/);
  assert.match(markup, /aria-hidden="true">A11y risk: High<\/span>/);
  assert.doesNotMatch(markup, /<span aria-label=/);
  assert.doesNotMatch(markup, /drivers:|requires:|WCAG|Excellent|Full/);
});

test("filter groups expose names and selected state", () => {
  const markup = renderToStaticMarkup(
    <FilterBar
      complexities={["Low"]}
      eras={["Modern"]}
      filters={DEFAULT_FILTERS}
      onChange={() => undefined}
      resultCount={50}
      totalCount={50}
      types={["General"]}
    />,
  );

  assert.match(markup, /aria-label="Status filter"[^>]*role="group"/);
  assert.match(markup, /aria-pressed="true"[^>]*>active<\/button>/);
  assert.match(markup, /aria-label="Type filter"[^>]*role="group"/);
  assert.match(markup, /aria-pressed="true"[^>]*>All<\/button>/);
});

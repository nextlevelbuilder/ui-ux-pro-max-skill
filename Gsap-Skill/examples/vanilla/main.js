/**
 * Minimal GSAP vanilla example — follows skills: transforms, autoAlpha, timeline, ScrollTrigger.
 * Run from repo root: npx serve examples/vanilla (or open index.html with a local server that supports ES modules).
 */
import { gsap } from "https://cdn.jsdelivr.net/npm/gsap@3.15.0/index.js";
import { ScrollTrigger } from "https://cdn.jsdelivr.net/npm/gsap@3.15.0/ScrollTrigger.js";

gsap.registerPlugin(ScrollTrigger);

// 1. Single tween — transform alias x, autoAlpha (opacity + visibility)
gsap.to("#single", {
  x: 120,
  autoAlpha: 1,
  duration: 0.6,
  ease: "power2"
});

// 2. Timeline for sequencing (defaults, position parameter)
const tl = gsap.timeline({ defaults: { duration: 0.5, ease: "power2" } });
tl.to(".a", { x: 100 })
  .to(".b", { y: 40 }, "+=0.2")
  .to(".c", { autoAlpha: 0 }, "-=0.1");

// 3. ScrollTrigger on timeline (not on child tween)
const tl2 = gsap.timeline({
  scrollTrigger: {
    trigger: "#scroll-section",
    start: "top center",
    end: "bottom center",
    scrub: true
  }
});
tl2.to(".panel", { x: 100 })
  .to(".panel", { rotation: 5, duration: 0.7 });

// After dynamic layout changes you would call: ScrollTrigger.refresh();

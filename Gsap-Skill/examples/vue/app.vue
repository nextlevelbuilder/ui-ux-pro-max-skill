/**
 * Minimal GSAP Vue 3 example — follows gsap-frameworks skill: gsap.context, scope, cleanup.
 * Scoped selectors via context; automatic revert on unmount.
 */
<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { gsap } from "gsap";

const container = ref(null);
let ctx;

onMounted(() => {
  ctx = gsap.context(() => {
    // Simple tween — moves the box right and fades it in
    gsap.to(".box", { x: 100, autoAlpha: 1, duration: 0.6, ease: "power2" });

    // Stagger animation on .item elements (scoped to container)
    gsap.from(".item", { autoAlpha: 0, y: 20, stagger: 0.1 });

    // ScrollTrigger timeline on the tall section
    gsap.timeline({
      scrollTrigger: { trigger: ".scroll-section", start: "top center", end: "bottom center", scrub: true },
    }).to(".scroll-box", { x: 200, rotation: 360 });
  }, container.value); // scope — all selectors resolve inside container
});

onUnmounted(() => {
  ctx?.revert(); // cleanup: reverts all GSAP animations created in this context
});
</script>

<template>
  <div ref="container" :style="{ padding: '2rem' }">
    <h1>GSAP Vue 3 — gsap.context + scope + cleanup</h1>

    <div class="box" :style="{ width: '80px', height: '80px', background: '#0fa', borderRadius: '8px', marginBottom: '1rem', visibility: 'hidden' }" />

    <div class="item" :style="{ margin: '0.5rem 0' }">Item 1</div>
    <div class="item" :style="{ margin: '0.5rem 0' }">Item 2</div>
    <div class="item" :style="{ margin: '0.5rem 0' }">Item 3</div>

    <div class="scroll-section" :style="{ height: '150vh', marginTop: '2rem', background: '#f0f0f0', padding: '1rem' }">
      <p>Scroll down to trigger the timeline</p>
      <div class="scroll-box" :style="{ width: '60px', height: '60px', background: '#f0a', borderRadius: '8px', marginTop: '1rem' }" />
    </div>
  </div>
</template>
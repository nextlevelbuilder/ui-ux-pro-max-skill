<script setup>
import { onMounted, onUnmounted } from "vue";

const { gsap, ScrollTrigger, lazyLoadPlugin } = useGSAP();

let ctx;
onMounted(async () => {
  const SplitText = await lazyLoadPlugin("SplitText");
  
  ctx = gsap.context(() => {
    const split = SplitText.create("h1", {
      type: "chars",
    });
    gsap.from(split.chars, {
      autoAlpha: 0,
      y: -50,
      xPercent: -100,
      rotation: -45,
      ease: "power1.inOut",
      stagger: {
        amount: 0.3,
      },
    });

    gsap.set("h1", { autoAlpha: 1 });
  });
});

onMounted(() => {
  ctx && ctx.revert();
});
</script>

<template>
  <main>
    <h1>GSAP SplitText</h1>
  </main>
</template>

<style scoped>
  main {
    width: 100%;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;
    font-size: 18px;
  }

  main h1 {
    opacity: 0;
    visibility: hidden;
  }
</style>
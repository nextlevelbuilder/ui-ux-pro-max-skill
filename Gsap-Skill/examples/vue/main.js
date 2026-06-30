import { createApp } from "vue";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import App from "./App.vue";

// Register all the GSAP Plugins you want only once at this top level file
gsap.registerPlugin(ScrollTrigger);

createApp(App).mount("#app");
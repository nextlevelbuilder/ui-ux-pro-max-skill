/**
 * Minimal GSAP React example — follows gsap-react skill: useGSAP, scope, cleanup.
 * No selector without scope; refs for targets; automatic revert on unmount.
 */
import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import { gsap } from "gsap";

// Register useGSAP once (could be in main.jsx for app-level)
gsap.registerPlugin(useGSAP);

function App() {
  const containerRef = useRef(null);
  const boxRef = useRef(null);

  useGSAP(
    () => {
      // Scoped to containerRef — selectors only match inside container
      gsap.to(boxRef.current, { x: 100, duration: 0.6, ease: "power2" });
      gsap.from(".item", { autoAlpha: 0, y: 20, stagger: 0.1 });
    },
    { scope: containerRef }
  );

  return (
    <div ref={containerRef} style={{ padding: "2rem" }}>
      <h1>GSAP React — useGSAP + scope + cleanup</h1>
      <div
        ref={boxRef}
        className="box"
        style={{
          width: 80,
          height: 80,
          background: "#0fa",
          borderRadius: 8,
          marginBottom: "1rem",
        }}
      />
      <div className="item" style={{ margin: "0.5rem 0" }}>Item 1</div>
      <div className="item" style={{ margin: "0.5rem 0" }}>Item 2</div>
      <div className="item" style={{ margin: "0.5rem 0" }}>Item 3</div>
    </div>
  );
}

export default App;

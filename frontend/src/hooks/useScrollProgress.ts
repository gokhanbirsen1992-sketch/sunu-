import { useEffect, useRef } from "react";

/**
 * Shared scroll progress ref. Lenis (or window scroll) updates `current.value`,
 * R3F scenes read it inside useFrame without triggering React re-renders.
 */
export type ScrollProgressRef = { current: { value: number; section: number } };

export function useScrollProgressRef(): ScrollProgressRef {
  const ref = useRef({ value: 0, section: 0 });

  useEffect(() => {
    let raf = 0;
    const update = () => {
      const doc = document.documentElement;
      const max = doc.scrollHeight - window.innerHeight;
      const p = max > 0 ? window.scrollY / max : 0;
      ref.current.value = p;
      raf = requestAnimationFrame(update);
    };
    raf = requestAnimationFrame(update);
    return () => cancelAnimationFrame(raf);
  }, []);

  return ref;
}

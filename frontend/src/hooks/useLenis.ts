import { useEffect } from "react";
import Lenis from "lenis";

/**
 * Lenis smooth-scroll hook. Yatay/dikey scroll'u CSS native'den
 * çıkarıp yumuşak (eased) bir akışa dönüştürür — NYT/Apple sitelerinde
 * scroll'un "kayar" gibi gelmesinin sebebi.
 */
export function useLenis() {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      wheelMultiplier: 1.0,
      touchMultiplier: 1.0,
    });

    let rafId = 0;
    const raf = (time: number) => {
      lenis.raf(time);
      rafId = requestAnimationFrame(raf);
    };
    rafId = requestAnimationFrame(raf);

    return () => {
      cancelAnimationFrame(rafId);
      lenis.destroy();
    };
  }, []);
}

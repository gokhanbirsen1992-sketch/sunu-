import { useEffect, useRef, useState } from "react";
import {
  animate,
  motion,
  useMotionValue,
  useScroll,
  useTransform,
} from "framer-motion";

/**
 * Cinematic opening: scroll'a kilitli, kademeli açılış.
 *
 * Phase A (start): siyah ekran + tek bir parlak nokta
 * Phase B (mid): nokta patlar, yıldız oluşur, bilirubin 0 → 28 sayar
 * Phase C (end): "YILDIZIN SARILIĞI" başlığı belirir, kayar gider
 */
export function CinematicHero({
  title,
  subtitle,
}: {
  title: string;
  subtitle: string;
}) {
  const ref = useRef<HTMLElement | null>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end end"],
  });

  // Counter
  const counter = useMotionValue(0);
  const [counterText, setCounterText] = useState("0");

  useEffect(() => {
    const unsub = counter.on("change", (v) =>
      setCounterText(Math.round(v).toString()),
    );
    const ctrl = animate(counter, 28, {
      duration: 2.8,
      delay: 1.2,
      ease: [0.16, 1, 0.3, 1],
    });
    return () => {
      ctrl.stop();
      unsub();
    };
  }, [counter]);

  // Scroll-bound: as user scrolls, title pulls up, fades
  const titleY = useTransform(scrollYProgress, [0, 1], [0, -180]);
  const titleScale = useTransform(scrollYProgress, [0, 1], [1, 0.7]);
  const titleOpacity = useTransform(
    scrollYProgress,
    [0, 0.6, 1],
    [1, 1, 0],
  );

  // The bilirubin meter fills as user scrolls
  const meterFill = useMotionValue(0);
  const meterScale = useTransform(meterFill, [0, 28], [0, 1]);

  useEffect(() => {
    const ctrl = animate(meterFill, 28, {
      duration: 2.8,
      delay: 1.2,
      ease: [0.16, 1, 0.3, 1],
    });
    return () => ctrl.stop();
  }, [meterFill]);

  // Scroll prompt fades as user starts scrolling
  const scrollPromptOpacity = useTransform(
    scrollYProgress,
    [0, 0.05],
    [1, 0],
  );

  return (
    <section ref={ref} className="hero-c" id="hero">
      <motion.div
        className="hero-c__inner"
        style={{
          y: titleY,
          scale: titleScale,
          opacity: titleOpacity,
        }}
      >
        <motion.div
          className="hero-c__kicker"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.2 }}
        >
          21 KATMANDA BİLİRUBİN · BİR YENİDOĞAN VAKASI
        </motion.div>

        <motion.h1
          className="hero-c__title"
          initial={{ opacity: 0, y: 40, filter: "blur(20px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{ duration: 1.4, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
        >
          {title}
        </motion.h1>

        <motion.p
          className="hero-c__subtitle"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.7 }}
        >
          {subtitle}
        </motion.p>

        <motion.div
          className="hero-c__meter"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 1.0 }}
        >
          <div className="hero-c__meter-head">
            <span className="hero-c__meter-num">{counterText}</span>
            <span className="hero-c__meter-unit">mg/dL</span>
          </div>
          <div className="hero-c__meter-bar">
            <motion.div
              className="hero-c__meter-fill"
              style={{ scaleX: meterScale }}
            />
          </div>
          <div className="hero-c__meter-label">
            BİLİRUBİN · 96. SAAT · FOTOTERAPİ ALTINDA
          </div>
        </motion.div>
      </motion.div>

      <motion.div
        className="hero-c__scroll"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 4.0 }}
        style={{ opacity: scrollPromptOpacity }}
      >
        <span>AŞAĞI KAYDIR</span>
        <span className="hero-c__scroll-line" />
      </motion.div>
    </section>
  );
}

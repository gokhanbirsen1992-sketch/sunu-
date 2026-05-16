import { useEffect, useState } from "react";
import { animate, motion, useMotionValue, useTransform } from "framer-motion";

type Props = {
  title: string;
  subtitle: string;
};

export function Hero({ title, subtitle }: Props) {
  const value = useMotionValue(0);
  const meterScale = useTransform(value, [0, 28], [0, 1]);
  const [display, setDisplay] = useState("0");

  useEffect(() => {
    const unsub = value.on("change", (v) => {
      setDisplay(Math.round(v).toString());
    });
    const controls = animate(value, 28, {
      duration: 2.1,
      delay: 1.1,
      ease: [0.2, 0.65, 0.3, 1],
    });
    return () => {
      controls.stop();
      unsub();
    };
  }, [value]);

  return (
    <section className="hero" id="hero">
      <div className="hero__inner">
        <motion.div
          className="hero__kicker"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.1 }}
        >
          21 Katmanda Bilirubin · Bir Yenidoğan Vakası
        </motion.div>

        <motion.h1
          className="hero__title"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.1, delay: 0.25 }}
        >
          {title}
        </motion.h1>

        <motion.p
          className="hero__subtitle"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.5 }}
        >
          {subtitle}
        </motion.p>

        <motion.div
          className="hero__meter"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, delay: 0.85 }}
        >
          <div className="hero__meter-head">
            <span className="hero__meter-num">{display}</span>
            <span className="hero__meter-unit">mg/dL</span>
          </div>
          <div className="hero__meter-bar">
            <motion.div
              className="hero__meter-fill"
              style={{ scaleX: meterScale }}
            />
            <div className="hero__meter-marks">
              <span style={{ left: "0%" }} />
              <span style={{ left: "35.7%" }} data-label="10" />
              <span style={{ left: "71.4%" }} data-label="20" />
              <span style={{ left: "100%" }} data-label="28" />
            </div>
          </div>
          <div className="hero__meter-label">
            Bilirubin · 96. saat · fototerapi altında
          </div>
        </motion.div>
      </div>

      <motion.div
        className="hero__scroll"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 3.4 }}
      >
        Aşağı kaydır
      </motion.div>
    </section>
  );
}

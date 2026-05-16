import { motion } from "framer-motion";

type Props = {
  title: string;
  subtitle: string;
};

export function Hero({ title, subtitle }: Props) {
  return (
    <section className="hero" id="hero">
      <div>
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
          className="hero__stat"
          initial={{ opacity: 0, scale: 0.94 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1, delay: 0.85, ease: [0.2, 0.65, 0.3, 1] }}
        >
          <span className="hero__stat-num">28</span>
          <span className="hero__stat-label">Bilirubin · mg/dL · 96. saat</span>
        </motion.div>
      </div>

      <motion.div
        className="hero__scroll"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.4 }}
      >
        Aşağı kaydır
      </motion.div>
    </section>
  );
}

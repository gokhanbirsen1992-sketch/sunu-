import { motion, useScroll, useSpring } from "framer-motion";

export function ProgressBar() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 120,
    damping: 28,
    mass: 0.3,
  });
  return (
    <div className="progress-bar" aria-hidden="true">
      <motion.div className="progress-bar__fill" style={{ scaleX }} />
    </div>
  );
}

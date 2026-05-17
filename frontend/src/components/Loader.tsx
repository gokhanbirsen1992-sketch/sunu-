import { useEffect, useState } from "react";
import {
  animate,
  AnimatePresence,
  motion,
  useMotionValue,
} from "framer-motion";

type Props = {
  onDone: () => void;
};

/**
 * 3.5 saniyelik markalı açılış:
 *  - Siyah ekran
 *  - Tek "Y" beliriyor, sonra "YILDIZ", sonra "YILDIZIN SARILIĞI"
 *  - Bilirubin sayacı 0 → 28
 *  - Yumuşak fade-out, asıl deneyime devreder
 */
export function Loader({ onDone }: Props) {
  const [stage, setStage] = useState<0 | 1 | 2 | 3>(0);
  const [done, setDone] = useState(false);
  const bili = useMotionValue(0);
  const [biliText, setBiliText] = useState("0");

  useEffect(() => {
    const unsub = bili.on("change", (v) =>
      setBiliText(Math.round(v).toString()),
    );
    const t1 = window.setTimeout(() => setStage(1), 350);
    const t2 = window.setTimeout(() => setStage(2), 800);
    const t3 = window.setTimeout(() => setStage(3), 1200);
    const ctrl = animate(bili, 28, {
      duration: 1.2,
      delay: 0.8,
      ease: [0.16, 1, 0.3, 1],
    });
    const t4 = window.setTimeout(() => setDone(true), 2200);
    const t5 = window.setTimeout(() => onDone(), 2700);
    return () => {
      window.clearTimeout(t1);
      window.clearTimeout(t2);
      window.clearTimeout(t3);
      window.clearTimeout(t4);
      window.clearTimeout(t5);
      ctrl.stop();
      unsub();
    };
  }, [bili, onDone]);

  return (
    <AnimatePresence>
      {!done && (
        <motion.div
          className="loader"
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.6, ease: [0.4, 0, 0.6, 1] }}
        >
          <div className="loader__inner">
            <motion.div
              className="loader__title"
              initial={{ opacity: 0 }}
              animate={{ opacity: stage >= 0 ? 1 : 0 }}
              transition={{ duration: 0.6 }}
            >
              <span className="loader__title-line">
                <motion.span
                  className="loader__letter"
                  initial={{ opacity: 0, y: 40 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8, delay: 0.05 }}
                >
                  Y
                </motion.span>
                <motion.span
                  className="loader__letter"
                  initial={{ opacity: 0, y: 40 }}
                  animate={{
                    opacity: stage >= 1 ? 1 : 0,
                    y: stage >= 1 ? 0 : 40,
                  }}
                  transition={{ duration: 0.6 }}
                >
                  ıldız
                </motion.span>
                <motion.span
                  className="loader__letter loader__letter--small"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: stage >= 2 ? 1 : 0 }}
                  transition={{ duration: 0.6 }}
                >
                  ın
                </motion.span>
              </span>
              <motion.span
                className="loader__title-line loader__title-line--alt"
                initial={{ opacity: 0, y: 24 }}
                animate={{
                  opacity: stage >= 2 ? 1 : 0,
                  y: stage >= 2 ? 0 : 24,
                }}
                transition={{ duration: 0.8, delay: 0.1 }}
              >
                Sarılığı
              </motion.span>
            </motion.div>

            <motion.div
              className="loader__meter"
              initial={{ opacity: 0 }}
              animate={{ opacity: stage >= 3 ? 1 : 0 }}
              transition={{ duration: 0.5 }}
            >
              <span className="loader__meter-num">{biliText}</span>
              <span className="loader__meter-unit">mg/dL · bilirubin · 96. saat</span>
            </motion.div>

            <motion.div
              className="loader__progress"
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 3.4, ease: "linear" }}
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

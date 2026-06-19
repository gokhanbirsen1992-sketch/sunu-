import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { ChevronLeft, ChevronRight, X, Pencil } from 'lucide-react'
import { SlideStage } from '../components/SlideStage'
import { useDeck } from '../lib/store'
import { cn } from '../lib/cn'

const variants = {
  enter: (dir: number) => ({ opacity: 0, scale: dir >= 0 ? 0.72 : 1.28 }),
  center: { opacity: 1, scale: 1 },
  exit: (dir: number) => ({ opacity: 0, scale: dir >= 0 ? 1.28 : 0.72 }),
}

export default function Present() {
  const navigate = useNavigate()
  const { deck, currentId, select } = useDeck()
  const slides = deck.slides

  const startIndex = Math.max(
    0,
    slides.findIndex((s) => s.id === currentId),
  )
  const [[index, dir], setState] = useState<[number, number]>([startIndex, 0])
  const [showUI, setShowUI] = useState(true)

  const go = useCallback(
    (next: number, direction: number) => {
      const clamped = Math.max(0, Math.min(slides.length - 1, next))
      setState([clamped, direction])
    },
    [slides.length],
  )

  const exit = useCallback(() => {
    // Remember where we were so the editor opens on the same slide.
    if (slides[index]) select(slides[index].id)
    navigate('/editor')
  }, [index, navigate, select, slides])

  // Keyboard navigation
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowRight':
        case ' ':
        case 'PageDown':
          e.preventDefault()
          go(index + 1, 1)
          break
        case 'ArrowLeft':
        case 'PageUp':
          e.preventDefault()
          go(index - 1, -1)
          break
        case 'Home':
          go(0, -1)
          break
        case 'End':
          go(slides.length - 1, 1)
          break
        case 'Escape':
          exit()
          break
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [index, go, exit, slides.length])

  // Auto-hide UI after inactivity
  useEffect(() => {
    let t: number
    const wake = () => {
      setShowUI(true)
      clearTimeout(t)
      t = window.setTimeout(() => setShowUI(false), 2600)
    }
    wake()
    window.addEventListener('mousemove', wake)
    window.addEventListener('keydown', wake)
    return () => {
      clearTimeout(t)
      window.removeEventListener('mousemove', wake)
      window.removeEventListener('keydown', wake)
    }
  }, [])

  const slide = slides[index]
  const atStart = index === 0
  const atEnd = index === slides.length - 1

  return (
    <div className="fixed inset-0 select-none overflow-hidden bg-black">
      {/* Top progress bar */}
      <div className="absolute left-0 right-0 top-0 z-30 h-1 bg-white/10">
        <motion.div
          className="h-full bg-gradient-to-r from-indigo-400 via-fuchsia-400 to-rose-400"
          animate={{ width: `${((index + 1) / slides.length) * 100}%` }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
        />
      </div>

      {/* Slide stage (letterboxed 16:9) */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div
          className="relative"
          style={{ width: 'min(100vw, calc(100vh * 16 / 9))', aspectRatio: '16 / 9' }}
        >
          <AnimatePresence custom={dir}>
            <motion.div
              key={slide.id}
              custom={dir}
              variants={variants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.62, ease: [0.22, 1, 0.36, 1] }}
              className="absolute inset-0 overflow-hidden"
            >
              {/* SlideStage scales the fixed 1280x720 design to fill this 16:9 box */}
              <SlideStage slide={slide} rounded={false} />
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Click zones for prev / next */}
      <button
        aria-label="Önceki"
        onClick={() => go(index - 1, -1)}
        className="absolute left-0 top-0 z-20 h-full w-1/3 cursor-w-resize focus:outline-none"
      />
      <button
        aria-label="Sonraki"
        onClick={() => go(index + 1, 1)}
        className="absolute right-0 top-0 z-20 h-full w-2/3 cursor-e-resize focus:outline-none"
      />

      {/* Controls */}
      <motion.div
        initial={false}
        animate={{ opacity: showUI ? 1 : 0, y: showUI ? 0 : 12 }}
        transition={{ duration: 0.25 }}
        className="pointer-events-none absolute inset-x-0 bottom-0 z-30 flex items-center justify-center pb-6"
      >
        <div className="glass pointer-events-auto flex items-center gap-1 rounded-2xl px-2 py-2">
          <Ctrl onClick={() => go(index - 1, -1)} disabled={atStart} title="Önceki">
            <ChevronLeft className="h-5 w-5" />
          </Ctrl>

          {/* Dots */}
          <div className="mx-2 flex items-center gap-1.5">
            {slides.map((s, i) => (
              <button
                key={s.id}
                onClick={() => go(i, i > index ? 1 : -1)}
                title={`Slayt ${i + 1}`}
                className={cn(
                  'h-2 rounded-full transition-all',
                  i === index
                    ? 'w-6 bg-white'
                    : 'w-2 bg-white/30 hover:bg-white/60',
                )}
              />
            ))}
          </div>

          <Ctrl onClick={() => go(index + 1, 1)} disabled={atEnd} title="Sonraki">
            <ChevronRight className="h-5 w-5" />
          </Ctrl>

          <div className="mx-1 h-6 w-px bg-white/15" />

          <span className="px-2 text-sm tabular-nums text-white/70">
            {index + 1} / {slides.length}
          </span>

          <Ctrl onClick={exit} title="Düzenleyiciye dön">
            <Pencil className="h-5 w-5" />
          </Ctrl>
        </div>
      </motion.div>

      {/* Exit */}
      <motion.button
        initial={false}
        animate={{ opacity: showUI ? 1 : 0 }}
        onClick={exit}
        title="Çıkış (Esc)"
        className="glass absolute right-5 top-5 z-30 flex h-10 w-10 items-center justify-center rounded-xl text-white/80 transition-colors hover:text-white"
      >
        <X className="h-5 w-5" />
      </motion.button>
    </div>
  )
}

function Ctrl({
  children,
  onClick,
  disabled,
  title,
}: {
  children: React.ReactNode
  onClick: () => void
  disabled?: boolean
  title?: string
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className="flex h-10 w-10 items-center justify-center rounded-xl text-white/80 transition-colors hover:bg-white/10 hover:text-white disabled:opacity-25 disabled:hover:bg-transparent"
    >
      {children}
    </button>
  )
}

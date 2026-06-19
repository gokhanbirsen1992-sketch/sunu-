import { useLayoutEffect, useRef, useState } from 'react'
import type { Slide } from '../lib/types'
import { getTheme } from '../lib/themes'
import { cn } from '../lib/cn'

/** Fixed design canvas — everything is laid out at this size then scaled. */
const W = 1280
const H = 720

/**
 * Renders the slide content at a fixed 1280x720 size. The parent <SlideStage>
 * scales it to fit, so thumbnails, the editor preview and present mode all
 * share pixel-identical layout.
 */
function SlideContent({ slide }: { slide: Slide }) {
  const theme = getTheme(slide.theme)

  return (
    <div
      className={cn(
        'relative h-full w-full overflow-hidden',
        theme.bg,
        'bg-[length:200%_200%] animate-gradient-x',
      )}
      style={{ width: W, height: H }}
    >
      {/* Decorative blurred accents */}
      <div className="pointer-events-none absolute -right-24 -top-24 h-[420px] w-[420px] rounded-full bg-white/15 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-32 -left-20 h-[380px] w-[380px] rounded-full bg-black/20 blur-3xl" />
      {/* Soft vignette for depth */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(120%_120%_at_50%_0%,transparent_55%,rgba(0,0,0,0.28))]" />

      {/* Brand mark */}
      <div className="absolute left-[72px] top-[60px] flex items-center gap-3">
        <div className="h-7 w-7 rounded-lg bg-white/90 shadow-sm" style={{ clipPath: 'polygon(50% 8%, 92% 92%, 8% 92%)' }} />
        <span className={cn('text-[22px] font-semibold tracking-tight', theme.muted)}>
          Aurora
        </span>
      </div>

      <div className="absolute inset-0 flex flex-col justify-center px-[120px] py-[110px]">
        {renderLayout(slide, theme)}
      </div>
    </div>
  )
}

function renderLayout(slide: Slide, theme: ReturnType<typeof getTheme>) {
  switch (slide.layout) {
    case 'title':
      return (
        <div className="max-w-[920px]">
          <div className={cn('mb-8 h-[6px] w-[120px] rounded-full', theme.accent)} />
          <h1 className={cn('text-[92px] font-black leading-[1.02] tracking-tight', theme.text)}>
            {slide.title}
          </h1>
          {slide.subtitle && (
            <p className={cn('mt-8 text-[34px] font-medium leading-snug', theme.muted)}>
              {slide.subtitle}
            </p>
          )}
        </div>
      )

    case 'statement':
      return (
        <div className="mx-auto max-w-[1000px] text-center">
          <h1 className={cn('text-[88px] font-extrabold leading-[1.08] tracking-tight', theme.text)}>
            “{slide.title}”
          </h1>
          {slide.subtitle && (
            <p className={cn('mt-10 text-[30px] font-medium', theme.muted)}>
              {slide.subtitle}
            </p>
          )}
        </div>
      )

    case 'section':
      return (
        <div className="max-w-[960px]">
          {slide.subtitle && (
            <p className={cn('mb-6 text-[28px] font-semibold uppercase tracking-[0.3em]', theme.muted)}>
              {slide.subtitle}
            </p>
          )}
          <h1 className={cn('text-[104px] font-black leading-[1.0] tracking-tight', theme.text)}>
            {slide.title}
          </h1>
          <div className={cn('mt-10 h-[6px] w-[180px] rounded-full', theme.accent)} />
        </div>
      )

    case 'bullets':
      return (
        <div className="max-w-[980px]">
          <h2 className={cn('text-[68px] font-extrabold leading-tight tracking-tight', theme.text)}>
            {slide.title}
          </h2>
          <div className={cn('mt-6 mb-10 h-[5px] w-[96px] rounded-full', theme.accent)} />
          <ul className="space-y-7">
            {(slide.bullets ?? []).filter(Boolean).map((b, i) => (
              <li key={i} className="flex items-start gap-5">
                <span className={cn('mt-[18px] h-[14px] w-[14px] shrink-0 rounded-full', theme.accent)} />
                <span className={cn('text-[40px] font-medium leading-snug', theme.text)}>
                  {b}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )
  }
}

/**
 * Scales SlideContent to fit its container while preserving the 16:9 ratio.
 * Use `fit="height"` (default fills width via aspect box) or pass explicit sizing
 * through className on the wrapper.
 */
export function SlideStage({
  slide,
  className,
  rounded = true,
}: {
  slide: Slide
  className?: string
  rounded?: boolean
}) {
  const ref = useRef<HTMLDivElement>(null)
  const [scale, setScale] = useState(0)

  useLayoutEffect(() => {
    const el = ref.current
    if (!el) return
    const update = () => setScale(el.clientWidth / W)
    update()
    const ro = new ResizeObserver(update)
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  return (
    <div
      ref={ref}
      className={cn(
        'relative aspect-video w-full overflow-hidden',
        rounded && 'rounded-2xl',
        className,
      )}
    >
      <div
        className="absolute left-0 top-0 origin-top-left"
        style={{ width: W, height: H, transform: `scale(${scale})` }}
      >
        <SlideContent slide={slide} />
      </div>
    </div>
  )
}

export { SlideContent }

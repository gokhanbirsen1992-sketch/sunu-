import { Link, useNavigate } from 'react-router-dom'
import {
  Plus,
  Play,
  Trash2,
  Copy,
  ChevronUp,
  ChevronDown,
  Home,
  RotateCcw,
} from 'lucide-react'
import { Button } from '../components/ui/Button'
import { SlideStage } from '../components/SlideStage'
import { useDeck } from '../lib/store'
import { THEMES } from '../lib/themes'
import { LAYOUT_LABELS, type Layout, type Slide } from '../lib/types'
import { cn } from '../lib/cn'

const LAYOUTS = Object.keys(LAYOUT_LABELS) as Layout[]

export default function Editor() {
  const navigate = useNavigate()
  const {
    deck,
    currentId,
    setDeckName,
    select,
    addSlide,
    duplicateSlide,
    deleteSlide,
    updateSlide,
    move,
    resetSample,
  } = useDeck()

  const current = deck.slides.find((s) => s.id === currentId) ?? deck.slides[0]

  return (
    <div className="flex h-screen flex-col bg-[#07070c]">
      {/* Top bar */}
      <header className="flex h-14 shrink-0 items-center gap-3 border-b border-white/10 px-4">
        <Link
          to="/"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-zinc-400 transition-colors hover:bg-white/5 hover:text-white"
          title="Ana sayfa"
        >
          <Home className="h-5 w-5" />
        </Link>
        <input
          value={deck.name}
          onChange={(e) => setDeckName(e.target.value)}
          className="min-w-0 max-w-xs flex-1 rounded-lg bg-transparent px-2 py-1 text-sm font-medium text-zinc-100 outline-none transition-colors hover:bg-white/5 focus:bg-white/5"
          placeholder="Sunum adı"
        />
        <div className="flex-1" />
        <span className="hidden text-xs text-zinc-500 sm:block">
          {deck.slides.length} slayt
        </span>
        <Button variant="ghost" size="sm" onClick={resetSample} title="Örnek sunuya sıfırla">
          <RotateCcw className="h-4 w-4" />
          <span className="hidden md:inline">Sıfırla</span>
        </Button>
        <Button size="sm" onClick={() => navigate('/present')}>
          <Play className="h-4 w-4" />
          Oynat
        </Button>
      </header>

      <div className="flex min-h-0 flex-1">
        {/* Slide list */}
        <aside className="flex w-56 shrink-0 flex-col border-r border-white/10">
          <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
            {deck.slides.map((s, i) => (
              <Thumb
                key={s.id}
                slide={s}
                index={i}
                active={s.id === currentId}
                canUp={i > 0}
                canDown={i < deck.slides.length - 1}
                onSelect={() => select(s.id)}
                onUp={() => move(s.id, -1)}
                onDown={() => move(s.id, 1)}
                onDuplicate={() => duplicateSlide(s.id)}
                onDelete={() => deleteSlide(s.id)}
              />
            ))}
          </div>
          <div className="border-t border-white/10 p-3">
            <Button variant="subtle" size="md" className="w-full" onClick={addSlide}>
              <Plus className="h-4 w-4" />
              Slayt ekle
            </Button>
          </div>
        </aside>

        {/* Canvas */}
        <main className="flex min-w-0 flex-1 items-center justify-center bg-[radial-gradient(circle_at_50%_0%,rgba(99,102,241,0.08),transparent_60%)] p-8">
          <div className="w-full max-w-4xl">
            <div className="rounded-3xl bg-white/[0.02] p-3 shadow-2xl shadow-black/40 ring-1 ring-white/10">
              <SlideStage slide={current} />
            </div>
            <p className="mt-4 text-center text-sm text-zinc-500">
              Düzenlemek için sağ paneli kullan · Tam ekran için “Oynat”
            </p>
          </div>
        </main>

        {/* Inspector */}
        <aside className="w-80 shrink-0 overflow-y-auto border-l border-white/10 p-5">
          <Inspector
            key={current.id}
            slide={current}
            onChange={(patch) => updateSlide(current.id, patch)}
          />
        </aside>
      </div>
    </div>
  )
}

function Thumb({
  slide,
  index,
  active,
  canUp,
  canDown,
  onSelect,
  onUp,
  onDown,
  onDuplicate,
  onDelete,
}: {
  slide: Slide
  index: number
  active: boolean
  canUp: boolean
  canDown: boolean
  onSelect: () => void
  onUp: () => void
  onDown: () => void
  onDuplicate: () => void
  onDelete: () => void
}) {
  return (
    <div
      className={cn(
        'group relative cursor-pointer rounded-xl p-1 ring-1 transition-all',
        active
          ? 'ring-2 ring-violet-400'
          : 'ring-white/10 hover:ring-white/25',
      )}
      onClick={onSelect}
    >
      <div className="absolute left-2 top-2 z-10 rounded-md bg-black/40 px-1.5 text-xs font-medium text-white/80 backdrop-blur">
        {index + 1}
      </div>
      <SlideStage slide={slide} rounded />
      {/* Hover actions */}
      <div className="absolute right-1.5 top-1.5 z-10 flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
        <MiniBtn disabled={!canUp} onClick={onUp} title="Yukarı">
          <ChevronUp className="h-3.5 w-3.5" />
        </MiniBtn>
        <MiniBtn disabled={!canDown} onClick={onDown} title="Aşağı">
          <ChevronDown className="h-3.5 w-3.5" />
        </MiniBtn>
        <MiniBtn onClick={onDuplicate} title="Çoğalt">
          <Copy className="h-3.5 w-3.5" />
        </MiniBtn>
        <MiniBtn onClick={onDelete} title="Sil" danger>
          <Trash2 className="h-3.5 w-3.5" />
        </MiniBtn>
      </div>
    </div>
  )
}

function MiniBtn({
  children,
  onClick,
  disabled,
  danger,
  title,
}: {
  children: React.ReactNode
  onClick: () => void
  disabled?: boolean
  danger?: boolean
  title?: string
}) {
  return (
    <button
      title={title}
      disabled={disabled}
      onClick={(e) => {
        e.stopPropagation()
        onClick()
      }}
      className={cn(
        'flex h-6 w-6 items-center justify-center rounded-md bg-black/50 text-white/80 backdrop-blur transition-colors hover:bg-black/70 disabled:opacity-30',
        danger && 'hover:bg-red-500/80 hover:text-white',
      )}
    >
      {children}
    </button>
  )
}

function Inspector({
  slide,
  onChange,
}: {
  slide: Slide
  onChange: (patch: Partial<Slide>) => void
}) {
  return (
    <div className="space-y-7">
      {/* Layout */}
      <Section title="Düzen">
        <div className="grid grid-cols-2 gap-2">
          {LAYOUTS.map((l) => (
            <button
              key={l}
              onClick={() => onChange({ layout: l })}
              className={cn(
                'rounded-lg border px-3 py-2 text-sm font-medium transition-all',
                slide.layout === l
                  ? 'border-violet-400 bg-violet-500/15 text-white'
                  : 'border-white/10 text-zinc-400 hover:border-white/25 hover:text-white',
              )}
            >
              {LAYOUT_LABELS[l]}
            </button>
          ))}
        </div>
      </Section>

      {/* Theme */}
      <Section title="Tema">
        <div className="grid grid-cols-3 gap-2.5">
          {THEMES.map((t) => (
            <button
              key={t.id}
              onClick={() => onChange({ theme: t.id })}
              title={t.name}
              className={cn(
                'group relative h-14 overflow-hidden rounded-xl ring-2 transition-all',
                slide.theme === t.id
                  ? 'ring-white scale-[1.03]'
                  : 'ring-transparent hover:ring-white/40',
              )}
            >
              <span className={cn('block h-full w-full bg-gradient-to-br', t.chip)} />
              <span className="absolute inset-x-0 bottom-0 truncate bg-black/30 px-1 py-0.5 text-center text-[10px] font-medium text-white backdrop-blur-sm">
                {t.name}
              </span>
            </button>
          ))}
        </div>
      </Section>

      {/* Text fields */}
      <Section title="İçerik">
        <Field label={slide.layout === 'statement' ? 'Vurgu metni' : 'Başlık'}>
          <Textarea
            value={slide.title}
            onChange={(v) => onChange({ title: v })}
            rows={slide.layout === 'statement' ? 3 : 2}
            placeholder="Başlığı yaz…"
          />
        </Field>

        {slide.layout !== 'bullets' && (
          <Field
            label={
              slide.layout === 'section'
                ? 'Üst etiket'
                : slide.layout === 'statement'
                  ? 'İmza / kaynak'
                  : 'Alt başlık'
            }
          >
            <Textarea
              value={slide.subtitle ?? ''}
              onChange={(v) => onChange({ subtitle: v })}
              rows={2}
              placeholder="İsteğe bağlı…"
            />
          </Field>
        )}

        {slide.layout === 'bullets' && (
          <Field label="Maddeler">
            <BulletsEditor
              bullets={slide.bullets ?? []}
              onChange={(bullets) => onChange({ bullets })}
            />
          </Field>
        )}
      </Section>
    </div>
  )
}

function BulletsEditor({
  bullets,
  onChange,
}: {
  bullets: string[]
  onChange: (b: string[]) => void
}) {
  const set = (i: number, v: string) =>
    onChange(bullets.map((b, idx) => (idx === i ? v : b)))
  const remove = (i: number) => onChange(bullets.filter((_, idx) => idx !== i))
  const add = () => onChange([...bullets, ''])

  return (
    <div className="space-y-2">
      {bullets.map((b, i) => (
        <div key={i} className="flex items-center gap-2">
          <input
            value={b}
            onChange={(e) => set(i, e.target.value)}
            placeholder={`Madde ${i + 1}`}
            className="min-w-0 flex-1 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-zinc-100 outline-none transition-colors focus:border-violet-400/60 focus:bg-white/[0.06]"
          />
          <button
            onClick={() => remove(i)}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-zinc-500 transition-colors hover:bg-red-500/15 hover:text-red-300"
            title="Maddeyi sil"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      ))}
      <Button variant="subtle" size="sm" className="w-full" onClick={add}>
        <Plus className="h-3.5 w-3.5" />
        Madde ekle
      </Button>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-500">
        {title}
      </h3>
      {children}
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="mb-3 block">
      <span className="mb-1.5 block text-sm text-zinc-400">{label}</span>
      {children}
    </label>
  )
}

function Textarea({
  value,
  onChange,
  rows = 2,
  placeholder,
}: {
  value: string
  onChange: (v: string) => void
  rows?: number
  placeholder?: string
}) {
  return (
    <textarea
      value={value}
      rows={rows}
      placeholder={placeholder}
      onChange={(e) => onChange(e.target.value)}
      className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-sm leading-relaxed text-zinc-100 outline-none transition-colors focus:border-violet-400/60 focus:bg-white/[0.06]"
    />
  )
}

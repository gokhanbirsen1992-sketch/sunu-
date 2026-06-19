import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ArrowRight,
  Sparkles,
  Wand2,
  Palette,
  MonitorPlay,
  Layers,
  Zap,
  MousePointerClick,
  Github,
} from 'lucide-react'
import { Button } from '../components/ui/Button'
import { SlideStage } from '../components/SlideStage'
import { sampleDeck } from '../lib/sampleDeck'

const features = [
  {
    icon: MonitorPlay,
    title: 'Sinematik geçişler',
    desc: 'Prezi tarzı zoom & fade animasyonlarıyla slaytlar arasında akıcı geçişler.',
  },
  {
    icon: Palette,
    title: 'Hazır temalar',
    desc: 'Tek tıkla profesyonel gradyan temalar. Renk paletiyle uğraşmana gerek yok.',
  },
  {
    icon: Wand2,
    title: 'Anında düzenleme',
    desc: 'Tarayıcıda yaz, gör, değiştir. Kurulum, hesap, bekleme yok.',
  },
  {
    icon: Layers,
    title: 'Akıllı düzenler',
    desc: 'Başlık, vurgu, madde ve bölüm düzenleri içeriğini otomatik hizalar.',
  },
  {
    icon: Zap,
    title: 'Şimşek hızında',
    desc: 'Saf React + Tailwind. Tarayıcıdan başka hiçbir şeye ihtiyaç yok.',
  },
  {
    icon: MousePointerClick,
    title: 'Klavyeyle sun',
    desc: 'Ok tuşları, boşluk ve ESC ile sunumunu pürüzsüz yönet.',
  },
]

const steps = [
  { n: '01', title: 'Slaytını yaz', desc: 'Başlık ve maddeleri ekle, düzeni seç.' },
  { n: '02', title: 'Temanı seç', desc: 'Hazır gradyanlardan birini tek tıkla uygula.' },
  { n: '03', title: 'Oynat & büyüle', desc: 'Tam ekran sinematik sunum moduna geç.' },
]

export default function Landing() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      <Background />

      {/* Nav */}
      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2.5">
          <Logo />
          <span className="text-lg font-semibold tracking-tight">Aurora</span>
        </div>
        <nav className="hidden items-center gap-8 text-sm text-zinc-400 md:flex">
          <a href="#features" className="transition-colors hover:text-white">
            Özellikler
          </a>
          <a href="#how" className="transition-colors hover:text-white">
            Nasıl çalışır
          </a>
          <a
            href="https://github.com/gokhanbirsen1992-sketch/sunu-"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 transition-colors hover:text-white"
          >
            <Github className="h-4 w-4" /> Kaynak
          </a>
        </nav>
        <Link to="/editor">
          <Button size="sm">Düzenleyiciye git</Button>
        </Link>
      </header>

      {/* Hero */}
      <section className="relative z-10 mx-auto max-w-7xl px-6 pb-16 pt-14 md:pt-24">
        <div className="grid items-center gap-14 lg:grid-cols-2">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="glass mb-7 inline-flex items-center gap-2 rounded-full px-3.5 py-1.5 text-sm text-zinc-300"
            >
              <Sparkles className="h-3.5 w-3.5 text-fuchsia-300" />
              Prezi'nin akışı, modern web'in zarafetiyle
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.05 }}
              className="text-5xl font-black leading-[1.05] tracking-tight md:text-7xl"
            >
              Sunularını{' '}
              <span className="text-gradient bg-gradient-to-r from-indigo-400 via-fuchsia-400 to-rose-400">
                canlandır.
              </span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.12 }}
              className="mt-6 max-w-xl text-lg leading-relaxed text-zinc-400"
            >
              Aurora, tarayıcıda saniyeler içinde sinematik sunular hazırlamanı
              sağlayan modern bir sunum stüdyosu. Şablon, kurulum ve tasarım
              bilgisi gerektirmez.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.18 }}
              className="mt-9 flex flex-wrap items-center gap-3"
            >
              <Link to="/editor">
                <Button size="lg" className="group">
                  Ücretsiz başla
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </Button>
              </Link>
              <Link to="/present">
                <Button size="lg" variant="outline">
                  <MonitorPlay className="h-4 w-4" />
                  Demoyu oynat
                </Button>
              </Link>
            </motion.div>

            <p className="mt-5 text-sm text-zinc-500">
              Kayıt yok · Ücretsiz · Tüm sunular tarayıcında saklanır
            </p>
          </div>

          {/* Floating preview */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, rotate: -2 }}
            animate={{ opacity: 1, scale: 1, rotate: 0 }}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            className="relative"
          >
            <div className="absolute -inset-6 -z-10 rounded-[2rem] bg-gradient-to-tr from-indigo-500/20 via-fuchsia-500/20 to-rose-500/20 blur-2xl" />
            <motion.div
              animate={{ y: [0, -12, 0] }}
              transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
              className="glass rounded-3xl p-3 shadow-2xl shadow-black/50"
            >
              <SlideStage slide={sampleDeck.slides[0]} />
            </motion.div>
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
              className="glass absolute -bottom-10 -left-8 w-44 rounded-2xl p-2 shadow-xl shadow-black/50 sm:w-56"
            >
              <SlideStage slide={sampleDeck.slides[2]} />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="relative z-10 mx-auto max-w-7xl px-6 py-24">
        <SectionHeading
          kicker="Özellikler"
          title="Güzel sunum için gereken her şey"
          subtitle="Karmaşık araçlara veda et. Aurora sadeliği ve estetiği bir araya getirir."
        />
        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 22 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.5, delay: i * 0.06 }}
              className="glass group rounded-2xl p-6 transition-colors hover:border-white/20"
            >
              <div className="mb-4 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/20 to-fuchsia-500/20 ring-1 ring-white/10">
                <f.icon className="h-5 w-5 text-fuchsia-300" />
              </div>
              <h3 className="text-lg font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-400">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="relative z-10 mx-auto max-w-7xl px-6 py-24">
        <SectionHeading
          kicker="Nasıl çalışır"
          title="Üç adımda sahnedesin"
          subtitle="Fikirden sunuma birkaç dakika."
        />
        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {steps.map((s, i) => (
            <motion.div
              key={s.n}
              initial={{ opacity: 0, y: 22 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="relative rounded-2xl border border-white/10 bg-white/[0.02] p-8"
            >
              <span className="text-gradient bg-gradient-to-r from-indigo-400 to-fuchsia-400 text-5xl font-black">
                {s.n}
              </span>
              <h3 className="mt-4 text-xl font-semibold">{s.title}</h3>
              <p className="mt-2 text-zinc-400">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA band */}
      <section className="relative z-10 mx-auto max-w-7xl px-6 pb-28">
        <div className="glass relative overflow-hidden rounded-3xl px-8 py-16 text-center md:py-20">
          <div className="absolute inset-0 -z-10 bg-gradient-to-br from-indigo-600/20 via-violet-600/15 to-fuchsia-600/20" />
          <h2 className="mx-auto max-w-2xl text-3xl font-bold tracking-tight md:text-5xl">
            İlk sununu hazırlamaya hazır mısın?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-zinc-400">
            Bir konu seç, birkaç slayt yaz, “Oynat”a bas. Gerisini Aurora halleder.
          </p>
          <Link to="/editor" className="mt-8 inline-block">
            <Button size="lg" className="group">
              Hemen başla
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 py-8 text-sm text-zinc-500 sm:flex-row">
          <div className="flex items-center gap-2">
            <Logo small />
            <span>Aurora — Modern Sunum Stüdyosu</span>
          </div>
          <span>React · Tailwind · Framer Motion ile yapıldı</span>
        </div>
      </footer>
    </div>
  )
}

function SectionHeading({
  kicker,
  title,
  subtitle,
}: {
  kicker: string
  title: string
  subtitle: string
}) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      <span className="text-sm font-semibold uppercase tracking-[0.25em] text-fuchsia-300/80">
        {kicker}
      </span>
      <h2 className="mt-3 text-3xl font-bold tracking-tight md:text-4xl">{title}</h2>
      <p className="mt-3 text-zinc-400">{subtitle}</p>
    </div>
  )
}

function Logo({ small = false }: { small?: boolean }) {
  return (
    <div
      className={small ? 'h-5 w-5' : 'h-8 w-8'}
      style={{
        background:
          'linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%)',
        borderRadius: small ? 6 : 10,
        WebkitMaskImage: 'none',
      }}
    >
      <div
        className="h-full w-full"
        style={{
          background: 'white',
          clipPath: 'polygon(50% 22%, 78% 76%, 22% 76%)',
          opacity: 0.95,
          transform: 'scale(0.62)',
        }}
      />
    </div>
  )
}

function Background() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-0">
      <div className="absolute inset-0 bg-[#07070c]" />
      {/* Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:64px_64px] [mask-image:radial-gradient(ellipse_at_center,black,transparent_75%)]" />
      {/* Blobs */}
      <div className="absolute -left-32 top-[-10%] h-[480px] w-[480px] animate-float-slow rounded-full bg-indigo-600/25 blur-[120px]" />
      <div className="absolute right-[-10%] top-[10%] h-[460px] w-[460px] animate-float-slower rounded-full bg-fuchsia-600/20 blur-[120px]" />
      <div className="absolute bottom-[-10%] left-[30%] h-[420px] w-[420px] animate-float-slow rounded-full bg-rose-500/15 blur-[120px]" />
    </div>
  )
}

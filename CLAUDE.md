# Claude Code Project Setup

PaperForge — SPSS'ten Makaleye Otomatik Pipeline

## Installed Skills

Bu proje aşağıdaki skills ile donatılmıştır:

### 1. `/karpathy-guidelines`
**Andrej Karpathy Kodlama Rehberi**

LLM kodlama hatalarını azaltmak için davranışsal rehberler:
- Varsayımları açık hale getir
- Basitliği ön planda tut
- Cerrahi değişiklikler yap
- Başarı kriterlerini tanımla

Kaynak: [andrej-karpathy-skills](https://github.com/gokhanbirsen1992-sketch/andrej-karpathy-skills)

### 2. `/ian-xiaohei-illustrations`
**Ian Tarzı Çince Artikel Görselleri**

中文正文配图 — Çince makaleler, yazılar, bloglar için orijinal stil görseller:
- Xiaohei IP karakteri
- El çizimi estetik
- Minimal red/orange/blue notasyonlar
- Hayal gücü ile beraber temiz görünüm

Kaynak: [ian-xiaohei-illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations)

### 3. `/find-skills`
**Skill Discovery Tool**

Yeni skilllar bulmak ve kurmak için kullan.

## Skills Konumu

- **Local (Project):** `.claude/skills/`
- **Global:** `~/.agents/skills/`

Her oturumda bu skills otomatik olarak yüklenmiştir.

## Kullanım

```bash
# Slash komutu ile erişim
/karpathy-guidelines
/ian-xiaohei-illustrations
/find-skills
```

## Kalıcılık

Tüm skills git repository'sine commit'lenmiştir:
```
commit de990c8
Add installed skills: karpathy-guidelines and ian-xiaohei-illustrations
```

Branch: `claude/karpathy-skills-repo-1d06q0`

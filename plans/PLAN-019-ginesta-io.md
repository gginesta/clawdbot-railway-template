# PLAN-019: ginesta.io — Family Landing Page

**Created:** 2026-03-24 | **Completed:** 2026-03-24 | **Status:** ✅ Done | **Owner:** Molty 🦎
**Source:** Webchat conversation with Guillermo, 2026-03-24 01:14–02:09 HKT

---

## Scope (from conversation)

**ginesta.io** is a family landing page — NOT a personal portfolio. It routes visitors to the right destination.

### Agreed decisions:
1. **Brand:** "GINESTA" — clean, like a house name
2. **Style:** Sleek, lean, minimal. Match Mana Capital's quality bar (warm, editorial, premium)
3. **Landing page:** Four cards with consistent one-liners, each routing deeper
4. **Hosting:** Vercel (git-push deploys, free tier)
5. **Steph's name:** Stephanie Rose (not Ginesta)

### Architecture:
```
ginesta.io                → Minimal landing page (4 cards)
├── /guillermo            → Personal profile (Brinc-forward, Cerebro, speaking) — sub-page
├── → manacapital.io      → External link (already built, Webflow)
├── → helmcl.com          → External link (placeholder to build later)
└── → Steph's site        → Placeholder / "coming soon"
```

### Card content (all cards get one-liner — consistent treatment):
| Card | Name | One-liner | Links to |
|------|------|-----------|----------|
| 1 | Guillermo Ginesta | Investor, builder, operator | /guillermo |
| 2 | Mana Capital | Private investment firm | manacapital.io |
| 3 | Helm Consulting | Advisory & investments | helmcl.com (placeholder) |
| 4 | Stephanie Rose | Counselling & therapy | Coming soon |

### Key context:
- **Mana Capital** = Guillermo's holdco (BVI + HK). Long-term play. Has full site at manacapital.io (Webflow, warm/editorial/premium design)
- **Helm Consulting** = Father's (Guillermo Ginesta IV) holdco. Guillermo is 50% shareholder, director, chairman. Sectors: logistics, shipping, sports & hospitality, infrastructure, agriculture
- **Guillermo's profile** = Brinc-forward (Managing Partner, Asia Pacific). Cerebro mentioned but subtle. Mana Capital mentioned but not headline. LinkedIn stays Brinc-focused for now
- **Steph** = Building her counselling practice. Site coming soon. Separate thing entirely

### Design reference:
- Match manacapital.io aesthetic: warm cream/stone textures, serif headlines, warm gold accents, extreme whitespace
- Luxury minimalism — restrained, confident
- Color palette: off-white/cream (#EDE8DC), charcoal (#1E1C1A), warm gold (#A07850)
- Fonts: editorial serif (Cormorant Garamond) + geometric sans (Montserrat)

---

## Build Plan

### Phase 1: Landing page (TODAY)
1. Create static site: HTML + CSS (no framework needed for this)
2. Four cards with hover effects
3. Responsive (desktop + mobile)
4. Deploy to Vercel via GitHub repo
5. Share preview URL with Guillermo

### Phase 2: /guillermo profile page (TODAY if time)
1. Bio section (Brinc-led, Cerebro, track record)
2. Contact section
3. Keep it elegant and consistent with landing

### Phase 3: DNS + go-live (needs Guillermo)
1. Point ginesta.io DNS to Vercel
2. Needs Namecheap credentials or Guillermo to update nameservers

---

## NOT in scope (per conversation)
- helmcl.com (separate build, later)
- Steph's website (she's building it)
- manacapital.io (already done)

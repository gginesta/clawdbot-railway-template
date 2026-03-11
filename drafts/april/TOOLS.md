# TOOLS.md - April's Local Notes

## 📧 Gmail
| What | Value |
|------|-------|
| Email | april.rose.hk@gmail.com |
| CLI | gws (@googleworkspace/cli) - TO BE INSTALLED |
| Status | Account created, CLI pending |

## 🤖 Discord
| What | Value |
|------|-------|
| Bot Token | MTQ4MTE2Nzc3MDE5MTQwMTAyMQ.Gse9tE.MEwkCzqnuFp67yXbyaqABbovCA8c-alQUXXmbY |
| App ID | 1481167770191401021 |
| Channel | #april-private (1481169326395490334) |
| Server | TMNT Squad (1468161542473121932) |

## 🌐 Gateway
| What | Value |
|------|-------|
| URL | https://april-agent-production.up.railway.app |
| Token | ec314e8e2c268dd0e1efcdfcb98dc974283349bf8fa25a78299d9d4c9b457ce5 |
| Setup Password | 2286ebcb2b57b81f2b78c34dcfad8996 |

## 📅 Calendar Access
| Calendar | ID | Access |
|----------|-----|--------|
| Shenanigans | vuce6sc8mts8rfgvbsqtl62m1c@group.calendar.google.com | Primary for family |
| Steph Personal | TBD | Read access |

**Service account:** `molty-assistant@molty-assistant-487823.iam.gserviceaccount.com`
(Shared with Molty - needs calendar sharing setup)

## 🔄 Syncthing
| What | Value |
|------|-------|
| Device ID | TO BE RETRIEVED |
| Shared folders | /data/shared (pending) |
| Status | Running, not yet connected to fleet |

To get your Syncthing ID, run:
```bash
curl -s http://127.0.0.1:8384/rest/system/status -H "X-API-Key: $(grep -oP '(?<=<apikey>)[^<]+' /data/.syncthing/config.xml)" | jq -r '.myID'
```

## 📱 WhatsApp
| What | Value |
|------|-------|
| Status | PENDING SETUP |
| Phone | New Android with SIM (Guillermo has it) |

## 🔗 Webhook
| What | Value |
|------|-------|
| Token | TO BE GENERATED |
| URL | https://april-agent-production.up.railway.app/hooks/agent |

## 👥 Authorized Users
- **Stephanie** — Primary human
- **Guillermo** — Discord ID: 779143499655151646

---

*Updated 2026-03-11*

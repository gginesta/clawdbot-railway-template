## 📁 Syncthing Shared Folders

### Architecture
Project-specific shares for isolation (not one big `/data/shared` folder).

### Folder IDs
| Folder ID | Path | Type | Shared With |
|-----------|------|------|-------------|
| `shared` | `/data/shared` | sendreceive | Raphael + Guillermo |
| `mv-daily` | `/data/shared/memory-vault/daily` | sendreceive | All |
| `mv-projects` | `/data/shared/memory-vault/knowledge/projects` | sendreceive | All |
| `mv-resources` | `/data/shared/memory-vault/knowledge/resources` | sendonly | All |
| `mv-squad` | `/data/shared/memory-vault/knowledge/squad` | sendonly | All |
| `mv-people` | `/data/shared/memory-vault/knowledge/people` | sendonly | All |

**Status:** ✅ WORKING (fixed 2026-02-04 14:32 UTC)
**Root cause:** Folder ID mismatch (`brinc-kb` vs `shared`). Changed Molty's folder to match Raphael's.
**Note:** `shared` folder overlaps with mv-* folders. Works but may need cleanup later.

### Device IDs
| Device | ID | Syncthing Status |
|--------|-----|------------------|
| Molty-Railway | `3SM5RVG-SI2I5NF-EVETYF4-NIHFBDO-4244FJH-GSAAYNA-RUXA4UA-ZIEBBQU` | ✅ Active |
| Raphael-Railway | `SA5L4UC-JDKR64B-ATFEIZT-FDZ5IU5-ZNXCG2R-AQUQAJU-DZYLPSB-OPCETAN` | ✅ Active |
| Leonardo-Railway | `ORN3YZG-X26ZTDR-RESO4XZ-T6LBPON-BFTLETF-NC2JGRF-GGCE4GZ-ILJBFAL` | ✅ Active |
| Guillermo-PC | `NSIAS7W-YAOTA6B-7A5I43O-6JCQHM7-ET4SPCF-6TB73UA-APHNHS5-2QLTVQP` | ✅ Active |

### Config Location
- Config: `/data/.syncthing/config.xml`
- API Key: `molty-syncthing-key`
- GUI: `http://localhost:8384`

---

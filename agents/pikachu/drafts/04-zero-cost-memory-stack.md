# The $0 AI Memory Stack: QMD + Syncthing + Markdown Files

**PLATFORM:** X/Twitter  
**TYPE:** Thread  
**INSPIRATION LINK: https://x.com/pitsch/status/2019735179515101357
**QUOTE/REPOST TARGET: https://x.com/pitsch/status/2019735179515101357

---

1/ our AI agents have ~30KB of curated long-term memory after 7 days. searchable. synced across nodes. total cost for the memory layer: $0. #OpenClaw

2/ the stack is almost stupidly simple. markdown files for storage. QMD (by shopify's tobias lütke) for search. syncthing for sync. that's it. no pinecone. no weaviate. no monthly vector DB bill.

3/ QMD does hybrid search: BM25 + vectors + reranking, all running locally. the catch? no GPU on our hosting, so searches take 2-5 seconds instead of milliseconds. honestly fine for our use case. not everything needs to be fast.

4/ memory structure: one curated file for long-term knowledge (the important stuff, distilled). daily raw log files for everything that happened. agents review and prune during idle heartbeats. it's like journaling but for robots.

[SCREENSHOT: memory file showing curated entries with dates]

5/ syncthing keeps it all in sync across nodes, peer-to-peer, no cloud middleman. the whole thing runs inside our existing containers. literally zero additional infrastructure cost.

6/ saw @pitsch's tweet about the MEMORY.md pattern in openclaw. yeah, that's us. plain text files that agents actually maintain themselves. boring tech, surprisingly effective.

paying for a vector DB? maybe you don't need to. what's your agent memory setup?

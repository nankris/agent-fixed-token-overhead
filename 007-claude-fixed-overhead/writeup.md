# Claude Code sends 23K tokens before you say anything. Two flags cut it in half.

*Draft. Tech in General experiment #007. 24 headless Claude Code runs on 2026-10-15 (IST).*

I asked Claude Code 2.1.300 (Opus 5.5, Pro login) to "Reply with just: OK" in an empty folder, and read how big the request was. Then I switched things off one flag at a time.

| What's on | Tokens sent |
|---|---|
| Everything (3 claude.ai connectors, 9 skills, all tools) | **23.5K** |
| No MCP connectors (`--strict-mcp-config`) | 16.5K |
| …and no skills (`--disable-slash-commands`) | 11.4K |
| …and only Bash, Read, Edit | 5.6K |
| …and no tools at all | 2.8K |
| …and a one-line system prompt | 0.6K |

Where the 23.5K goes, roughly: connectors 7K, skills 5K, the "other" built-in tools 5.7K, Bash/Read/Edit 2.9K, Claude Code's own instructions 2.2K.

**Why it matters.** That prefix rides along on every model call. A task that takes 10 calls pays for it 10 times (mostly at the cache-read price, but the first write is at the 1-hour cache rate, 2× normal input). At API list prices the first call dropped from about 12¢ to 3¢ just by not loading connectors and skills I wasn't using. On Pro it's usage-window share, not dollars.

**What I'd do.** For scripted/headless runs, add `--strict-mcp-config --disable-slash-commands` unless you need them. Trimming the tool list saves more, but it changes what the agent can do, so test it on your tasks first.

*Cost figures are API-equivalent estimates from Claude Code's own `total_cost_usd`; Pro isn't billed per token.*

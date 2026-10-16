# #007 Measure your fixed overhead (Claude Code CLI)

**Question.** How many tokens does Claude Code send before you've asked anything, and how much of that can you trim with CLI flags?

**Short answer.** On a one-word reply ("Reply with just: OK") in an empty folder, default Claude Code 2.1.300 sent **~23.5K prompt tokens** (one run 18.7K). Trimming with flags took it down step by step: `--strict-mcp-config` (drops the 3 claude.ai connectors) **16.5K**, `+ --disable-slash-commands` (drops skills) **11.4K**, `+ --tools Bash,Read,Edit` **5.6K**, `+ --tools ""` **2.8K**, and replacing the system prompt with one line **555**. So on this account: MCP connectors ≈ 7K, skills/slash commands ≈ 5K, the 14 built-in tools beyond Bash/Read/Edit ≈ 5.7K, Bash+Read+Edit schemas ≈ 2.9K, Claude Code's own system prompt ≈ 2.2K. API-equivalent est. cost of that first call fell from **$0.12 to $0.03** with the two "free" flags (strict MCP + no slash commands) and to under half a cent fully stripped.

The cited known result was ~39K before customisation and +2.9K for 85 skills; this build's base is far smaller (≈11K with tools, no MCP, no skills), but it's the same shape: tool schemas + connectors dominate.

## Setup
- Claude Code 2.1.300, default model `claude-opus-5-5` (Claude Pro sign-in), headless `claude -p "Reply with just: OK" --output-format stream-json --verbose --dangerously-skip-permissions --no-session-persistence`, run in an empty temp dir. 3 reps per condition, 3 at a time, 2026-10-14 ~19:42 UTC (01:12 IST 15 Oct).
- The account has 3 claude.ai MCP connectors (Claude Docs, iHatePosting, Magnific) and 9 synced skills (docs, docx, google-workspace, import-memory, morning, pdf, pptx, skill-creator, xlsx). No CLAUDE.md, no hooks.
- "Prompt tokens" = input + cache_creation + cache_read from Claude's final `usage` (one model call per run, so this is the full first-request size).
- Est. $ = Claude Code's own `total_cost_usd` (list API price). **API-equivalent estimate only**: Pro isn't billed per token. Implied rates from the runs: ~$4/M input, **$8/M cache write** (Claude Code writes the 1-hour cache, `ephemeral_1h`, 2× base), $0.20/M cache read, ~$20/M output.
- `--bare` was not tested: it ignores OAuth and needs an API key.

## Exact commands
```bash
source /workspace/tools/setup.sh
scripts/harness/driver_cc.sh scripts/jobs.txt 3 results/driver.log
/workspace/tools/mlenv/bin/python scripts/analyze.py
```

## Results (24 runs, all replied "OK")
| Condition | Prompt tokens (median) | cache write | cache read | Est. $ (median) |
|---|---|---|---|---|
| default | 23,534 (18,686–23,536) | 14,926 | 8,606 | $0.121 |
| --strict-mcp-config | 16,452 | 7,844 | 8,606 | $0.065 |
| --safe-mode (alone) | 13,621 | 5,013 | 8,606 | $0.042 |
| strict + --disable-slash-commands | 11,387 | 3,402 | 7,983 | $0.029 |
| … + --exclude-dynamic-system-prompt-sections | 11,198 | 3,213 | 7,983 | $0.027 |
| … + --tools Bash,Read,Edit | 5,647 | 5,643 | 0 | $0.045 |
| … + --tools "" | 2,769 | 2,118 | 649 | $0.017 |
| … + --system-prompt "You are a helpful assistant." | 555 | 553 | 0 | $0.0045 |

`results/summary.csv`, `results/runs.csv`, raw stream-json in `results/raw/`. Chart: `results/chart.png`.

## Caveats
- Cost per call depends on the cache: the `--tools Bash,Read,Edit` arm is *smaller* but cost *more* than the arm above it because its prefix was new (all cache write, no read). Across a session the size matters more than the first-call price.
- One default run was 4.8K smaller (18.7K); MCP connector tool lists likely loaded late or partially. 3 reps only.
- Trimming tools changes what the agent can do; this measures overhead, not task quality. Later experiments (#015, #017) run with default tools + `--strict-mcp-config`.
- Plugin rows #001–003, #005 skipped (see the Claude-run summary).

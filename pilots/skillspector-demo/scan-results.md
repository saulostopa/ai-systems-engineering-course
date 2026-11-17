# Scan of all repository skills

`gate-skill-scan.sh --all` · SkillSpector `v2.11.2` · static (`--no-llm`) ·
2026-09-17

**41 targets** scanned — skills appear in copies (`.claude/skills/`,
`.agents/skills/`, `skills-artifacts/`, `app-harness/`, `area-copilot/`,
`domains/`), and each copy is scanned on its own, because copies diverge.

```
SKILL GUARD OK — 40 aprovada(s), 1 com aviso, 0 bloqueada(s)   (exit 0)
```

## Result

| Target | Score | Severity | Findings |
|---|---|---|---|
| `.agents/skills/archify` (vendored, with baseline) | 22/100 | MEDIUM | 2 |
| `.agents/skills/agenfk` · `.claude/skills/agenfk` | 11/100 | LOW | 2 |
| `.agents/skills/agenfk-test` · `.claude/skills/agenfk-test` | 7/100 | LOW | 1 |
| `skills-artifacts/feature-archify` | 7/100 | LOW | 1 |
| `.agents/skills/agenfk-pr` · `.claude/skills/agenfk-pr` | 6/100 | LOW | 1 |
| `.claude/skills/agenfk-flow` | 6/100 | LOW | 1 |
| other 32 targets | 0/100 | LOW | 0 |

Only one is above the warning threshold — and it is the **only third-party**
skill in the repository. That is not a coincidence: the others were born here,
in reviewed PRs.

### Bonus: the copies diverged

`.claude/skills/agenfk-flow` scores 6/100 and `.agents/skills/agenfk-flow`
scores 0/100. It is not scanner noise — the files **are different**:

```
- compatibility: all            (.agents — CLI-only version, current)
+ compatibility: claude-code    (.claude — old version, MCP-oriented)
```

The old copy documents `list_projects()` via MCP and the `curl
http://localhost:3000` that the new one forbids — hence the `E1` finding.

This only surfaced because the gate names the report by **path**. In the first
version it used the basename, and `.claude/skills/agenfk-flow` overwrote
`.agents/skills/agenfk-flow`: half of the results silently disappeared and the
drift between the two trees would have stayed invisible.

## The LOW findings — all triaged

| Skill | Rule | What matched | Verdict |
|---|---|---|---|
| `agenfk` | `EA2` Autonomous Decision Making x2 | the expression *"without asking"* in the `SKILL.md` | Legitimate observation about autonomy, not a defect. The skill does describe when the agent acts without asking. |
| `agenfk-flow` | `E1` External Transmission | `curl http://localhost:3000` | **False positive with irony**: the matched line is the one that **forbids** that bypass route. The scanner flags the example inside the prohibition. |
| `agenfk-pr` | `RA2` Session Persistence | the text of the `description` itself | False positive — collision with the description's vocabulary. |
| `agenfk-test`, `feature-archify` | `RP1` MCP Rug Pull | — (no snippet, confidence 0.7) | False positive: neither declares an MCP tool. |

None required action. All below the warning threshold (20).

## `archify` — 100/100 CRITICAL, and what that really means

The gate rejected a skill **that was already installed in this repository**
since commit `5a485aa`. That is the pilot's most useful demonstration: the
gate arrived after the skill and found what no one had looked at.

But 100/100 does not mean "malicious". Opening the 59 findings one by one:

| Rule | Count | What really matched | Verdict |
|---|---|---|---|
| `AE1` analysis-evasion | 13 | `bin/archify.mjs` (2101 lines), `assets/template.html` (14934 lines) above the per-file inspection limit | **Coverage signal**, not evasion |
| `RA2` Session Persistence | 8 | the JavaScript identifier `pList` | False positive |
| `PE3` Credential Access | 7 | `/etc/passwd`, `secret.txt`, `access tokens` — **inside `test/`** | False positive (fixtures) |
| `EA3` Scope Creep | 7 | the **`NOT LIMITED TO`** phrase from the SIL Open Font license text | False positive |
| `P2` Hidden Instructions | 6 | HTML/SVG comments (`<!-- Toolbar -->`, `<!-- Legend -->`) | False positive |
| `YR4` YARA MCP tool poisoning | 6 | the base64 of the embedded WOFF2 font (`d09GMg` = magic `wOF2`) + `description =` from the CSS | False positive |
| `RP1` MCP Rug Pull | 6 | test files; archify is not an MCP server | False positive |
| `TM1`, `MP3`, `OH3`, `LP3` | 4 | `"remove"`, `"reset state"`, `"without cutting"` in tests | False positive |
| `SC1` Unpinned Dependencies | 1 | `"ajv": "^8.17.1"` without an exact pin | **True**, minor |
| `SC4` Known Vulnerable Dependency | 1 | **`fast-uri@3.1.5`, 4 advisories** (via `ajv@8.20.0`) | **TRUE AND ACTIONABLE** |

**58 of 59 were noise. 1 was real.**

The real finding, verified in `.agents/skills/archify/package-lock.json:41`:

```
node_modules/ajv           -> 8.20.0   (dependency: fast-uri ^3.0.1)
node_modules/ajv/node_modules/fast-uri -> 3.1.5
```

`fast-uri@3.1.5` carries CVE-2026-75931 (host confusion from skipped IDN
canonicalization), CVE-2026-75975 and CVE-2026-75899 (SSRF from malformed IPv6
normalization and from a hostname with repeated percent), plus a fourth
advisory. It arrives via `ajv`, which archify uses to validate the diagram
schemas.

### What was done about it

`.harness/baselines/agents-skills-archify.yaml` suppresses **only the
verified false positives**, with the reason for each written out in full.
`SC4` and `SC1` are intentionally left out of the baseline — they stay visible
on every scan until fixed upstream.

Re-scan with the baseline applied:

```
[warn]  archify — score 22/100 (MEDIUM), 2 achado(s), cobertura partial
```

| | Without baseline | With baseline |
|---|---|---|
| Score | 100/100 CRITICAL | **22/100 MEDIUM** |
| Findings | 59 | **2** |
| Suppressed | 0 | **57** |
| Gate | blocks (exit 1) | **warns** (exit 0) |

The 2 that remain are exactly `SC4` and `SC1` — the true ones. The verdict was
recorded in `skills-lock.json` as `ACEITO_COM_RESSALVA`, with the raw score
(100) preserved next to the triaged one (22): whoever opens the file sees both
numbers, not only the comfortable one.

The baseline lives **outside the scanned tree**, in `.harness/baselines/`,
one per skill. It used to live inside the skill directory — the external
review showed that was a bypass, and the fix is described in
`REVISAO-EXTERNA.md`.

## The `SC4` outcome — the full cycle

The real finding became a fix, and the path to it is what the gate exists to
provoke.

**First, measure the exposure instead of reacting to the label.** "2 HIGH
CVEs" does not say whether anyone is exposed. What does:

| Question | Answer |
|---|---|
| Is `ajv` a runtime dependency? | No — `devDependencies` |
| Who uses `ajv`? | Only `scripts/generate-validators.mjs`, a build generator that reads **local** schemas |
| Is its output versioned? | Yes — `renderers/shared/generated-validators.mjs`, which is what `bin/archify.mjs` loads |
| Does `node_modules` exist? | No |
| Does the `SKILL.md` tell you to install? | No |

The CVEs are SSRF and host confusion **in URI parsing**. The only consumer
reads JSON from disk. **Real exposure: none.**

**Still, fix it.** The advisories are resolved in `3.1.6`; `ajv` asks for
`^3.0.1`, so `3.1.8` fits without conflict — one lockfile entry, no code
touched. Two reasons, neither of them "we are vulnerable":

1. Protects whoever someday runs `npm install` there to regenerate the
   validators. Today nobody runs it; the vendored copy is permanent and that
   assumption is not.
2. Keeps the gate's warning meaning something. A known and never-resolved
   `SC4` teaches the team to ignore archify's warning — and the next finding,
   which could be real, arrives inside that noise.

What was **not** done: raising the threshold or suppressing `SC4` in the
baseline. Suppressing a true finding to turn green is exactly what the skill
prohibits.

**The `integrity` was verified against the real tarball** (`sha512` computed
from the downloaded `.tgz`), not copied from the registry response. In a
supply chain fix, trusting a hash someone handed you is repeating the problem.

**And the patch needs to survive.** Fixing a vendored lockfile creates silent
divergence from upstream: the next archify update would erase the patch
without warning. So:

- `skills-lock.json` gained `localPatches`, with a **verifiable** assertion
  (`verifyContains: fast-uri-3.1.8.tgz`, `verifyAbsent: fast-uri-3.1.5.tgz`).
- `validate-harness.sh` now checks that on every health check. If the patch is
  reverted, it fails with *"patch perdido — falta fast-uri-3.1.8.tgz"*.
- Upstream issue: [tt-a1i/archify#463](https://github.com/tt-a1i/archify/issues/463),
  so the patch stops being ours.

**Result, re-scanned:**

| | Before the bump | After |
|---|---|---|
| Score | 22/100 MEDIUM | **2/100 LOW** |
| Findings | 2 (`SC4` + `SC1`) | **1 (`SC1`)** |
| Gate | warns | **approves** |

The `SC4` disappeared because the cause was fixed, not because it was
suppressed. The remaining `SC1` is the `"ajv": "^8.17.1"` range without an
exact pin — true, minor, and upstream: it stays visible.

A field nobody verifies is an annotation, not a control — the same lesson as
`scanVerdict`, which only started to count when `validate-harness` began
checking the recorded score instead of the mere presence of the field.

## The gate rejected itself

On the first full sweep after it was ready, **`skill-guard` itself** came out
at **33/100 MEDIUM, 2 findings** — both `SC2` (External Script Fetching),
matching the text `curl | bash` in the lines where the skill **names the
pattern** for whoever reads the scanner report.

It is the same irony as `agenfk-flow`, flagged for documenting the `curl
http://localhost:3000` it forbids: **the static scanner does not distinguish
mentioning from doing.**

The answer was not to rewrite the text. Security documentation must be able to
quote the string it describes — whoever reads the report has to find in the
text the same `curl | bash` they saw in the finding. It went to the baseline,
with the reason written out.

And then the circular case appeared: suppressing the two `SC2` gave birth to a
new `AE1`, because the `SKILL.md` now cites `.skillspector-baseline.yaml` — a
file SkillSpector **deliberately excludes** from content analysis (so the text
of the suppressions does not become a finding). The reference stays
`out_of_scope` and comes out as a coverage signal.

| | Without baseline | SC2 only | SC2 + AE1 |
|---|---|---|---|
| Score | 33/100 | 25/100 | **0/100** |
| Findings | 2 | 1 | **0** |

Three iterations for a 114-line skill that does nothing dangerous. That is the
real cost of operating a gate — and the reason it needs an owner, not just an
installation.

## The pilot's lesson

A security scanner delivers **noise with signal inside**, not a verdict. The
value is not in the number: it is in someone opening the 59 findings,
checking each one against the code, and writing down why 58 do not count. The
gate automates the question; the answer is still human work.

And the inverse also holds: **score 0 is not approval.** Twenty skills scored
0 in this scan. That means "no known pattern matched in static mode" — not
that they are safe.
# Command: triage-status

## What it does
Shows progress on the Fortinet audit — how many triaged, verdicts breakdown, what's left.

## Instructions for Claude Code
1. Count total candidates:
   ```bash
   # subtract header row
   echo $(( $(wc -l < ~/Desktop/fortinet_candidates.csv) - 1 )) candidates total
   ```

2. Count triaged (triage_verdict column not empty):
   ```bash
   awk -F',' 'NR>1 && $7!=""' ~/Desktop/fortinet_candidates.csv | wc -l
   ```

3. If triage log exists, summarize it:
   ```bash
   cat ~/Desktop/fortinet_triage_log.csv
   ```
   Break down by verdict: archive / promote / extract / review counts.

4. Report:
   - X of Y notes triaged (Z% complete)
   - Archive: N | Promote: N | Extract: N | Review: N
   - Estimated time remaining at current pace (if >1 session)

5. If promotes or extracts exist, list their suggested titles so David can see what's graduating.

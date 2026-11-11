# Call Desk → Apollo enrichment

Puts every Call Desk lead into Apollo under Rubik (Nick Krajkova, Apollo user `698a2d889ba4fe0011f3709d`) with the
right person and a validated mobile, so the green **Call in Apollo** button on the Call Desk opens that contact
one click from ringing. Run it as a scheduled task (new leads only) or by hand for a backfill.

## Inputs
- Leads: `GET https://call-desk.happyproductions-hooks.workers.dev/prospects` with header `X-Pass: <passcode>`.
  Fields used: `id`, `org`, `website`, `town`, `state`, `contactName`, `contactTitle`, `email`, `phone`.
- Existing map: `call-desk/apollo.json`. Skip any lead id already in it, unless it is marked `"m": false` and
  older than 30 days (retry for a mobile).

## For each lead
1. **Domain.** From `website` (strip `www.`). No website → `moltsets.search_companies` by org name + state, limit 1.
2. **Find the person** (`moltsets.search_people`, `company_domain`, **probe at limit 1 first**):
   - Keep the named Call Desk contact if Moltsets finds them at that domain (query = their name).
   - Otherwise pick by title, in order: Communications / Marketing director → Executive Director / CEO →
     Development / Outreach director → Program director for the lead's program. Skip interns, board members,
     volunteers, and anyone whose location is outside the US.
   - Reject when the profile's employer doesn't match the org (common with same-name chapters/affiliates).
3. **Mobile:** `moltsets.linkedin_to_mobile_phone` (1 token + 1 phone token, charged only on a hit). Moltsets only
   returns validated mobiles, never land lines. Keep `last_validated_at`.
4. **Email:** `moltsets.linkedin_to_best_email`. Drop risk grade **D**. Keep A/B; keep C/F but don't make them
   the primary email.
5. **Apollo contact** (owner Rubik): search Apollo contacts first (name + org) to avoid duplicates, then
   `apollo_contacts_create` / `apollo_contacts_update` with `mobile_phone`, email, title, org, website, and
   label `Call Desk - Rubik`. Don't put the org's main line in `direct_phone`; office numbers go in
   `corporate_phone` only, so Apollo's dialer offers the mobile first.
6. **Map:** add `"<lead id>": {"c": "<apollo contact id>", "n": "<full name>", "t": "<title>", "m": true|false}`
   to `call-desk/apollo.json`. **Never write phone numbers or emails into this file** — the repo is public.

## Cost guardrails
- Probe every search at `limit: 1`; a `total` of 0 means a wrong filter, not an empty org.
- Stop and report when the Moltsets token or phone-token balance can't cover the next 10 leads.
- No Apollo enrichment credits are needed: Moltsets supplies the data, Apollo just stores it.

## Not in scope
- No browser add-on: Apollo has no link that starts a call, so Rubik clicks the phone icon on the contact.
- No calls are placed by the run.

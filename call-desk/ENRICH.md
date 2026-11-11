# Call Desk → Apollo links

The green **Call in Apollo** button on every Call Desk lead opens Apollo in one reused tab ("hp-apollo"):

1. **Contact page** when the lead has a contact in Apollo, so Rubik hits the phone icon and rings.
2. **Company page** (account, else organization) when there's no contact, so he can call the company lines
   or pick the right person from the company's people.
3. **Apollo company search by name** only for leads not matched yet (no website, or not found in Apollo).

The script sheet opens on the Call Desk at the same time.

## The map: `call-desk/apollo.json`
```json
{
  "leads":   {"<lead id>": {"c": "<apollo contact id>", "n": "Full Name", "t": "Title"}},
  "domains": {"<lead website domain>": {"o": "<apollo organization id>"}}
}
```
A `leads` entry wins; otherwise the lead's website domain picks its company. Company ids come from Apollo's free
organization lookup by domain (`apollo_organizations_lookup` with `q_organization_domains_list`, 100 per call).
Skip matches that point at a different body (a school district, police department or whole state government).
Only Apollo ids, names and titles. **Never phone numbers or emails** — the repo is public.

## Building the map (Apollo only, no credits)
Leads come from `GET https://call-desk.happyproductions-hooks.workers.dev/prospects` with header `X-Pass: <passcode>`.
For each lead not yet mapped (or mapped only to a company):
- **Contact:** if the lead has `contactName`, look for that person in Apollo contacts (name + org). If found,
  map `c`. If not, create the contact under Rubik (Apollo user `698a2d889ba4fe0011f3709d`) from the Call Desk's own
  name, title, email and phone, and map `c`. No enrichment, so no credits.
- **Company:** otherwise find the org by its website domain with Apollo company search. Prefer the saved
  account (`a`); else the organization (`o`).
- No Moltsets phone lookups (no phone tokens on the account).

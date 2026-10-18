---
name: adopt
description: Bring an existing draft, old framework or half-finished material under a knowtether worksheet without starting over. Maps the material to the eight worksheet rows, marks each row as present (with location), missing, or needs rework, and generates revision tasks only for the gaps. Use when the user has prior writing and wants to continue it with proper grounding.
argument-hint: "<path to existing draft or folder>"
---

# Adopt existing material

Source: $ARGUMENTS

Read the material. Do not rewrite it. Build `knowtether/worksheet.md` by mapping:

| Worksheet row | Look for | Mark |
|---|---|---|
| Intent | stated audience, purpose, use, any quality target | present (file:section) / missing / needs rework |
| Central idea | the thesis, the contribution, claims the author treats as settled | same |
| Expression | outline, headings, how a reader moves through it | same |
| Grounding and scope | citations, data, examples, stated limits; rights notes | same |
| Mandate | any record of what AI or collaborators were allowed to do | usually missing; ask |
| Acceptance | any reader task, review record, pass condition | usually missing; ask |
| Results and revisions | change logs, review comments | present or missing |
| Human decisions | accepted versions, decisions about scope or claims | present or missing |

Then:

1. For every external fact or number in the draft, create a material record line with what locator exists. Status `unverified` unless the original was clearly checked. Count them; tell the user how many are unverified.
2. Flag author hypotheses that read as facts, coined terms, and status words without evidence. Do not fix them yet.
3. Write a revision task list for the `missing` and `needs rework` rows only. Keep usable content and sources as they are.
4. Ask the user the two questions adoption usually needs: what the mandate is now, and what reader task counts as success.

Hand over with: the mapped worksheet, the unverified-claim count, the task list, and the next command (`/knowtether:research` if grounding is thin, `/knowtether:draft` otherwise).

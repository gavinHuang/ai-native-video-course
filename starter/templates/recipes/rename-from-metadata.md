# Recipe: rename clips from metadata

**Use:** after import, so that clip names are take IDs (C08·M01).
**Permissions:** rename clips in the media pool and on the timeline. Nothing else.

Instruction for the agent:

> Work on a duplicate: duplicate the timeline "{timeline}" as "{timeline} agent".
> For every clip on V1 of the duplicate, set the clip name to "{scene}_{shot}_{take}" from the clip metadata
> fields Scene, Shot, and Take. If a field is empty, do not rename the clip; add a yellow marker "NO METADATA".
> Report as JSON: [{"type": "renamed", "clip": "<old>", "to": "<new>"}] and a list of clips without metadata.

**Check:** the diff may contain only `renamed` (and `markers` for clips without metadata).

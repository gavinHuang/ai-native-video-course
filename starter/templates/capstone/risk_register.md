# Risk register (C18·M01)

Score likelihood (L) and impact (I) from 1 to 3. Review every week; close or re-score.

| ID | Risk | L | I | L×I | Early sign | Mitigation (before) | Response (if it happens) | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|
| R1 | Identity drift of a recurring character | 3 | 3 | 9 | identity score < 0.5 on a shot | character LoRA + identity gate (C14, C04·M03) | re-generate from the last good frame; reduce shot length | | open |
| R2 | A hosted model is removed or changed | 2 | 3 | 6 | deprecation notice | backend abstraction; a second model tested (C12·M01) | switch the route; re-test 5 cases | | open |
| R3 | Usable rate below plan → budget overrun | 3 | 2 | 6 | spend > 50 % at < 40 % of shots | caps in genqueue; explore cheap (C05·M06) | cut or merge shots; change the route | | open |
| R4 | Rights or consent gap | 2 | 3 | 6 | audit warning | rights log from day 1; weekly audit (C16) | replace the asset | | open |
| R5 | GPU not available | 2 | 2 | 4 | queue wait > 1 h | serverless + API fallback (C13) | | | open |

# Build log

## 2026-10-01 — Chart selection and genre counting

Actual user prompt excerpts (copied from the conversation):

> Genre Breakdown: Distribution of genres among movies that were rated? (Movies can have multiple genres- Please explain how it handled that before you count anything)

> I would assume some kind of Pie Chart would be used for this, let me know if something better can be used

> I think a bar chart would likely be the best use for this given we are comparing averages across categories, and we would want it to be sorted

> We would need some kind of filtered bar chart i guess and a bar to filter through floors from 50-150

First assistant recommendation (verbatim):

> I recommend sorted horizontal bars for both genre charts, a line chart for release years, and a ranked horizontal bar chart with a minimum-ratings slider for the top five.

The assistant explained counting distinct movies once per genre before calculating any totals. A Comedy|Romance movie counts in both categories. Percentages divide by all rated movies, so overlapping shares can exceed 100%. That is why the proposed pie became horizontal bars.

The assistant's decision question (verbatim):

> First decision: shall we use distinct movies counted once per genre, with overlapping percentages, for genre breakdown?

User reply (verbatim text; accompanied by the implement skill link):

> Yes that works

## 2026-10-01 — First implementation

The user invoked `anthropic-skills:implement` with the reply above.

Assistant implementation scope (verbatim):

> I’ll implement the four charts in Streamlit, using the genre-counting method you approved and the proposed rating averages. I’ll also add the 50–150 ratings slider, a direct comparison of those two floors, and a build log. This will give us a working version to use for the design discussion.

First version: `app.py` supplies four Plotly charts, a count/share radio control, a 50–150 ratings slider, and fixed comparison tables at 50 and 150. `analysis.py` holds calculations independently of the display code. The initial design uses an ivory background, serif headings, and a rust accent; the user has not yet reviewed this visual treatment.

Implementation defaults, not separately confirmed user choices:

- Genre and release-year means average individual ratings, not movie means.
- Rankings use unrounded means and deterministic tie-breaking by rating count and movie ID.
- The rating-floor control is local to the movie ranking.

Observed source issues: actual ID columns use snake_case; 30 ratings lack a release year. Those ratings remain in other analyses. There are no duplicate user/movie pairs. No source data was edited.

Validation and any subsequent revisions are recorded below after execution; no user feedback on the first visual version has been received yet.

## 2026-10-01 — Verification and first revision

Eight tests passed, including a separate standard-library CSV accumulation to verify every genre count/mean, every release-year mean, and both movie-ranking endpoints. Streamlit's AppTest rendered all four charts, moved the slider to 150, and switched counts to shares without errors.

Two separate code-review passes checked the assignment requirements and implementation standards; neither reported substantive findings.

The first browser pass found that Streamlit overrode the heading font and dimmed the explanatory captions. The initial comparison data grids also required horizontal scrolling to see all fields. The revision strengthens the typography/caption CSS and replaces the two fixed comparison grids with wrapping static tables. This was an assistant correction based on observed rendering, not a user-requested revision.

After the revision, all eight tests passed again and `pip check` reported no broken requirements. Browser inspection confirmed four rendered charts, the intended heading font, readable captions, and no page overflow at desktop and 320-pixel phone widths. The fixed comparison tables expose all four fields on narrow screens. The local preview runs at http://localhost:8501; public deployment remains a later step.

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

## 2026-10-01 — User-requested terminal restyle

Actual user feedback excerpts (copied from the conversation):

> I really hate how this UI looks could you spice it up so that visually it looks more appealing and such that the functionality is awesome?

> Try not to add more but just switch up typography (I don't want to see the same default for typography) maybe a tmux/ascii styled would be super nice?

> Use [design.md](design.md) to restyle.

The revised interface follows the supplied terminal design system: dark square panes, ANSI-inspired colors with a separate pane identity for each chart, restrained data marks, a pinned tmux-style statusline, and mint keyboard-focus styling. Fira Mono replaces the default interface/chart typography; Departure Mono supplies the pixel-style title. Text stays at 14px in the ordinary interface. Expandable tables keep sample sizes, full movie titles, and the fixed floor comparison available without adding charts or data controls.

The four analyses, the count/share radio control, and the 50–150 ratings slider remain. Calculations and the CSV are unchanged. The direct 50-versus-150 comparison remains in the best-movies pane. `terminal.css` owns the visual tokens; Plotly reads its chart colors from those same tokens. `terminal.js` supplies labelled regions on native Streamlit panes and fits long movie labels to their available chart width.

The self-hosted typography consists of Fira Mono regular/bold Latin and box-drawing symbol subsets from Google Fonts, plus Departure Mono 1.500 from its official project. The five WOFF2 assets total 67,296 bytes. Both use the SIL Open Font License 1.1; complete license texts are bundled in `static/fonts/FiraMono-OFL.txt` and `static/fonts/DepartureMono-OFL.txt`.

Official font sources:

- [Fira Mono in Google Fonts](https://github.com/google/fonts/tree/main/ofl/firamono)
- [Departure Mono](https://github.com/rektdeckard/departure-mono)

Deployment documentation now includes `terminal.css`, `terminal.js`, and all of `static/fonts/` alongside the existing application files and Streamlit config. Static serving is enabled in `.streamlit/config.toml`; a running server must restart for this setting to take effect. Public deployment remains pending.

Verification at this stage: all eight existing tests pass, and the count/share control and rating-floor slider have been exercised. Font files have valid WOFF2 signatures and their license headers were checked. The final responsive and keyboard review is still in progress; its results will be recorded separately after completion.

Final browser review: all four charts rendered with the bundled fonts loaded. At 320px, 720px, and 1440px the page had no horizontal overflow; panes stacked at narrow widths. The final mobile table check found no overflowing cells. Arrow keys switched the genre chart to shares, and the slider's End key moved to 150, updating the leader to Schindler's List and the statusline to the same floor. Statusline links reached their labelled chart regions. Mint focus borders and the slider focus outline were observed. The browser reported no console errors or warnings during these checks. Reduced-motion behavior is defined in CSS; an actual browser zoom setting was not separately verified.

Corrections made during this review: disabled Plotly's automatic text shrinking, fixed the native slider focus styling for the installed Streamlit version, configured its canvas tables to use Fira Mono, and wrapped mobile table content without reducing the 14px text size. The analysis functions and source CSV remain unchanged.

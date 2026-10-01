<script>
(() => {
  // Add region semantics to native containers after Streamlit widget reruns.
  if (window.ratingRoomObserver) window.ratingRoomObserver.disconnect();
  if (window.ratingRoomResize) window.ratingRoomResize.disconnect();
  let pending = false;
  const update = () => {
    pending = false;
    ['genres', 'satisfaction', 'years', 'movies'].forEach((name, index) => {
      const pane = document.querySelector(`.st-key-pane_${name}`);
      if (!pane) return;
      pane.setAttribute('role', 'region');
      pane.setAttribute('aria-labelledby', `pane-title-0${index + 1}`);
      pane.setAttribute('data-ink', ['blue', 'purple', 'orange', 'yellow'][index]);
    });
    // Fit titles without shrinking text. Full titles remain in the data table.
    const plot = document.querySelector('.st-key-pane_movies .js-plotly-plot');
    if (!plot?._fullLayout) return;
    const limit = Math.max(12, Math.floor(plot._fullLayout._size.w / 8.4) - 1);
    plot.querySelectorAll('.annotation-text').forEach((label, index) => {
      const title = plot.data?.[0]?.customdata?.[index]?.[0];
      if (!title) return;
      const full = `${String(index + 1).padStart(2, '0')}  ${title}`;
      const text = full.length > limit ? full.slice(0, limit - 1).trimEnd() + '…' : full;
      if (label.textContent !== text) label.textContent = text;
    });
  };
  const schedule = () => {
    if (!pending) { pending = true; requestAnimationFrame(update); }
  };
  window.ratingRoomObserver = new MutationObserver(schedule);
  window.ratingRoomObserver.observe(document.body, {childList: true, subtree: true});
  window.ratingRoomResize = new ResizeObserver(schedule);
  window.ratingRoomResize.observe(document.body);
  schedule();
})();
</script>

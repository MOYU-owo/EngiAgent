(() => {
  // Trusted local presentation code. No Python bridge, requests or model calls.
  document.querySelectorAll('[data-ea-home]').forEach(root => {
    if (root.dataset.enhanced === 'true') return;
    const vectors = __EA_VECTORS__;
    root.querySelectorAll('[data-ea-vector]').forEach(mount => {
      const vector = new DOMParser().parseFromString(vectors[Number(mount.dataset.eaVector)], 'image/svg+xml').documentElement;
      mount.replaceWith(document.importNode(vector, true));
    });
    const plan = root.querySelector('.ea-plan-region');
    const svg = root.querySelector('.ea-plan-svg');
    const beam = root.querySelector('.ea-beam-region');
    const cursor = root.querySelector('.ea-hero-cursor');
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const fine = matchMedia('(hover: hover) and (pointer: fine)');
    const horizontal = root.querySelector('.ea-crosshair-horizontal');
    const vertical = root.querySelector('.ea-crosshair-vertical');
    const center = root.querySelector('.ea-crosshair-center');
    const column = root.querySelector('.ea-guide-column');
    const row = root.querySelector('.ea-guide-row');
    if (!plan || !svg || !beam || !cursor) return;
    let frame = 0;
    let latest = null;
    const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
    const nearest = (value, values) => values.reduce((a, b) => Math.abs(b - value) < Math.abs(a - value) ? b : a);
    function draw() {
      frame = 0;
      if (!root.isConnected || !latest) return;
      const {x, y, target} = latest;
      cursor.style.transform = `translate3d(${x}px,${y}px,0) translate(-50%,-50%)`;
      const inPlan = plan.contains(target);
      root.dataset.zone = inPlan ? 'plan' : beam.contains(target) ? 'beam' : target.closest('a') ? 'link' : 'surface';
      plan.dataset.pointer = String(inPlan);
      if (inPlan) {
        const matrix = svg.getScreenCTM();
        if (matrix) {
          const point = new DOMPoint(x, y).matrixTransform(matrix.inverse());
          const px = clamp(point.x, 75, 797), py = clamp(point.y, 79, 515);
          horizontal.setAttribute('y1', py); horizontal.setAttribute('y2', py);
          vertical.setAttribute('x1', px); vertical.setAttribute('x2', px);
          center.setAttribute('x', px - 4); center.setAttribute('y', py - 4);
          const gx = nearest(px, [110, 270, 430, 590, 750]);
          const gy = nearest(py, [125, 245, 365, 485]);
          column.setAttribute('x1', gx); column.setAttribute('x2', gx);
          row.setAttribute('y1', gy); row.setAttribute('y2', gy);
        }
      }
      if (beam.contains(target) && !reduced.matches) {
        const rect = beam.getBoundingClientRect();
        beam.style.setProperty('--beam-x', `${clamp((x - rect.left) / rect.width - .5, -.5, .5) * 7}px`);
        beam.style.setProperty('--beam-y', `${clamp((y - rect.top) / rect.height - .5, -.5, .5) * 5}px`);
      } else {
        beam.style.setProperty('--beam-x', '0px'); beam.style.setProperty('--beam-y', '0px');
      }
    }
    root.addEventListener('pointermove', event => {
      if (event.pointerType !== 'mouse' || !fine.matches) return;
      root.dataset.cursor = 'active';
      latest = {x:event.clientX, y:event.clientY, target:event.target};
      if (!frame) frame = requestAnimationFrame(draw);
    }, {passive:true});
    root.addEventListener('pointerleave', () => {
      if (frame) cancelAnimationFrame(frame);
      frame = 0; latest = null;
      root.dataset.cursor = ''; root.dataset.zone = '';
      plan.dataset.pointer = 'false';
      beam.style.setProperty('--beam-x', '0px'); beam.style.setProperty('--beam-y', '0px');
    });
    root.dataset.enhanced = 'true';
  });
})();

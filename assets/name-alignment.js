/* Measure name alignment; CSS adds stroke weight and a small optical lift. */
(() => {
  const english = document.querySelector('.english-name');
  const chinese = document.querySelector('.chinese-name');
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  if (!english || !chinese || !context || !document.fonts) return;
  let pending = false;

  function align() {
    const style = getComputedStyle(english);
    context.font = `${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
    const top = context.measureText('T').actualBoundingBoxAscent;
    const bottom = context.measureText(english.textContent).actualBoundingBoxDescent;
    context.font = '400 100px "LXGW WenKai TC Name"';
    // Use identical reference ink bounds for both scripts so 王 and 天
    // retain the same scale and baseline when 华 changes to 華.
    const sample = context.measureText('王天华華');
    const inkHeight = sample.actualBoundingBoxAscent + sample.actualBoundingBoxDescent;
    if (!(inkHeight > 0 && top > 0) || !Number.isFinite(bottom)) return;
    const scale = (top + bottom) / inkHeight;
    chinese.style.fontSize = `${100 * scale}px`;
    chinese.style.setProperty('--name-alignment', `${bottom - sample.actualBoundingBoxDescent * scale}px`);
  }

  function queueAlignment() {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => { pending = false; align(); });
  }

  document.fonts.load('400 100px "LXGW WenKai TC Name"', '王天华華')
    .then(() => document.fonts.ready)
    .then(() => {
      align();
      if ('ResizeObserver' in window) new ResizeObserver(queueAlignment).observe(english);
      window.addEventListener('resize', queueAlignment);
    })
    .catch(() => { /* Keep the readable CSS fallback if the font cannot load. */ });
})();

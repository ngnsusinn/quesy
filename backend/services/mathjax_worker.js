/**
 * MathJax Worker for Quesy.
 * Typesets TeX / LaTeX mathematical formulas into:
 * 1. MathML (for Word OMML conversion)
 * 2. Vector SVG with exact baseline alignment metrics
 * 3. High-resolution raster PNG (via @resvg/resvg-js) with proper bounding box padding
 */

const fs = require('fs');
global.MathJax = {};

let mathjaxInstance = null;
let resvgClass = null;

try {
  const { Resvg } = require('@resvg/resvg-js');
  resvgClass = Resvg;
} catch (e) {
  resvgClass = null;
}

function initMathJax() {
  if (mathjaxInstance) return Promise.resolve(mathjaxInstance);
  return require('mathjax/es5/node-main.js').init({
    loader: { load: ['input/tex-full', 'output/svg'] }
  }).then((mj) => {
    mathjaxInstance = mj;
    return mj;
  });
}

function renderFormula(mj, latex, options = {}) {
  const fontSizePt = options.fontSizePt || 11.0;
  const dpi = options.dpi || 300;
  const generatePng = options.generatePng !== false && resvgClass !== null;

  // Clean math delimiters if present
  let clean = (latex || '').trim();
  if (clean.startsWith('${') && clean.endsWith('}$')) {
    clean = clean.slice(2, -2).trim();
  } else if (clean.startsWith('$$') && clean.endsWith('$$')) {
    clean = clean.slice(2, -2).trim();
  } else if (clean.startsWith('$') && clean.endsWith('$')) {
    clean = clean.slice(1, -1).trim();
  }

  // Common TeX normalizations for MathJax
  clean = clean.replace(/\\dfrac/g, '\\frac');

  // 1. Convert to MathML
  let mml = null;
  try {
    mml = mj.tex2mml(clean, { display: false });
  } catch (err) {
    mml = null;
  }

  // 2. Convert to SVG
  let svgString = null;
  let wPt = 0.0;
  let hPt = 0.0;
  let depthPt = 0.0;
  let shiftHalfPt = 0;
  let pngBase64 = null;

  try {
    const svgNode = mj.tex2svg(clean, { display: false });
    const adaptor = mj.startup.adaptor;
    const svgElem = adaptor.tags(svgNode, 'svg')[0];

    if (svgElem) {
      const style = adaptor.getAttribute(svgElem, 'style') || '';
      const vMatch = style.match(/vertical-align:\s*([-\d.]+)ex/);
      const vAlignEx = vMatch ? parseFloat(vMatch[1]) : 0.0;

      const wEx = parseFloat(adaptor.getAttribute(svgElem, 'width') || '0ex');
      const hEx = parseFloat(adaptor.getAttribute(svgElem, 'height') || '0ex');

      const viewBoxStr = adaptor.getAttribute(svgElem, 'viewBox') || '';
      const [minX, minY, vbW, vbH] = viewBoxStr.split(/\s+/).map(Number);

      // Keep padX tight to prevent artificial gaps before sentence-ending punctuation
      const hasWideArrow = /\\(overrightarrow|overleftrightarrow|underrightarrow|underleftarrow)/.test(latex);
      const padX = hasWideArrow ? 120 : 15;
      const padY = Math.round(vbH * 0.05) + 40;

      const newMinX = minX - padX;
      const newMinY = minY - padY;
      const newVbW = vbW + padX * 2;
      const newVbH = vbH + padY * 2;

      const scaleX = newVbW / (vbW || 1);
      const scaleY = newVbH / (vbH || 1);

      const adjWEx = wEx * scaleX;
      const adjHEx = hEx * scaleY;

      adaptor.setAttribute(svgElem, 'viewBox', `${newMinX} ${newMinY} ${newVbW} ${newVbH}`);
      adaptor.setAttribute(svgElem, 'width', `${adjWEx.toFixed(3)}ex`);
      adaptor.setAttribute(svgElem, 'height', `${adjHEx.toFixed(3)}ex`);

      // 1ex in MathJax is roughly 0.431em. 1em = fontSizePt.
      // Therefore, 1ex ~ 0.431 * fontSizePt.
      const exToPt = 0.431 * fontSizePt;
      wPt = Math.max(1.0, adjWEx * exToPt);
      hPt = Math.max(1.0, adjHEx * exToPt);

      // Adjusted vertical alignment in ex:
      const adjVAlignEx = vAlignEx - ((padY / (vbH || 1)) * hEx);
      depthPt = Math.max(0.0, -adjVAlignEx * exToPt);
      shiftHalfPt = -max(0, Math.round(depthPt * 2));

      adaptor.setAttribute(svgElem, 'style', `vertical-align: ${adjVAlignEx.toFixed(3)}ex;`);
      svgString = adaptor.outerHTML(svgElem);

      // 3. Render PNG via Resvg if available
      if (generatePng && resvgClass) {
        const resvg = new resvgClass(svgString, { dpi: dpi });
        const pngData = resvg.render();
        const pngBuf = pngData.asPng();
        pngBase64 = pngBuf.toString('base64');
      }
    }
  } catch (err) {
    svgString = null;
  }

  return {
    latex: clean,
    mml: mml,
    svg: svgString,
    w_pt: Math.round(wPt * 100) / 100,
    h_pt: Math.round(hPt * 100) / 100,
    depth_pt: Math.round(depthPt * 100) / 100,
    shift_half_pt: shiftHalfPt,
    png_base64: pngBase64
  };
}

function max(a, b) {
  return a > b ? a : b;
}

// CLI handler: reads JSON from stdin or argument
async function main() {
  const mj = await initMathJax();

  // If argument provided, parse it
  if (process.argv.length > 2) {
    const rawInput = process.argv[2];
    try {
      const data = JSON.parse(rawInput);
      if (Array.isArray(data)) {
        const out = data.map((item) => {
          if (typeof item === 'string') return renderFormula(mj, item);
          return renderFormula(mj, item.latex, item);
        });
        process.stdout.write(JSON.stringify(out));
      } else {
        const out = renderFormula(mj, data.latex || data, data);
        process.stdout.write(JSON.stringify(out));
      }
      return;
    } catch (e) {
      // not JSON arg, process as raw stdin below
    }
  }

  // Interactive line-by-line stdin mode
  const readline = require('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
  });

  rl.on('line', (line) => {
    if (!line.trim()) return;
    try {
      const req = JSON.parse(line);
      const res = renderFormula(mj, req.latex, req);
      process.stdout.write(JSON.stringify(res) + '\n');
    } catch (err) {
      process.stdout.write(JSON.stringify({ error: String(err) }) + '\n');
    }
  });
}

main().catch((err) => {
  console.error('Fatal MathJax Worker Error:', err);
  process.exit(1);
});

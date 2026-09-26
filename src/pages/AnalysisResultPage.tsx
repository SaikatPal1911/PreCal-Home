import React, { useState, useRef, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Download, Save, Plus, Users, Edit2, ChevronDown, ChevronUp,
  Calendar, Tag, MapPin, Sparkles, Info, CheckCircle, Printer
} from 'lucide-react';
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { useAnalysis, useProjects, useToast, useLang } from '../context/AppContext';
import type { DesignRecommendation, MaterialItem, BudgetBreakdown } from '../types';

const normalizeHex = (value?: string): string => {
  if (!value) return '#D9B98A';
  const trimmed = value.trim();
  if (!trimmed) return '#D9B98A';

  if (trimmed.startsWith('#')) {
    const compact = trimmed.slice(1);
    if (compact.length === 3) return `#${compact.split('').map(ch => ch + ch).join('')}`.toUpperCase();
    if (compact.length === 6) return `#${compact}`.toUpperCase();
    return `#${compact.padEnd(6, '0')}`.toUpperCase();
  }

  if (trimmed.startsWith('rgb')) {
    const matches = trimmed.match(/\d+/g);
    if (matches && matches.length >= 3) {
      const [r, g, b] = matches.slice(0, 3).map(Number);
      return `#${[r, g, b].map(v => v.toString(16).padStart(2, '0')).join('').toUpperCase()}`;
    }
  }

  return `#${trimmed.replace(/[^0-9A-Fa-f]/g, '').slice(0, 6).padEnd(6, '0')}`.toUpperCase();
};

const hexToRgb = (hex: string) => {
  const safe = normalizeHex(hex).replace('#', '');
  const num = Number.parseInt(safe, 16);
  return {
    r: (num >> 16) & 255,
    g: (num >> 8) & 255,
    b: num & 255,
  };
};

const rgbToHex = ({ r, g, b }: { r: number; g: number; b: number }) =>
  `#${[r, g, b].map(v => Math.max(0, Math.min(255, v)).toString(16).padStart(2, '0')).join('').toUpperCase()}`;

const blendWithTarget = (base: { r: number; g: number; b: number }, target: { r: number; g: number; b: number }, amount: number) => {
  const mix = Math.max(0, Math.min(1, amount));
  return {
    r: Math.round(base.r * (1 - mix) + target.r * mix),
    g: Math.round(base.g * (1 - mix) + target.g * mix),
    b: Math.round(base.b * (1 - mix) + target.b * mix),
  };
};

const buildWallMask = (pixels: Uint8ClampedArray, width: number, height: number): Uint8ClampedArray => {
  const mask = new Uint8ClampedArray(width * height);

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = (y * width + x) * 4;
      const r = pixels[i];
      const g = pixels[i + 1];
      const b = pixels[i + 2];
      const channelMax = Math.max(r, g, b);
      const channelMin = Math.min(r, g, b);
      const saturation = channelMax === 0 ? 0 : ((channelMax - channelMin) / channelMax) * 100;
      const brightness = (r + g + b) / 3;
      const distance = Math.hypot(x - width / 2, y - height / 2) / Math.max(width, height);
      const wallLike = brightness > 30 && brightness < 230 && saturation < 60 && distance < 1.1;
      const neutralEdge = brightness > 35 && brightness < 235 && saturation < 75 && (x < width * 0.12 || x > width * 0.88 || y < height * 0.12 || y > height * 0.88);
      mask[y * width + x] = wallLike || neutralEdge ? 255 : 0;
    }
  }

  return mask;
};

const recolorImageWithWallMask = async (imageUrl: string, hex: string): Promise<string> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        const width = img.naturalWidth || img.width;
        const height = img.naturalHeight || img.height;
        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error('Canvas context is not available.'));
          return;
        }

        ctx.drawImage(img, 0, 0, width, height);
        const imageData = ctx.getImageData(0, 0, width, height);
        const target = hexToRgb(hex);
        const wallMask = buildWallMask(imageData.data, width, height);

        for (let i = 0; i < wallMask.length; i += 1) {
          if (wallMask[i] <= 0) continue;

          const px = i * 4;
          const base = {
            r: imageData.data[px],
            g: imageData.data[px + 1],
            b: imageData.data[px + 2],
          };

          const blended = blendWithTarget(base, target, 0.58);
          const brightnessBoost = Math.max(0, (base.r + base.g + base.b) / 765);
          imageData.data[px] = Math.min(255, blended.r + brightnessBoost * 12);
          imageData.data[px + 1] = Math.min(255, blended.g + brightnessBoost * 12);
          imageData.data[px + 2] = Math.min(255, blended.b + brightnessBoost * 12);
        }

        ctx.putImageData(imageData, 0, 0);
        resolve(canvas.toDataURL('image/png'));
      } catch (error) {
        reject(error);
      }
    };

    img.onerror = () => reject(new Error('Unable to load the uploaded image.'));
    img.src = imageUrl;
  });
};

// ---- Color Swatch ----
const ColorSwatch: React.FC<{ hex: string; name: string; size?: 'sm' | 'lg' }> = ({ hex, name, size = 'sm' }) => (
  <div className="flex flex-col items-center gap-1">
    <div
      className={`rounded-xl border border-warm-100 shadow-sm ${size === 'lg' ? 'w-14 h-14' : 'w-10 h-10'}`}
      style={{ backgroundColor: hex }}
    />
    <span className="text-[10px] text-charcoal-700 opacity-70 text-center leading-tight max-w-[48px]">{name}</span>
    <span className="text-[9px] text-gray-400 font-mono">{hex}</span>
  </div>
);

// ---- Recommendation Card ----
const RecommendationCard: React.FC<{ rec: DesignRecommendation; i: number }> = ({ rec, i }) => {
  const labelColor = rec.label === 'Recommended'
    ? 'badge-green'
    : rec.label === 'Alternative 1'
    ? 'badge-blue'
    : 'bg-purple-50 text-purple-700 badge';

  return (
    <div className={`card p-5 ${i === 0 ? 'ring-2 ring-sage-500' : ''}`}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <h4 className="font-display font-semibold text-charcoal-800">{rec.title}</h4>
        <span className={labelColor}>{rec.label}</span>
      </div>
      <p className="text-sm text-charcoal-700 opacity-70 leading-relaxed mb-4">{rec.description}</p>

      {/* Colors */}
      {rec.primaryColorHex && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-charcoal-700 mb-2">Colour Palette</p>
          <div className="flex gap-3 flex-wrap">
            {rec.primaryColorHex && (
              <ColorSwatch hex={rec.primaryColorHex} name={rec.primaryColor || 'Primary'} size="lg" />
            )}
            {rec.complementaryColors?.map(c => (
              <ColorSwatch key={c.hex} hex={c.hex} name={c.name} />
            ))}
          </div>
        </div>
      )}

      {/* Details */}
      <div className="flex flex-wrap gap-2">
        {rec.finish && (
          <span className="text-xs bg-cream-100 text-charcoal-700 px-2.5 py-1 rounded-full">Finish: {rec.finish}</span>
        )}
        {rec.material && (
          <span className="text-xs bg-cream-100 text-charcoal-700 px-2.5 py-1 rounded-full">Material: {rec.material}</span>
        )}
        {rec.tags.map(tag => (
          <span key={tag} className="badge badge-green !text-[10px]">{tag}</span>
        ))}
      </div>
    </div>
  );
};

// ---- Material Table ----
const MaterialTable: React.FC<{ items: MaterialItem[] }> = ({ items }) => {
  const total = items.reduce((s, i) => s + i.totalPrice, 0);
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-warm-100">
            <th className="text-left py-3 px-3 text-xs font-semibold text-charcoal-700 opacity-70">#</th>
            <th className="text-left py-3 px-3 text-xs font-semibold text-charcoal-700 opacity-70">Material Name</th>
            <th className="text-left py-3 px-3 text-xs font-semibold text-charcoal-700 opacity-70 hidden md:table-cell">Specification</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-charcoal-700 opacity-70">Qty</th>
            <th className="text-left py-3 px-3 text-xs font-semibold text-charcoal-700 opacity-70">Unit</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-charcoal-700 opacity-70">Unit Price</th>
            <th className="text-right py-3 px-3 text-xs font-semibold text-charcoal-700 opacity-70">Total</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, i) => (
            <tr key={item.id} className={`border-b border-warm-50 hover:bg-cream-50 transition-colors ${i % 2 === 0 ? 'bg-white' : 'bg-cream-50/30'}`}>
              <td className="py-3 px-3 text-gray-400 text-xs">{i + 1}</td>
              <td className="py-3 px-3 font-medium text-charcoal-800">{item.name}</td>
              <td className="py-3 px-3 text-charcoal-700 opacity-60 text-xs hidden md:table-cell">{item.specification}</td>
              <td className="py-3 px-3 text-right text-charcoal-800">{item.quantity}</td>
              <td className="py-3 px-3 text-charcoal-700 opacity-60">{item.unit}</td>
              <td className="py-3 px-3 text-right text-charcoal-700">₹{item.unitPrice.toLocaleString('en-IN')}</td>
              <td className="py-3 px-3 text-right font-semibold text-charcoal-800">₹{item.totalPrice.toLocaleString('en-IN')}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-warm-200 bg-cream-100">
            <td colSpan={5} className="py-3 px-3 font-semibold text-charcoal-800 text-sm">Total Material Cost</td>
            <td />
            <td className="py-3 px-3 text-right font-bold text-sage-700 text-base">₹{total.toLocaleString('en-IN')}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
};

// ---- Budget Chart ----
const CHART_COLORS = ['#4a7c4a', '#d4a017', '#7a9bb5', '#c17f5c', '#9fbf9f'];
const BudgetChart: React.FC<{ breakdown: BudgetBreakdown }> = ({ breakdown }) => {
  const data = [
    { name: 'Materials', value: breakdown.material },
    { name: 'Labour', value: breakdown.labour },
    { name: 'Transport', value: breakdown.transport },
    { name: 'Miscellaneous', value: breakdown.misc },
    { name: 'Contingency', value: breakdown.contingency },
  ];
  const fmt = (v: number) => `₹${v.toLocaleString('en-IN')}`;

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={65} outerRadius={100} paddingAngle={3} dataKey="value">
          {data.map((_, i) => (
            <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(v: number) => fmt(v)} />
        <Legend iconType="circle" iconSize={8} formatter={(value) => <span className="text-xs text-charcoal-700">{value}</span>} />
      </PieChart>
    </ResponsiveContainer>
  );
};

export const AnalysisResultPage: React.FC = () => {
  const { result } = useAnalysis();
  const { saveProject, projects } = useProjects();
  const { showToast } = useToast();
  const { t } = useLang();
  const navigate = useNavigate();
  const [showDetailedCost, setShowDetailedCost] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showOriginalImage, setShowOriginalImage] = useState(false);
  const [selectedColor, setSelectedColor] = useState<{ name: string; hex: string } | null>(null);
  const [customColor, setCustomColor] = useState('#7B2D43');
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isProcessingPreview, setIsProcessingPreview] = useState(false);
  const reportRef = useRef<HTMLDivElement>(null);

  if (!result) {
    return (
      <div className="p-8 text-center">
        <p className="text-charcoal-700 mb-4">No analysis result found. Please complete an analysis first.</p>
        <button onClick={() => navigate('/analysis')} className="btn-primary">Start Analysis</button>
      </div>
    );
  }

  const { budgetBreakdown: bd } = result;
  const categoryLabel = result.category ? result.category.charAt(0).toUpperCase() + result.category.slice(1) : '';

  const allColorOptions = useMemo(() => {
    const map = new Map<string, { name: string; hex: string }>();
    result.recommendations.forEach(rec => {
      if (rec.primaryColorHex) {
        const hex = normalizeHex(rec.primaryColorHex);
        map.set(hex, { name: rec.primaryColor || rec.title || 'Recommended', hex });
      }
      rec.complementaryColors?.forEach(color => {
        const hex = normalizeHex(color.hex);
        if (!map.has(hex)) map.set(hex, { name: color.name || 'Accent', hex });
      });
    });
    return Array.from(map.values());
  }, [result.recommendations]);

  useEffect(() => {
    if (!result.imagePreviewUrl) {
      setPreviewUrl(null);
      return;
    }

    const first = allColorOptions[0];
    const defaultSelection = first ? { name: first.name, hex: first.hex } : { name: 'Default', hex: '#D9B98A' };
    setSelectedColor(prev => prev ?? defaultSelection);
    setCustomColor(defaultSelection.hex);
  }, [result.imagePreviewUrl, allColorOptions]);

  useEffect(() => {
    if (!result.imagePreviewUrl) return;
    if (showOriginalImage) {
      setPreviewUrl(result.imagePreviewUrl);
      return;
    }

    if (!selectedColor) {
      setPreviewUrl(result.imagePreviewUrl);
      return;
    }

    let cancelled = false;
    setIsProcessingPreview(true);
    recolorImageWithWallMask(result.imagePreviewUrl, selectedColor.hex)
      .then(url => {
        if (!cancelled) setPreviewUrl(url);
      })
      .catch(() => {
        if (!cancelled) setPreviewUrl(result.imagePreviewUrl);
      })
      .finally(() => {
        if (!cancelled) setIsProcessingPreview(false);
      });

    return () => { cancelled = true; };
  }, [result.imagePreviewUrl, selectedColor, showOriginalImage]);

  const handleSave = () => {
    saveProject({
      id: result.id,
      name: result.projectName,
      category: result.category,
      thumbnail: result.imagePreviewUrl,
      budget: bd.total,
      createdAt: result.createdAt,
      result,
    });
    setSaved(true);
    showToast(t('toast.projectSaved'), 'success');
  };

  const handleDownload = () => {
    const content = `
PreCal Home Analysis Report
======================
Project: ${result.projectName}
Category: ${categoryLabel}
Budget Tier: ${result.budget}
Property Type: ${result.propertyType}
Date: ${new Date(result.createdAt).toLocaleDateString('en-IN')}

DESIGN RECOMMENDATIONS
----------------------
${result.recommendations.map(r => `${r.label}: ${r.title}\n${r.description}`).join('\n\n')}

BILL OF MATERIALS (BOM)
-----------------------
${result.materials.map((m, i) => `${i + 1}. ${m.name} - ${m.quantity} ${m.unit} @ ₹${m.unitPrice} = ₹${m.totalPrice}`).join('\n')}

BUDGET BREAKDOWN
----------------
Materials:     ₹${bd.material.toLocaleString('en-IN')}
Labour:        ₹${bd.labour.toLocaleString('en-IN')}
Transport:     ₹${bd.transport.toLocaleString('en-IN')}
Miscellaneous: ₹${bd.misc.toLocaleString('en-IN')}
Contingency:   ₹${bd.contingency.toLocaleString('en-IN')}
TOTAL:         ₹${bd.total.toLocaleString('en-IN')}

Note: All prices are approximate.
Generated by PreCal Home · precal.home
    `.trim();

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `PreCal-Home-Report-${result.id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Report downloaded!', 'success');
  };

  const handleColorSelect = (name: string, hex: string) => {
    const normalizedHex = normalizeHex(hex);
    setSelectedColor({ name, hex: normalizedHex });
    setCustomColor(normalizedHex);
    setShowOriginalImage(false);
  };

  const handleResetOriginal = () => {
    setShowOriginalImage(true);
    setSelectedColor(null);
  };

  const handleCustomColorChange = (hex: string) => {
    const normalized = normalizeHex(hex);
    setCustomColor(normalized);
    setSelectedColor({ name: 'Custom Colour', hex: normalized });
    setShowOriginalImage(false);
  };

  const currentDisplayImage = showOriginalImage ? result.imagePreviewUrl : previewUrl || result.imagePreviewUrl;

  return (
    <div ref={reportRef} className="p-6 lg:p-8 max-w-5xl mx-auto animate-fade-in space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="badge-green">Analysis Complete</span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-display font-bold text-charcoal-800">{result.projectName}</h1>
          <p className="text-sm text-charcoal-700 opacity-60 mt-1">
            {new Date(result.createdAt).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={() => navigate('/analysis')} className="btn-secondary !text-xs !py-2">
            <Edit2 className="w-3.5 h-3.5" /> Edit Preferences
          </button>
          <button onClick={handleDownload} className="btn-secondary !text-xs !py-2">
            <Download className="w-3.5 h-3.5" /> Download Report
          </button>
        </div>
      </div>

      {/* SECTION A: Project Summary */}
      <div className="card p-6">
        <h2 className="font-display font-semibold text-lg text-charcoal-800 mb-4 flex items-center gap-2">
          <Tag className="w-4 h-4 text-sage-600" /> Project Summary
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {[
            { label: 'Category', value: categoryLabel },
            { label: 'Budget Tier', value: result.budget ? result.budget.charAt(0).toUpperCase() + result.budget.slice(1) : '–' },
            { label: 'Property Type', value: result.propertyType ? result.propertyType.charAt(0).toUpperCase() + result.propertyType.slice(1) : '–' },
            { label: 'Design Style', value: result.preferences?.designStyle || 'Not specified' },
          ].map(item => (
            <div key={item.label} className="bg-cream-50 rounded-xl p-3">
              <p className="text-xs text-charcoal-700 opacity-60 mb-0.5">{item.label}</p>
              <p className="font-semibold text-charcoal-800 text-sm">{item.value}</p>
            </div>
          ))}
        </div>
        {result.imagePreviewUrl && (
          <div className="mt-2">
            <p className="text-xs font-semibold text-charcoal-700 mb-2">Uploaded Image</p>
            <img src={result.imagePreviewUrl} alt="Uploaded space" className="w-full max-w-xs h-40 object-cover rounded-xl" />
          </div>
        )}
      </div>

      {/* SECTION B: Compare Your Options */}
      <div className="card p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
          <div>
            <h2 className="font-display font-semibold text-xl text-charcoal-800 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-gold-500" /> Compare Your Options
            </h2>
            <p className="text-xs text-charcoal-700 opacity-60 mt-1">Demo wall mask preview for your uploaded room image.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setShowOriginalImage(true)}
              className={`btn-secondary !text-xs !py-2 ${showOriginalImage ? '!bg-sage-50 !text-sage-700 !border-sage-300' : ''}`}
            >
              Original
            </button>
            <button
              type="button"
              onClick={() => setShowOriginalImage(false)}
              className={`btn-secondary !text-xs !py-2 ${!showOriginalImage && selectedColor ? '!bg-sage-50 !text-sage-700 !border-sage-300' : ''}`}
            >
              Preview
            </button>
            <button
              type="button"
              onClick={handleResetOriginal}
              className="btn-secondary !text-xs !py-2"
            >
              Reset to Original
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[1.35fr,0.85fr] gap-6">
          <div className="rounded-2xl border border-warm-100 bg-cream-50 p-3">
            <div className="relative overflow-hidden rounded-xl bg-white border border-warm-100">
              {currentDisplayImage ? (
                <img
                  src={currentDisplayImage}
                  alt="Room preview"
                  className="w-full h-[360px] object-cover"
                />
              ) : (
                <div className="h-[360px] flex items-center justify-center text-sm text-charcoal-700 opacity-60">No image available</div>
              )}
              {isProcessingPreview && !showOriginalImage && (
                <div className="absolute inset-0 bg-white/45 backdrop-blur-[1px] flex items-center justify-center text-xs font-medium text-sage-700">
                  Applying colour preview...
                </div>
              )}
            </div>
            <div className="mt-3 flex items-center justify-between gap-3">
              <div>
                <p className="text-[11px] uppercase tracking-[0.12em] text-charcoal-700 opacity-50">Selected</p>
                <p className="font-medium text-charcoal-800">{selectedColor ? selectedColor.name : 'Original'}</p>
              </div>
              <div className="text-right">
                <p className="text-[11px] uppercase tracking-[0.12em] text-charcoal-700 opacity-50">Hex</p>
                <p className="font-mono text-sm text-charcoal-800">{selectedColor ? selectedColor.hex.toUpperCase() : '—'}</p>
              </div>
            </div>
          </div>

          <div className="space-y-5">
            <div>
              <p className="text-xs font-semibold text-charcoal-700 mb-2 uppercase tracking-[0.08em]">AI Recommendations</p>
              <div className="flex flex-wrap gap-3">
                {allColorOptions.map((option) => (
                  <button
                    key={`${option.hex}-${option.name}`}
                    type="button"
                    onClick={() => handleColorSelect(option.name, option.hex)}
                    className={`flex items-center gap-2 rounded-xl border px-2.5 py-2 text-left transition ${
                      selectedColor?.hex === option.hex && !showOriginalImage
                        ? 'border-sage-500 bg-sage-50 shadow-sm ring-2 ring-sage-200'
                        : 'border-warm-100 bg-white hover:border-sage-300'
                    }`}
                  >
                    <span className="w-9 h-9 rounded-lg border border-warm-100" style={{ backgroundColor: option.hex }} />
                    <span className="min-w-0">
                      <span className="block text-xs font-semibold text-charcoal-800 truncate max-w-[100px]">{option.name}</span>
                      <span className="block text-[10px] text-charcoal-600 font-mono">{option.hex}</span>
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div className="border-t border-warm-100 pt-5">
              <p className="text-xs font-semibold text-charcoal-700 mb-3 uppercase tracking-[0.08em]">Choose Any Color</p>
              <div className="flex items-center gap-3 flex-wrap">
                <input
                  type="color"
                  value={customColor}
                  onChange={(event) => handleCustomColorChange(event.target.value)}
                  className="w-14 h-12 border border-warm-200 rounded-lg bg-transparent cursor-pointer"
                  aria-label="Choose any colour"
                />
                <input
                  type="text"
                  value={customColor}
                  onChange={(event) => handleCustomColorChange(event.target.value)}
                  className="form-input !w-[120px] uppercase"
                  placeholder="#AABBCC"
                  aria-label="Custom colour hex value"
                />
                <div className="w-10 h-10 rounded-full border border-warm-200" style={{ backgroundColor: customColor }} />
              </div>
              <p className="mt-3 text-[11px] text-charcoal-700 opacity-60">
                Demo wall recolor only: the app uses the uploaded room photo and a fallback wall mask to preview paint on wall regions. Real AI segmentation is not active in this demo build.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION B: Design Recommendations */}
      <div>
        <h2 className="font-display font-semibold text-xl text-charcoal-800 mb-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-gold-500" /> AI Design Recommendations
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {result.recommendations.map((rec, i) => (
            <RecommendationCard key={i} rec={rec} i={i} />
          ))}
        </div>
      </div>

      {/* SECTION C: BOM */}
      <div>
        <h2 className="font-display font-semibold text-xl text-charcoal-800 mb-4 flex items-center gap-2">
          <Printer className="w-5 h-5 text-sage-600" /> Bill of Materials (BOM)
        </h2>
        <div className="card overflow-hidden">
          <MaterialTable items={result.materials} />
        </div>
        <div className="mt-3 p-3 bg-blue-50 rounded-xl border border-blue-100">
          <p className="text-xs text-blue-700">
            <strong>Note:</strong> Quantities are calculated from your measurements and rounded up to standard purchase units. Actual quantities may vary based on site conditions and workmanship. Prices are approximate market estimates.
          </p>
        </div>
      </div>

      {/* SECTION D: Budget Breakdown */}
      <div>
        <h2 className="font-display font-semibold text-xl text-charcoal-800 mb-4 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-gold-500" /> Budget Breakdown
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Chart */}
          <div className="card p-6">
            <BudgetChart breakdown={bd} />
          </div>
          {/* Numbers */}
          <div className="card p-6 space-y-3">
            {[
              { label: 'Material Cost', value: bd.material, color: 'bg-sage-500' },
              { label: 'Labour / Installation', value: bd.labour, color: 'bg-gold-500' },
              { label: 'Transportation', value: bd.transport, color: 'bg-blue-400' },
              { label: 'Miscellaneous', value: bd.misc, color: 'bg-rose-400' },
              { label: 'Contingency (8%)', value: bd.contingency, color: 'bg-emerald-400' },
            ].map(item => (
              <div key={item.label} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
                  <span className="text-sm text-charcoal-700">{item.label}</span>
                </div>
                <span className="text-sm font-semibold text-charcoal-800">₹{item.value.toLocaleString('en-IN')}</span>
              </div>
            ))}
            <div className="border-t border-warm-100 pt-3">
              <div className="flex items-center justify-between">
                <span className="font-display font-bold text-lg text-charcoal-800">Total Estimated Budget</span>
                <span className="font-display font-bold text-2xl text-sage-700">₹{bd.total.toLocaleString('en-IN')}</span>
              </div>
              <p className="text-xs text-charcoal-700 opacity-60 mt-1">
                Range: ₹{Math.round(bd.total * 0.85).toLocaleString('en-IN')} – ₹{Math.round(bd.total * 1.20).toLocaleString('en-IN')} (±15%)
              </p>
            </div>
          </div>
        </div>

        {/* Expandable Detail */}
        <button
          onClick={() => setShowDetailedCost(!showDetailedCost)}
          className="mt-4 flex items-center gap-2 text-sm text-sage-600 font-medium hover:text-sage-700"
        >
          {showDetailedCost ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          {showDetailedCost ? 'Hide' : 'View'} Detailed Cost Assumptions
        </button>
        {showDetailedCost && (
          <div className="mt-3 card p-5 text-sm space-y-2 animate-slide-up">
            <p className="font-semibold text-charcoal-800 mb-2">Cost Calculation Assumptions</p>
            <ul className="space-y-1.5 text-charcoal-700 opacity-80">
              <li>• Material prices based on average Indian retail market (2024)</li>
              <li>• Labour rates estimated at {result.category === 'furniture' ? '55%' : result.category === 'ceiling' ? '65%' : '45%'} of material cost for {result.category}</li>
              <li>• Transportation estimated at 6% of material cost</li>
              <li>• Miscellaneous (masking, cleanup, small tools) at 4%</li>
              <li>• 8% contingency for scope changes, rework, and price fluctuations</li>
              <li>• All prices in Indian Rupees (INR) and exclusive of GST</li>
              <li className="text-amber-700 font-medium">• These are illustrative estimates only — not professional quotes</li>
            </ul>
          </div>
        )}
      </div>

      {/* SECTION E: Actions */}
      <div className="card p-6 bg-gradient-to-br from-sage-50 to-cream-100">
        <h3 className="font-display font-semibold text-lg text-charcoal-800 mb-2">Ready to Transform Your Space?</h3>
        <p className="text-sm text-charcoal-700 opacity-70 mb-5">
          Connect with verified local professionals for your renovation project, or save this report for later.
        </p>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleDownload}
            className="btn-secondary !text-sm"
            id="download-report"
          >
            <Download className="w-4 h-4" /> {t('btn.downloadReport')}
          </button>
          <button
            onClick={handleSave}
            disabled={saved}
            className="btn-secondary !text-sm disabled:opacity-60"
            id="save-project"
          >
            {saved ? <><CheckCircle className="w-4 h-4 text-sage-600" /> Saved!</> : <><Save className="w-4 h-4" /> {t('btn.saveProject')}</>}
          </button>
          <button
            onClick={() => { navigate('/analysis'); }}
            className="btn-secondary !text-sm"
          >
            <Plus className="w-4 h-4" /> New Analysis
          </button>
          <button
            onClick={() => navigate('/professionals')}
            className="btn-gold !text-sm"
            id="book-professionals"
          >
            <Users className="w-4 h-4" /> {t('btn.bookProfessionals')}
          </button>
        </div>
      </div>

      {/* CTA Banner */}
      <div className="rounded-2xl bg-charcoal-900 text-white p-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <p className="font-display font-bold text-xl mb-1">Ready to Get Started?</p>
          <p className="text-gray-400 text-sm">Connect with verified renovation professionals in your area.</p>
        </div>
        <button
          onClick={() => navigate('/professionals')}
          className="flex items-center gap-2 bg-sage-600 hover:bg-sage-700 text-white font-semibold px-6 py-3 rounded-xl transition-all flex-shrink-0"
        >
          <Users className="w-4 h-4" /> Book Professionals
        </button>
      </div>
    </div>
  );
};

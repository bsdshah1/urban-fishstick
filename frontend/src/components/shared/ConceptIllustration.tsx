/**
 * Topic-specific visual illustrations for the parent digest.
 * Reflects the school's concrete–pictorial–abstract approach.
 */
import React from 'react'

const C = {
  green: '#2A6049',
  greenLight: '#E8F4F0',
  greenMid: '#C6E9DC',
  amber: '#C97B2E',
  amberLight: '#FDF3E7',
  blue: '#2D6A9F',
  blueLight: '#EBF4FF',
  red: '#C0392B',
  redLight: '#FFF0E6',
  purple: '#6B46C1',
  purpleLight: '#F0EBFF',
  text: '#1C2B3A',
  textMuted: '#718096',
  white: '#FFFFFF',
  bg: '#F8F6F1',
  border: '#DDD8D0',
}

function FractionsIllustration() {
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      {/* Whole label */}
      <text x="22" y="16" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">WHOLE</text>
      <rect x="4" y="22" width="46" height="28" rx="4" fill={C.greenLight} stroke={C.green} strokeWidth="1.5"/>
      <text x="27" y="41" fontSize="11" fill={C.green} fontFamily="system-ui" fontWeight="700" textAnchor="middle">1</text>

      {/* Halves label */}
      <text x="66" y="16" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">HALVES</text>
      <rect x="56" y="22" width="22" height="28" rx="4" fill={C.green} stroke={C.green} strokeWidth="1.5"/>
      <text x="67" y="41" fontSize="11" fill={C.white} fontFamily="system-ui" fontWeight="700" textAnchor="middle">½</text>
      <rect x="80" y="22" width="22" height="28" rx="4" fill={C.greenLight} stroke={C.green} strokeWidth="1.5"/>
      <text x="91" y="41" fontSize="11" fill={C.green} fontFamily="system-ui" fontWeight="700" textAnchor="middle">½</text>

      {/* Quarters label */}
      <text x="116" y="16" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">QUARTERS</text>
      <rect x="108" y="22" width="22" height="28" rx="4" fill={C.green} stroke={C.green} strokeWidth="1.5"/>
      <text x="119" y="41" fontSize="11" fill={C.white} fontFamily="system-ui" fontWeight="700" textAnchor="middle">¼</text>
      <rect x="132" y="22" width="22" height="28" rx="4" fill={C.greenMid} stroke={C.green} strokeWidth="1.5"/>
      <text x="143" y="41" fontSize="11" fill={C.green} fontFamily="system-ui" fontWeight="700" textAnchor="middle">¼</text>
      <rect x="156" y="22" width="22" height="28" rx="4" fill={C.greenLight} stroke={C.green} strokeWidth="1.5"/>
      <text x="167" y="41" fontSize="11" fill={C.green} fontFamily="system-ui" fontWeight="700" textAnchor="middle">¼</text>
      <rect x="180" y="22" width="22" height="28" rx="4" fill={C.greenLight} stroke={C.green} strokeWidth="1.5"/>
      <text x="191" y="41" fontSize="11" fill={C.green} fontFamily="system-ui" fontWeight="700" textAnchor="middle">¼</text>

      {/* Circle fraction diagram */}
      <circle cx="218" cy="36" r="24" fill={C.greenLight} stroke={C.green} strokeWidth="1.5"/>
      <path d="M218,36 L218,12 A24,24 0 0,1 242,36 Z" fill={C.green}/>
      <line x1="218" y1="12" x2="218" y2="60" stroke={C.green} strokeWidth="1.5"/>
      <line x1="194" y1="36" x2="242" y2="36" stroke={C.green} strokeWidth="1.5"/>
      <text x="228" y="26" fontSize="9" fill={C.white} fontFamily="system-ui" fontWeight="700" textAnchor="middle">¼</text>

      {/* Thirds row */}
      <text x="56" y="72" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">THIRDS</text>
      <rect x="56" y="78" width="16" height="22" rx="3" fill={C.amber} stroke={C.amber} strokeWidth="1.5"/>
      <text x="64" y="93" fontSize="10" fill={C.white} fontFamily="system-ui" fontWeight="700" textAnchor="middle">⅓</text>
      <rect x="74" y="78" width="16" height="22" rx="3" fill={C.amberLight} stroke={C.amber} strokeWidth="1.5"/>
      <text x="82" y="93" fontSize="10" fill={C.amber} fontFamily="system-ui" fontWeight="700" textAnchor="middle">⅓</text>
      <rect x="92" y="78" width="16" height="22" rx="3" fill={C.amberLight} stroke={C.amber} strokeWidth="1.5"/>
      <text x="100" y="93" fontSize="10" fill={C.amber} fontFamily="system-ui" fontWeight="700" textAnchor="middle">⅓</text>

      {/* Key insight */}
      <text x="120" y="90" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontStyle="italic">bigger bottom → smaller piece</text>
    </svg>
  )
}

function TimeIllustration() {
  // Clock face
  const cx = 60, cy = 60, r = 44
  const hourMarks = Array.from({ length: 12 }, (_, i) => {
    const angle = (i * 30 - 90) * (Math.PI / 180)
    const x1 = cx + (r - 6) * Math.cos(angle)
    const y1 = cy + (r - 6) * Math.sin(angle)
    const x2 = cx + r * Math.cos(angle)
    const y2 = cy + r * Math.sin(angle)
    return { x1, y1, x2, y2, label: i === 0 ? 12 : i }
  })
  // Quarter past 3 — hour hand between 3 and 4, minute hand at 3
  const minuteAngle = (90 - 90) * (Math.PI / 180) // pointing to 3
  const hourAngle = (90 + 7.5 - 90) * (Math.PI / 180) // between 3 and 4
  const mx = cx + 32 * Math.cos(minuteAngle)
  const my = cy + 32 * Math.sin(minuteAngle)
  const hx = cx + 22 * Math.cos(hourAngle)
  const hy = cy + 22 * Math.sin(hourAngle)

  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      {/* Analogue clock */}
      <circle cx={cx} cy={cy} r={r} fill={C.white} stroke={C.text} strokeWidth="2"/>
      <circle cx={cx} cy={cy} r={r - 2} fill="none" stroke={C.greenLight} strokeWidth="6"/>

      {/* Hour marks */}
      {hourMarks.map((m, i) => (
        <line key={i} x1={m.x1} y1={m.y1} x2={m.x2} y2={m.y2}
          stroke={C.text} strokeWidth={i % 3 === 0 ? 2 : 1} strokeLinecap="round"/>
      ))}

      {/* Numbers at 12, 3, 6, 9 */}
      <text x={cx} y={cy - r + 14} textAnchor="middle" fontSize="10" fill={C.text} fontFamily="system-ui" fontWeight="700">12</text>
      <text x={cx + r - 12} y={cy + 4} textAnchor="middle" fontSize="10" fill={C.text} fontFamily="system-ui" fontWeight="700">3</text>
      <text x={cx} y={cy + r - 6} textAnchor="middle" fontSize="10" fill={C.text} fontFamily="system-ui" fontWeight="700">6</text>
      <text x={cx - r + 12} y={cy + 4} textAnchor="middle" fontSize="10" fill={C.text} fontFamily="system-ui" fontWeight="700">9</text>

      {/* Minute hand (long, green) — pointing to 3 = quarter past */}
      <line x1={cx} y1={cy} x2={mx} y2={my} stroke={C.green} strokeWidth="3" strokeLinecap="round"/>
      {/* Hour hand (short, dark) — between 3 and 4 */}
      <line x1={cx} y1={cy} x2={hx} y2={hy} stroke={C.text} strokeWidth="4" strokeLinecap="round"/>
      <circle cx={cx} cy={cy} r="3" fill={C.text}/>

      {/* Digital equivalent */}
      <rect x="118" y="22" width="80" height="40" rx="8" fill={C.text}/>
      <text x="158" y="50" textAnchor="middle" fontSize="22" fill={C.greenMid}
        fontFamily="'Courier New', monospace" fontWeight="700" letterSpacing="2">3:15</text>
      <text x="158" y="72" textAnchor="middle" fontSize="10" fill={C.textMuted} fontFamily="system-ui">quarter past 3</text>

      {/* Quarter turn arc illustration */}
      <text x="134" y="92" textAnchor="middle" fontSize="10" fill={C.textMuted} fontFamily="system-ui">¼ turn</text>
      <path d="M 148 98 A 18 18 0 0 1 166 80" fill="none" stroke={C.amber} strokeWidth="2" strokeDasharray="3,2"/>
      <text x="178" y="92" textAnchor="middle" fontSize="10" fill={C.textMuted} fontFamily="system-ui">= 15 min</text>

      {/* Labels */}
      <text x="32" y="112" textAnchor="middle" fontSize="9" fill={C.green} fontFamily="system-ui" fontWeight="600">minute hand</text>
      <text x="88" y="112" textAnchor="middle" fontSize="9" fill={C.text} fontFamily="system-ui" fontWeight="600">hour hand</text>
    </svg>
  )
}

function StatisticsIllustration() {
  const data = [
    { label: 'Cats', count: 4, color: C.green },
    { label: 'Dogs', count: 7, color: C.blue },
    { label: 'Fish', count: 2, color: C.amber },
    { label: 'Rabbits', count: 5, color: C.purple },
  ]
  const maxCount = 8
  const barW = 28, gap = 12, startX = 28, baseY = 88

  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      {/* Title */}
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">OUR PETS — CLASS SURVEY</text>

      {/* Y-axis gridlines */}
      {[2, 4, 6, 8].map(v => {
        const y = baseY - (v / maxCount) * 64
        return (
          <g key={v}>
            <line x1={startX} y1={y} x2={startX + data.length * (barW + gap) - gap + 4} y2={y}
              stroke={C.bg} strokeWidth="1"/>
            <text x={startX - 4} y={y + 4} textAnchor="end" fontSize="9" fill={C.textMuted} fontFamily="system-ui">{v}</text>
          </g>
        )
      })}

      {/* Bars */}
      {data.map((d, i) => {
        const x = startX + i * (barW + gap)
        const barH = (d.count / maxCount) * 64
        return (
          <g key={i}>
            <rect x={x} y={baseY - barH} width={barW} height={barH} rx="3" fill={d.color} opacity="0.85"/>
            <text x={x + barW / 2} y={baseY - barH - 3} textAnchor="middle" fontSize="10"
              fill={d.color} fontFamily="system-ui" fontWeight="700">{d.count}</text>
            <text x={x + barW / 2} y={baseY + 10} textAnchor="middle" fontSize="9"
              fill={C.textMuted} fontFamily="system-ui">{d.label}</text>
          </g>
        )
      })}

      {/* Axis */}
      <line x1={startX} y1="18" x2={startX} y2={baseY} stroke={C.text} strokeWidth="1.5"/>
      <line x1={startX} y1={baseY} x2={startX + data.length * (barW + gap)} y2={baseY} stroke={C.text} strokeWidth="1.5"/>

      {/* Tally chart panel */}
      <rect x="168" y="18" width="68" height="76" rx="6" fill={C.bg} stroke={C.greenLight} strokeWidth="1.5"/>
      <text x="202" y="30" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">TALLY</text>
      {data.map((d, i) => (
        <g key={i}>
          <text x="174" y={44 + i * 14} fontSize="9" fill={C.textMuted} fontFamily="system-ui">{d.label}</text>
          <text x="210" y={44 + i * 14} fontSize="9" fill={d.color} fontFamily="system-ui" fontWeight="600">
            {'||||'.slice(0, Math.min(d.count, 4))}{d.count >= 5 ? ' ⧵' : ''}
            {d.count > 5 ? ' ' + '|'.repeat(d.count - 5) : ''}
          </text>
        </g>
      ))}
    </svg>
  )
}

function PositionDirectionIllustration() {
  const gridSize = 16, cols = 6, rows = 5
  const ox = 20, oy = 20

  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      {/* Grid */}
      {Array.from({ length: cols + 1 }, (_, i) => (
        <line key={`v${i}`} x1={ox + i * gridSize} y1={oy} x2={ox + i * gridSize} y2={oy + rows * gridSize}
          stroke={C.greenLight} strokeWidth="1"/>
      ))}
      {Array.from({ length: rows + 1 }, (_, i) => (
        <line key={`h${i}`} x1={ox} y1={oy + i * gridSize} x2={ox + cols * gridSize} y2={oy + i * gridSize}
          stroke={C.greenLight} strokeWidth="1"/>
      ))}

      {/* Robot start position (1,3) */}
      <rect x={ox + 1 * gridSize + 2} y={oy + 2 * gridSize + 2} width={gridSize - 4} height={gridSize - 4}
        rx="3" fill={C.green}/>
      <text x={ox + 1.5 * gridSize} y={oy + 2.5 * gridSize + 2} textAnchor="middle"
        fontSize="10" fill={C.white} fontFamily="system-ui">🤖</text>

      {/* Target position (4,1) */}
      <rect x={ox + 4 * gridSize + 2} y={oy + 1 * gridSize + 2} width={gridSize - 4} height={gridSize - 4}
        rx="3" fill={C.amberLight} stroke={C.amber} strokeWidth="1.5"/>
      <text x={ox + 4.5 * gridSize} y={oy + 1.5 * gridSize + 2} textAnchor="middle"
        fontSize="10" fill={C.amber} fontFamily="system-ui">⭐</text>

      {/* Arrows showing path: right x3, then up x1 */}
      {[1, 2, 3].map(i => (
        <line key={`r${i}`}
          x1={ox + (0.5 + i) * gridSize} y1={oy + 2.5 * gridSize}
          x2={ox + (0.5 + i + 0.7) * gridSize} y2={oy + 2.5 * gridSize}
          stroke={C.green} strokeWidth="2" markerEnd="url(#arr)" strokeLinecap="round"/>
      ))}
      <line x1={ox + 4.5 * gridSize} y1={oy + 2.5 * gridSize}
        x2={ox + 4.5 * gridSize} y2={oy + 1.5 * gridSize + 4}
        stroke={C.amber} strokeWidth="2" markerEnd="url(#arrAmber)" strokeLinecap="round"/>

      <defs>
        <marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 Z" fill={C.green}/>
        </marker>
        <marker id="arrAmber" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 Z" fill={C.amber}/>
        </marker>
      </defs>

      {/* Axis labels */}
      <text x={ox + 1.5 * gridSize} y={oy + rows * gridSize + 12} textAnchor="middle"
        fontSize="8" fill={C.textMuted} fontFamily="system-ui">1</text>
      {[2,3,4,5,6].map(n => (
        <text key={n} x={ox + (n - 0.5) * gridSize} y={oy + rows * gridSize + 12} textAnchor="middle"
          fontSize="8" fill={C.textMuted} fontFamily="system-ui">{n}</text>
      ))}

      {/* Compass rose */}
      <g transform="translate(168, 28)">
        <circle cx="18" cy="18" r="18" fill={C.blueLight} stroke={C.blue} strokeWidth="1"/>
        {/* N */}
        <line x1="18" y1="18" x2="18" y2="4" stroke={C.blue} strokeWidth="2.5" strokeLinecap="round"/>
        <polygon points="18,2 15,8 21,8" fill={C.blue}/>
        {/* S */}
        <line x1="18" y1="18" x2="18" y2="32" stroke={C.textMuted} strokeWidth="1.5" strokeLinecap="round"/>
        {/* E */}
        <line x1="18" y1="18" x2="32" y2="18" stroke={C.textMuted} strokeWidth="1.5" strokeLinecap="round"/>
        {/* W */}
        <line x1="18" y1="18" x2="4" y2="18" stroke={C.textMuted} strokeWidth="1.5" strokeLinecap="round"/>
        <text x="18" y="-1" textAnchor="middle" fontSize="8" fill={C.blue} fontFamily="system-ui" fontWeight="700">N</text>
        <text x="18" y="43" textAnchor="middle" fontSize="8" fill={C.textMuted} fontFamily="system-ui">S</text>
        <text x="38" y="21" textAnchor="middle" fontSize="8" fill={C.textMuted} fontFamily="system-ui">E</text>
        <text x="-2" y="21" textAnchor="middle" fontSize="8" fill={C.textMuted} fontFamily="system-ui">W</text>
      </g>

      {/* Turns diagram */}
      <text x="172" y="72" fontSize="9" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">TURNS</text>
      <path d="M 172 86 A 12 12 0 0 1 196 86" fill="none" stroke={C.amber} strokeWidth="2"/>
      <text x="184" y="100" textAnchor="middle" fontSize="8" fill={C.amber} fontFamily="system-ui">¼ turn</text>
      <path d="M 204 86 A 12 12 0 0 1 228 86" fill="none" stroke={C.purple} strokeWidth="2"/>
      <path d="M 204 86 A 12 12 0 1 0 228 86" fill="none" stroke={C.purple} strokeWidth="1" strokeDasharray="2,2"/>
      <text x="216" y="100" textAnchor="middle" fontSize="8" fill={C.purple} fontFamily="system-ui">½ turn</text>

      {/* Route key */}
      <text x="20" y="108" fontSize="8" fill={C.green} fontFamily="system-ui" fontWeight="600">→ 3 steps right</text>
      <text x="90" y="108" fontSize="8" fill={C.amber} fontFamily="system-ui" fontWeight="600">↑ 1 step up</text>
    </svg>
  )
}

function PlaceValueIllustration() {
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      {/* Number: 34 */}
      <text x="20" y="24" fontSize="42" fill={C.text} fontFamily="system-ui" fontWeight="700">34</text>

      {/* Column headers */}
      <rect x="90" y="8" width="52" height="20" rx="4" fill={C.blue} opacity="0.15"/>
      <text x="116" y="22" textAnchor="middle" fontSize="11" fill={C.blue} fontFamily="system-ui" fontWeight="700">tens</text>
      <rect x="148" y="8" width="52" height="20" rx="4" fill={C.amber} opacity="0.15"/>
      <text x="174" y="22" textAnchor="middle" fontSize="11" fill={C.amber} fontFamily="system-ui" fontWeight="700">ones</text>

      {/* 3 ten-rods */}
      {[0,1,2].map(i => (
        <g key={i} transform={`translate(${93 + i * 16}, 32)`}>
          {Array.from({length: 10}, (_, j) => (
            <rect key={j} x="0" y={j * 7} width="12" height="6" rx="1"
              fill={C.blue} opacity="0.7" stroke={C.white} strokeWidth="0.5"/>
          ))}
        </g>
      ))}
      {/* digit 3 */}
      <text x="116" y="110" textAnchor="middle" fontSize="22" fill={C.blue} fontFamily="system-ui" fontWeight="700">3</text>

      {/* 4 ones-cubes */}
      {[0,1,2,3].map(i => (
        <rect key={i} x={151 + (i % 2) * 14} y={32 + Math.floor(i / 2) * 14} width="12" height="12"
          rx="2" fill={C.amber} opacity="0.7" stroke={C.white} strokeWidth="0.5"/>
      ))}
      {/* digit 4 */}
      <text x="174" y="110" textAnchor="middle" fontSize="22" fill={C.amber} fontFamily="system-ui" fontWeight="700">4</text>

      {/* Divider line */}
      <line x1="88" y1="28" x2="88" y2="100" stroke={C.border} strokeWidth="1" strokeDasharray="3,2"/>

      {/* = 30 + 4 */}
      <text x="18" y="105" fontSize="11" fill={C.textMuted} fontFamily="system-ui">3 tens + 4 ones</text>
      <text x="18" y="118" fontSize="11" fill={C.textMuted} fontFamily="system-ui">= 30 + 4 = 34</text>
    </svg>
  )
}

function MultiplicationIllustration() {
  // 3 × 4 array
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="14" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">ARRAYS — 3 × 4</text>

      {/* 3 rows of 4 dots */}
      {Array.from({length: 3}, (_, row) =>
        Array.from({length: 4}, (_, col) => (
          <circle key={`${row}-${col}`}
            cx={20 + col * 22} cy={28 + row * 22} r="8"
            fill={C.green} opacity="0.8"/>
        ))
      )}

      {/* Row brace */}
      <text x="112" y="40" fontSize="11" fill={C.text} fontFamily="system-ui">3 rows</text>
      <text x="112" y="56" fontSize="11" fill={C.text} fontFamily="system-ui">of 4</text>

      {/* = repeated addition */}
      <text x="4" y="88" fontSize="11" fill={C.textMuted} fontFamily="system-ui">4 + 4 + 4 = 12</text>
      <text x="4" y="104" fontSize="14" fill={C.green} fontFamily="system-ui" fontWeight="700">3 × 4 = 12</text>

      {/* also 4 × 3 */}
      <text x="112" y="72" fontSize="10" fill={C.textMuted} fontFamily="system-ui">also written:</text>
      <text x="112" y="88" fontSize="14" fill={C.amber} fontFamily="system-ui" fontWeight="700">4 × 3 = 12</text>
      <text x="112" y="104" fontSize="9" fill={C.textMuted} fontFamily="system-ui" fontStyle="italic">order doesn't change the answer!</text>

      {/* Equal sign decoration */}
      <line x1="90" y1="76" x2="108" y2="76" stroke={C.border} strokeWidth="1" strokeDasharray="2,2"/>
    </svg>
  )
}

function AdditionSubtractionIllustration() {
  // Number line showing 34 + 25 = 59
  const y = 60
  const start = 20, end = 220
  const scale = (end - start) / 50 // show 30 to 80
  const toX = (n: number) => start + (n - 30) * scale

  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="14" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">NUMBER LINE — 34 + 25</text>

      {/* Number line */}
      <line x1={start} y1={y} x2={end} y2={y} stroke={C.text} strokeWidth="2"/>
      {/* Arrow */}
      <polygon points={`${end},${y} ${end-6},${y-4} ${end-6},${y+4}`} fill={C.text}/>

      {/* Ticks */}
      {[30,35,40,45,50,55,60,65,70,75,80].map(n => {
        const x = toX(n)
        return (
          <g key={n}>
            <line x1={x} y1={y-4} x2={x} y2={y+4} stroke={C.text} strokeWidth={n % 10 === 0 ? 2 : 1}/>
            {n % 10 === 0 && <text x={x} y={y + 14} textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">{n}</text>}
          </g>
        )
      })}

      {/* Start point 34 */}
      <circle cx={toX(34)} cy={y} r="5" fill={C.blue}/>
      <text x={toX(34)} y={y - 10} textAnchor="middle" fontSize="10" fill={C.blue} fontFamily="system-ui" fontWeight="700">34</text>

      {/* Jump +20 */}
      <path d={`M ${toX(34)} ${y} Q ${toX(44)} ${y-30} ${toX(54)} ${y}`}
        fill="none" stroke={C.green} strokeWidth="2.5" strokeLinecap="round"/>
      <text x={toX(44)} y={y - 35} textAnchor="middle" fontSize="10" fill={C.green} fontFamily="system-ui" fontWeight="600">+20</text>

      {/* Jump +5 */}
      <path d={`M ${toX(54)} ${y} Q ${toX(56.5)} ${y-18} ${toX(59)} ${y}`}
        fill="none" stroke={C.amber} strokeWidth="2.5" strokeLinecap="round"/>
      <text x={toX(56.5)} y={y - 22} textAnchor="middle" fontSize="10" fill={C.amber} fontFamily="system-ui" fontWeight="600">+5</text>

      {/* End point 59 */}
      <circle cx={toX(59)} cy={y} r="5" fill={C.green}/>
      <text x={toX(59)} y={y - 10} textAnchor="middle" fontSize="10" fill={C.green} fontFamily="system-ui" fontWeight="700">59</text>

      {/* Answer */}
      <text x="120" y="100" textAnchor="middle" fontSize="16" fill={C.green} fontFamily="system-ui" fontWeight="700">34 + 25 = 59</text>
      <text x="120" y="114" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">jump in tens, then ones</text>
    </svg>
  )
}

function ShapeIllustration() {
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">2D SHAPES</text>
      {/* Square */}
      <rect x="10" y="20" width="44" height="44" rx="2" fill={C.greenLight} stroke={C.green} strokeWidth="2"/>
      <text x="32" y="78" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">square</text>
      <text x="32" y="89" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">4 equal sides</text>

      {/* Rectangle */}
      <rect x="66" y="28" width="56" height="30" rx="2" fill={C.blueLight} stroke={C.blue} strokeWidth="2"/>
      <text x="94" y="78" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">rectangle</text>
      <text x="94" y="89" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">4 right angles</text>

      {/* Triangle */}
      <polygon points="154,20 134,64 174,64" fill={C.amberLight} stroke={C.amber} strokeWidth="2"/>
      <text x="154" y="78" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">triangle</text>
      <text x="154" y="89" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">3 sides</text>

      {/* Circle */}
      <circle cx="210" cy="42" r="22" fill={C.purpleLight} stroke={C.purple} strokeWidth="2"/>
      <text x="210" y="78" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">circle</text>
      <text x="210" y="89" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">no corners</text>

      {/* Right angle markers */}
      <polyline points="10,56 18,56 18,64" fill="none" stroke={C.green} strokeWidth="1.5"/>
      <polyline points="66,50 74,50 74,58" fill="none" stroke={C.blue} strokeWidth="1.5"/>
    </svg>
  )
}

function MoneyIllustration() {
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">MONEY</text>
      {/* Coins */}
      <circle cx="28" cy="50" r="20" fill={C.amberLight} stroke={C.amber} strokeWidth="2"/>
      <text x="28" y="54" textAnchor="middle" fontSize="10" fill={C.amber} fontFamily="system-ui" fontWeight="700">1p</text>

      <circle cx="78" cy="50" r="22" fill={C.amber} stroke={C.amber} strokeWidth="2"/>
      <text x="78" y="54" textAnchor="middle" fontSize="11" fill={C.white} fontFamily="system-ui" fontWeight="700">2p</text>

      <circle cx="130" cy="50" r="20" fill={C.amberLight} stroke={C.amber} strokeWidth="2"/>
      <text x="130" y="54" textAnchor="middle" fontSize="10" fill={C.amber} fontFamily="system-ui" fontWeight="700">5p</text>

      <circle cx="178" cy="50" r="22" fill={C.amber} stroke={C.amber} strokeWidth="2"/>
      <text x="178" y="54" textAnchor="middle" fontSize="11" fill={C.white} fontFamily="system-ui" fontWeight="700">10p</text>

      {/* Note */}
      <rect x="4" y="80" width="60" height="32" rx="4" fill={C.greenLight} stroke={C.green} strokeWidth="2"/>
      <text x="34" y="100" textAnchor="middle" fontSize="13" fill={C.green} fontFamily="system-ui" fontWeight="700">£1</text>

      <rect x="74" y="80" width="60" height="32" rx="4" fill={C.blueLight} stroke={C.blue} strokeWidth="2"/>
      <text x="104" y="100" textAnchor="middle" fontSize="13" fill={C.blue} fontFamily="system-ui" fontWeight="700">£5</text>

      <text x="148" y="97" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontStyle="italic">coins + notes</text>
      <text x="148" y="110" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontStyle="italic">make any amount</text>
    </svg>
  )
}

function DecimalsIllustration() {
  // 10×10 grid showing 0.37 shaded
  const cells: React.ReactElement[] = []
  for (let row = 0; row < 5; row++) {
    for (let col = 0; col < 10; col++) {
      const idx = row * 10 + col
      const shaded = idx < 37
      cells.push(
        <rect key={idx} x={4 + col * 11} y={18 + row * 11} width="10" height="10"
          fill={shaded ? C.blue : C.blueLight} stroke={C.white} strokeWidth="0.5"/>
      )
    }
  }
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">DECIMALS</text>
      {cells}
      <text x="4" y="84" fontSize="9" fill={C.textMuted} fontFamily="system-ui">5 rows of 10 = 50 squares</text>
      <text x="4" y="95" fontSize="9" fill={C.blue} fontFamily="system-ui" fontWeight="600">37 shaded = 0.37</text>
      {/* Number line */}
      <line x1="120" y1="55" x2="235" y2="55" stroke={C.text} strokeWidth="1.5"/>
      <circle cx="120" cy="55" r="3" fill={C.text}/>
      <circle cx="235" cy="55" r="3" fill={C.text}/>
      <circle cx="177" cy="55" r="4" fill={C.amber}/>
      <text x="120" y="68" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">0</text>
      <text x="177" y="68" textAnchor="middle" fontSize="9" fill={C.amber} fontFamily="system-ui" fontWeight="700">0.5</text>
      <text x="235" y="68" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">1</text>
      <text x="177" y="90" textAnchor="middle" fontSize="10" fill={C.amber} fontFamily="system-ui" fontWeight="700">½ = 0.5</text>
      <text x="177" y="105" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">between 0 and 1</text>
    </svg>
  )
}

function PercentagesIllustration() {
  // 10×10 grid showing 25% shaded
  const cells: React.ReactElement[] = []
  for (let row = 0; row < 10; row++) {
    for (let col = 0; col < 10; col++) {
      const idx = row * 10 + col
      const shaded = idx < 25
      cells.push(
        <rect key={idx} x={4 + col * 10} y={14 + row * 10} width="9" height="9"
          fill={shaded ? C.purple : C.purpleLight} stroke={C.white} strokeWidth="0.5"/>
      )
    }
  }
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="11" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">PERCENTAGES</text>
      {cells}
      <text x="120" y="30" fontSize="28" fill={C.purple} fontFamily="system-ui" fontWeight="700">25%</text>
      <text x="120" y="52" fontSize="11" fill={C.textMuted} fontFamily="system-ui">= 25 out of 100</text>
      <line x1="120" y1="62" x2="235" y2="62" stroke={C.border} strokeWidth="1"/>
      <text x="120" y="78" fontSize="11" fill={C.purple} fontFamily="system-ui" fontWeight="600">25% = ¼ = 0.25</text>
      <text x="120" y="93" fontSize="10" fill={C.textMuted} fontFamily="system-ui">per cent = per hundred</text>
      <text x="120" y="108" fontSize="9" fill={C.textMuted} fontFamily="system-ui" fontStyle="italic">25 squares shaded ←</text>
    </svg>
  )
}

function PerimeterAreaIllustration() {
  const rx = 20, ry = 28, rw = 140, rh = 65
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">PERIMETER &amp; AREA</text>
      {/* Rectangle fill for area */}
      <rect x={rx} y={ry} width={rw} height={rh} rx="3" fill={C.greenLight}/>
      {/* Area label inside */}
      <text x={rx + rw/2} y={ry + rh/2 - 6} textAnchor="middle" fontSize="10" fill={C.green} fontFamily="system-ui" fontWeight="700">Area = l × w</text>
      <text x={rx + rw/2} y={ry + rh/2 + 8} textAnchor="middle" fontSize="11" fill={C.green} fontFamily="system-ui" fontWeight="700">= 7 × 3 = 21 cm²</text>
      {/* Border for perimeter */}
      <rect x={rx} y={ry} width={rw} height={rh} rx="3" fill="none" stroke={C.amber} strokeWidth="3" strokeDasharray="6 3"/>
      {/* Width arrow */}
      <line x1={rx} y1={ry + rh + 10} x2={rx + rw} y2={ry + rh + 10} stroke={C.text} strokeWidth="1.5" markerEnd="url(#arr)"/>
      <text x={rx + rw/2} y={ry + rh + 22} textAnchor="middle" fontSize="10" fill={C.text} fontFamily="system-ui">7 cm</text>
      {/* Height arrow */}
      <line x1={rx + rw + 10} y1={ry} x2={rx + rw + 10} y2={ry + rh} stroke={C.text} strokeWidth="1.5"/>
      <text x={rx + rw + 22} y={ry + rh/2 + 4} textAnchor="middle" fontSize="10" fill={C.text} fontFamily="system-ui">3 cm</text>
      {/* Perimeter label */}
      <text x="185" y="36" fontSize="9" fill={C.amber} fontFamily="system-ui" fontWeight="600">Perimeter</text>
      <text x="185" y="48" fontSize="9" fill={C.amber} fontFamily="system-ui">= 2×(l+w)</text>
      <text x="185" y="60" fontSize="9" fill={C.amber} fontFamily="system-ui">= 20 cm</text>
    </svg>
  )
}

function VolumeCapacityIllustration() {
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">VOLUME &amp; CAPACITY</text>
      {/* Jug outline */}
      <path d="M 30 20 L 30 100 L 90 100 L 90 20 Z" fill={C.blueLight} stroke={C.blue} strokeWidth="2"/>
      {/* Spout */}
      <path d="M 90 35 Q 108 35 108 48 Q 108 60 90 60" fill="none" stroke={C.blue} strokeWidth="2"/>
      {/* Water fill 75% */}
      <rect x="31" y="41" width="58" height="58" fill={C.blue} opacity="0.35"/>
      {/* Scale marks */}
      <line x1="25" y1="41" x2="30" y2="41" stroke={C.text} strokeWidth="1.5"/>
      <text x="20" y="44" textAnchor="end" fontSize="9" fill={C.text} fontFamily="system-ui">750</text>
      <line x1="25" y1="60" x2="30" y2="60" stroke={C.text} strokeWidth="1.5"/>
      <text x="20" y="63" textAnchor="end" fontSize="9" fill={C.text} fontFamily="system-ui">500</text>
      <line x1="25" y1="80" x2="30" y2="80" stroke={C.text} strokeWidth="1.5"/>
      <text x="20" y="83" textAnchor="end" fontSize="9" fill={C.text} fontFamily="system-ui">250</text>
      <text x="60" y="116" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">ml / litres</text>
      {/* Key facts */}
      <text x="120" y="38" fontSize="11" fill={C.blue} fontFamily="system-ui" fontWeight="700">1 litre = 1000 ml</text>
      <text x="120" y="56" fontSize="10" fill={C.textMuted} fontFamily="system-ui">Capacity = how much</text>
      <text x="120" y="70" fontSize="10" fill={C.textMuted} fontFamily="system-ui">a container holds</text>
      <text x="120" y="90" fontSize="10" fill={C.textMuted} fontFamily="system-ui">Volume = how much</text>
      <text x="120" y="104" fontSize="10" fill={C.textMuted} fontFamily="system-ui">space an object takes</text>
    </svg>
  )
}

function MassWeightIllustration() {
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">MASS &amp; WEIGHT</text>
      {/* Balance beam pivot */}
      <line x1="90" y1="40" x2="90" y2="90" stroke={C.text} strokeWidth="2"/>
      <polygon points="90,90 75,108 105,108" fill={C.text}/>
      {/* Beam - tilted left (left side heavier) */}
      <line x1="20" y1="52" x2="160" y2="28" stroke={C.text} strokeWidth="2.5" strokeLinecap="round"/>
      {/* Left pan (heavy) */}
      <line x1="24" y1="52" x2="24" y2="65" stroke={C.text} strokeWidth="1.5"/>
      <line x1="14" y1="52" x2="34" y2="52" stroke={C.text} strokeWidth="1"/>
      <rect x="12" y="65" width="24" height="8" rx="2" fill={C.amber} stroke={C.amber} strokeWidth="1.5"/>
      <text x="24" y="73" textAnchor="middle" fontSize="8" fill={C.white} fontFamily="system-ui" fontWeight="700">500g</text>
      {/* Right pan (light) */}
      <line x1="156" y1="28" x2="156" y2="44" stroke={C.text} strokeWidth="1.5"/>
      <line x1="146" y1="28" x2="166" y2="28" stroke={C.text} strokeWidth="1"/>
      <rect x="144" y="44" width="24" height="8" rx="2" fill={C.greenLight} stroke={C.green} strokeWidth="1.5"/>
      <text x="156" y="52" textAnchor="middle" fontSize="8" fill={C.green} fontFamily="system-ui" fontWeight="700">100g</text>
      {/* Key facts */}
      <text x="175" y="40" fontSize="10" fill={C.text} fontFamily="system-ui" fontWeight="700">1 kg = 1000 g</text>
      <text x="175" y="56" fontSize="9" fill={C.textMuted} fontFamily="system-ui">heavier side</text>
      <text x="175" y="68" fontSize="9" fill={C.textMuted} fontFamily="system-ui">goes down</text>
    </svg>
  )
}

function LengthHeightIllustration() {
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">LENGTH &amp; HEIGHT</text>
      {/* Ruler */}
      <rect x="10" y="22" width="150" height="24" rx="3" fill={C.amberLight} stroke={C.amber} strokeWidth="2"/>
      {[0,1,2,3,4,5,6,7,8,9,10].map(i => (
        <g key={i}>
          <line x1={10 + i*15} y1="22" x2={10 + i*15} y2={i % 5 === 0 ? 34 : 30} stroke={C.amber} strokeWidth="1.5"/>
          {i % 5 === 0 && <text x={10 + i*15} y="52" textAnchor="middle" fontSize="9" fill={C.amber} fontFamily="system-ui">{i}</text>}
        </g>
      ))}
      <text x="85" y="59" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">centimetres (cm)</text>
      {/* Height measurement */}
      <line x1="190" y1="18" x2="190" y2="105" stroke={C.blue} strokeWidth="2" strokeDasharray="4 2"/>
      <line x1="183" y1="18" x2="197" y2="18" stroke={C.blue} strokeWidth="2"/>
      <line x1="183" y1="105" x2="197" y2="105" stroke={C.blue} strokeWidth="2"/>
      <text x="210" y="62" textAnchor="middle" fontSize="10" fill={C.blue} fontFamily="system-ui" fontWeight="700" transform="rotate(90,210,62)">height</text>
      {/* Unit reminders */}
      <text x="10" y="78" fontSize="9" fill={C.textMuted} fontFamily="system-ui">mm · cm · m · km</text>
      <text x="10" y="92" fontSize="9" fill={C.green} fontFamily="system-ui" fontWeight="600">10 mm = 1 cm</text>
      <text x="10" y="106" fontSize="9" fill={C.green} fontFamily="system-ui" fontWeight="600">100 cm = 1 m</text>
    </svg>
  )
}

function NegativeNumbersIllustration() {
  const y = 55
  const toX = (n: number) => 120 + n * 18
  const marks = [-5,-4,-3,-2,-1,0,1,2,3,4,5]
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">NEGATIVE NUMBERS</text>
      {/* Number line */}
      <line x1={toX(-5) - 8} y1={y} x2={toX(5) + 8} y2={y} stroke={C.text} strokeWidth="2"/>
      {marks.map(n => (
        <g key={n}>
          <line x1={toX(n)} y1={y-6} x2={toX(n)} y2={y+6} stroke={n === 0 ? C.text : C.textMuted} strokeWidth={n === 0 ? 2 : 1}/>
          <text x={toX(n)} y={y+18} textAnchor="middle" fontSize="9"
            fill={n < 0 ? C.blue : n === 0 ? C.text : C.green}
            fontFamily="system-ui" fontWeight={n === 0 ? '700' : '400'}>{n}</text>
        </g>
      ))}
      {/* Arrow from -3 to 2 */}
      <path d={`M ${toX(-3)} ${y-14} Q ${toX(-0.5)} ${y-34} ${toX(2)} ${y-14}`}
        fill="none" stroke={C.amber} strokeWidth="2" strokeLinecap="round"/>
      <text x={toX(-0.5)} y={y-38} textAnchor="middle" fontSize="9" fill={C.amber} fontFamily="system-ui" fontWeight="600">+5</text>
      {/* Temperature context */}
      <text x="10" y="95" fontSize="9" fill={C.textMuted} fontFamily="system-ui">−3°C is colder than 2°C</text>
      <text x="10" y="109" fontSize="9" fill={C.blue} fontFamily="system-ui" fontWeight="600">below zero → negative</text>
    </svg>
  )
}

function AlgebraIllustration() {
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">ALGEBRA</text>
      {/* Bar model: n + 4 = 10 */}
      <text x="120" y="30" textAnchor="middle" fontSize="13" fill={C.purple} fontFamily="system-ui" fontWeight="700">n + 4 = 10</text>
      {/* Total bar */}
      <rect x="20" y="38" width="110" height="20" rx="3" fill={C.purpleLight} stroke={C.purple} strokeWidth="2"/>
      <text x="75" y="52" textAnchor="middle" fontSize="11" fill={C.purple} fontFamily="system-ui" fontWeight="700">10</text>
      {/* Split bar */}
      <rect x="20" y="66" width="66" height="20" rx="3" fill={C.purple} stroke={C.purple} strokeWidth="2"/>
      <text x="53" y="80" textAnchor="middle" fontSize="11" fill={C.white} fontFamily="system-ui" fontWeight="700">n = ?</text>
      <rect x="90" y="66" width="40" height="20" rx="3" fill={C.purpleLight} stroke={C.purple} strokeWidth="2"/>
      <text x="110" y="80" textAnchor="middle" fontSize="11" fill={C.purple} fontFamily="system-ui" fontWeight="700">4</text>
      {/* Arrow to answer */}
      <text x="150" y="52" fontSize="11" fill={C.textMuted} fontFamily="system-ui">→</text>
      <text x="165" y="52" fontSize="12" fill={C.green} fontFamily="system-ui" fontWeight="700">n = 6</text>
      <text x="20" y="106" fontSize="9" fill={C.textMuted} fontFamily="system-ui" fontStyle="italic">a letter stands for an unknown number</text>
    </svg>
  )
}

function RatioIllustration() {
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">RATIO</text>
      {/* Ratio 2:3 shown as coloured squares */}
      <text x="120" y="28" textAnchor="middle" fontSize="16" fill={C.text} fontFamily="system-ui" fontWeight="700">2 : 3</text>
      {/* One set */}
      <rect x="16" y="36" width="20" height="20" rx="3" fill={C.blue}/>
      <rect x="40" y="36" width="20" height="20" rx="3" fill={C.blue}/>
      <rect x="64" y="36" width="20" height="20" rx="3" fill={C.amber}/>
      <rect x="88" y="36" width="20" height="20" rx="3" fill={C.amber}/>
      <rect x="112" y="36" width="20" height="20" rx="3" fill={C.amber}/>
      {/* Two sets */}
      <rect x="16" y="62" width="20" height="20" rx="3" fill={C.blue}/>
      <rect x="40" y="62" width="20" height="20" rx="3" fill={C.blue}/>
      <rect x="64" y="62" width="20" height="20" rx="3" fill={C.blue}/>
      <rect x="88" y="62" width="20" height="20" rx="3" fill={C.blue}/>
      <rect x="112" y="62" width="20" height="20" rx="3" fill={C.amber}/>
      <rect x="136" y="62" width="20" height="20" rx="3" fill={C.amber}/>
      <rect x="160" y="62" width="20" height="20" rx="3" fill={C.amber}/>
      <rect x="184" y="62" width="20" height="20" rx="3" fill={C.amber}/>
      <rect x="208" y="62" width="20" height="20" rx="3" fill={C.amber}/>
      <text x="148" y="52" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">1 part</text>
      <text x="60" y="96" fontSize="9" fill={C.textMuted} fontFamily="system-ui">for every 2 blue, 3 amber</text>
      <text x="60" y="110" fontSize="9" fill={C.textMuted} fontFamily="system-ui" fontStyle="italic">ratio stays the same when scaled</text>
    </svg>
  )
}

function ConvertingUnitsIllustration() {
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      <text x="4" y="13" fontSize="10" fill={C.textMuted} fontFamily="system-ui" fontWeight="600">CONVERTING UNITS</text>
      {/* Length row */}
      <rect x="10" y="22" width="44" height="22" rx="4" fill={C.blueLight} stroke={C.blue} strokeWidth="1.5"/>
      <text x="32" y="37" textAnchor="middle" fontSize="10" fill={C.blue} fontFamily="system-ui" fontWeight="700">km</text>
      <text x="68" y="30" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">×1000</text>
      <line x1="56" y1="33" x2="80" y2="33" stroke={C.text} strokeWidth="1.5" markerEnd="url(#a)"/>
      <text x="68" y="43" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">÷1000</text>
      <rect x="82" y="22" width="44" height="22" rx="4" fill={C.blueLight} stroke={C.blue} strokeWidth="1.5"/>
      <text x="104" y="37" textAnchor="middle" fontSize="10" fill={C.blue} fontFamily="system-ui" fontWeight="700">m</text>
      <text x="140" y="30" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">×100</text>
      <line x1="128" y1="33" x2="152" y2="33" stroke={C.text} strokeWidth="1.5"/>
      <text x="140" y="43" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">÷100</text>
      <rect x="154" y="22" width="44" height="22" rx="4" fill={C.blueLight} stroke={C.blue} strokeWidth="1.5"/>
      <text x="176" y="37" textAnchor="middle" fontSize="10" fill={C.blue} fontFamily="system-ui" fontWeight="700">cm</text>

      {/* Mass row */}
      <rect x="10" y="58" width="44" height="22" rx="4" fill={C.amberLight} stroke={C.amber} strokeWidth="1.5"/>
      <text x="32" y="73" textAnchor="middle" fontSize="10" fill={C.amber} fontFamily="system-ui" fontWeight="700">kg</text>
      <text x="68" y="65" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">×1000</text>
      <line x1="56" y1="69" x2="80" y2="69" stroke={C.text} strokeWidth="1.5"/>
      <text x="68" y="79" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">÷1000</text>
      <rect x="82" y="58" width="44" height="22" rx="4" fill={C.amberLight} stroke={C.amber} strokeWidth="1.5"/>
      <text x="104" y="73" textAnchor="middle" fontSize="10" fill={C.amber} fontFamily="system-ui" fontWeight="700">g</text>

      {/* Capacity row */}
      <rect x="10" y="94" width="44" height="22" rx="4" fill={C.greenLight} stroke={C.green} strokeWidth="1.5"/>
      <text x="32" y="109" textAnchor="middle" fontSize="10" fill={C.green} fontFamily="system-ui" fontWeight="700">l</text>
      <text x="68" y="101" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">×1000</text>
      <line x1="56" y1="105" x2="80" y2="105" stroke={C.text} strokeWidth="1.5"/>
      <text x="68" y="115" textAnchor="middle" fontSize="9" fill={C.textMuted} fontFamily="system-ui">÷1000</text>
      <rect x="82" y="94" width="44" height="22" rx="4" fill={C.greenLight} stroke={C.green} strokeWidth="1.5"/>
      <text x="104" y="109" textAnchor="middle" fontSize="10" fill={C.green} fontFamily="system-ui" fontWeight="700">ml</text>
    </svg>
  )
}

function DefaultIllustration() {
  return (
    <svg viewBox="0 0 240 120" aria-hidden="true" style={{ width: '100%', height: '100%' }}>
      {/* Decorative maths symbols */}
      <text x="20" y="70" fontSize="48" fill={C.greenLight} fontFamily="system-ui" fontWeight="700">+</text>
      <text x="70" y="55" fontSize="36" fill={C.amberLight} fontFamily="system-ui" fontWeight="700">×</text>
      <text x="115" y="72" fontSize="50" fill={C.blueLight} fontFamily="system-ui" fontWeight="700">÷</text>
      <text x="165" y="58" fontSize="38" fill={C.purpleLight} fontFamily="system-ui" fontWeight="700">−</text>
      <text x="55" y="108" fontSize="13" fill={C.textMuted} fontFamily="system-ui" fontStyle="italic">
        concrete → pictorial → abstract
      </text>
    </svg>
  )
}

function getTopicKey(unitTitle: string): string {
  const t = unitTitle.toLowerCase()
  // Check more specific topics first to avoid false matches
  if (t.includes('converting unit') || t.includes('convert')) return 'converting'
  if (t.includes('percent') || (t.includes('fraction') && t.includes('decimal'))) return 'percentages'
  if (t.includes('decimal')) return 'decimals'
  if (t.includes('ratio')) return 'ratio'
  if (t.includes('algebra')) return 'algebra'
  if (t.includes('negative')) return 'negative'
  if (t.includes('perimeter') || t.includes('area') || t.includes('volume')) return 'perimeter'
  if (t.includes('mass') || t.includes('weight')) return 'mass'
  if (t.includes('capacity') || (t.includes('volume') && !t.includes('area'))) return 'capacity'
  if (t.includes('length') || t.includes('height')) return 'length'
  if (t.includes('money') || t.includes('coin') || t.includes('pound') || t.includes('pence')) return 'money'
  if (t.includes('fraction') || t.includes('half') || t.includes('quarter') || t.includes('third')) return 'fractions'
  if (t.includes('time') || t.includes('clock') || t.includes("o'clock") || t.includes('past')) return 'time'
  if (t.includes('statistic') || t.includes('tally') || t.includes('pictogram') || t.includes('chart') || t.includes('data')) return 'statistics'
  if (t.includes('position') || t.includes('direction') || t.includes('turn') || t.includes('compass')) return 'position'
  if (t.includes('place value') || t.includes('tens') || t.includes('ones')) return 'placevalue'
  if (t.includes('multipl') || t.includes('division') || t.includes('times table')) return 'multiplication'
  if (t.includes('addition') || t.includes('subtraction') || t.includes('add') || t.includes('subtract')) return 'addition'
  if (t.includes('shape') || t.includes('geometry')) return 'shape'
  return 'default'
}

export function ConceptIllustration({ unitTitle }: { unitTitle: string }) {
  const key = getTopicKey(unitTitle)
  const map: Record<string, React.ReactElement> = {
    fractions: <FractionsIllustration />,
    time: <TimeIllustration />,
    statistics: <StatisticsIllustration />,
    position: <PositionDirectionIllustration />,
    placevalue: <PlaceValueIllustration />,
    multiplication: <MultiplicationIllustration />,
    addition: <AdditionSubtractionIllustration />,
    shape: <ShapeIllustration />,
    money: <MoneyIllustration />,
    decimals: <DecimalsIllustration />,
    percentages: <PercentagesIllustration />,
    perimeter: <PerimeterAreaIllustration />,
    capacity: <VolumeCapacityIllustration />,
    mass: <MassWeightIllustration />,
    length: <LengthHeightIllustration />,
    negative: <NegativeNumbersIllustration />,
    algebra: <AlgebraIllustration />,
    ratio: <RatioIllustration />,
    converting: <ConvertingUnitsIllustration />,
    default: <DefaultIllustration />,
  }
  return map[key] ?? <DefaultIllustration />
}

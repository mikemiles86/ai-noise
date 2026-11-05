```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1b1640"/>
      <stop offset="1" stop-color="#3b1d5e"/>
    </linearGradient>
    <linearGradient id="key" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f4f1fb"/>
      <stop offset="1" stop-color="#c9c2dd"/>
    </linearGradient>
  </defs>
  <rect width="800" height="600" fill="url(#bg)"/>

  <!-- floating glyphs -->
  <g font-family="sans-serif" fill="#ffd36e" opacity="0.85">
    <text x="60" y="80" font-size="42" transform="rotate(-12 60 80)">≧</text>
    <text x="150" y="130" font-size="30" fill="#7fe3ff">⇣</text>
    <text x="250" y="70" font-size="38" fill="#ff8fb1" transform="rotate(15 250 70)">א</text>
    <text x="360" y="120" font-size="34">Τ</text>
    <text x="470" y="60" font-size="40" fill="#7fe3ff" transform="rotate(-20 470 60)">≱</text>
    <text x="560" y="130" font-size="32" fill="#b7ff8a">Ӓ</text>
    <text x="660" y="80" font-size="44" fill="#ff8fb1">⇢</text>
    <text x="730" y="160" font-size="30">ぷ</text>
    <text x="90" y="200" font-size="28" fill="#b7ff8a">佔</text>
    <text x="680" y="230" font-size="30" fill="#7fe3ff">亙</text>
    <text x="40" y="280" font-size="26" fill="#ff8fb1">Ȝ</text>
  </g>

  <!-- birthday cake -->
  <g transform="translate(330 150)">
    <rect x="0" y="60" width="140" height="70" rx="10" fill="#ff8fb1"/>
    <path d="M0 75 q17 18 35 0 q17 18 35 0 q17 18 35 0 q17 18 35 0 V60 H0Z" fill="#fff4e0"/>
    <rect x="-10" y="128" width="160" height="12" rx="6" fill="#e6dff5"/>
    <g fill="#7fe3ff">
      <rect x="30" y="25" width="10" height="38" rx="3"/>
      <rect x="65" y="20" width="10" height="43" rx="3"/>
      <rect x="100" y="25" width="10" height="38" rx="3"/>
    </g>
    <g fill="#ffd36e">
      <ellipse cx="35" cy="15" rx="6" ry="10"/>
      <ellipse cx="70" cy="10" rx="6" ry="10"/>
      <ellipse cx="105" cy="15" rx="6" ry="10"/>
    </g>
  </g>

  <!-- keyboard -->
  <g transform="translate(90 320)">
    <rect width="620" height="230" rx="22" fill="#2a2448" stroke="#5a4f8a" stroke-width="3"/>
    <g font-family="monospace" font-size="22" text-anchor="middle" fill="#2a2448" font-weight="bold">
      <!-- row 1 -->
      <g transform="translate(25 20)">
        <rect x="0" width="50" height="45" rx="8" fill="url(#key)"/><text x="25" y="30">Q</text>
        <rect x="58" width="50" height="45" rx="8" fill="#ffd36e"/><text x="83" y="30">W</text>
        <rect x="116" width="50" height="45" rx="8" fill="url(#key)"/><text x="141" y="30">E</text>
        <rect x="174" width="50" height="45" rx="8" fill="url(#key)"/><text x="199" y="30">R</text>
        <rect x="232" width="50" height="45" rx="8" fill="#ff8fb1"/><text x="257" y="30">T</text>
        <rect x="290" width="50" height="45" rx="8" fill="url(#key)"/><text x="315" y="30">Y</text>
        <rect x="348" width="50" height="45" rx="8" fill="url(#key)"/><text x="373" y="30">U</text>
        <rect x="406" width="50" height="45" rx="8" fill="url(#key)"/><text x="431" y="30">I</text>
        <rect x="464" width="50" height="45" rx="8" fill="#7fe3ff"/><text x="489" y="30">O</text>
        <rect x="522" width="50" height="45" rx="8" fill="#b7ff8a"/><text x="547" y="30">P</text>
      </g>
      <!-- row 2 -->
      <g transform="translate(50 75)">
        <rect x="0" width="50" height="45" rx="8" fill="#ffd36e"/><text x="25" y="30">A</text>
        <rect x="58" width="50" height="45" rx="8" fill="#ff8fb1"/><text x="83" y="30">S</text>
        <rect x="116" width="50" height="45" rx="8" fill="#7fe3ff"/><text x="141" y="30">D</text>
        <rect x="174" width="50" height="45" rx="8" fill="url(#key)"/><text x="199" y="30">F</text>
        <rect x="232" width="50" height="45" rx="8" fill="url(#key)"/><text x="257" y="30">G</text>
        <rect x="290" width="50" height="45" rx="8" fill="#b7ff8a"/><text x="315" y="30">H</text>
        <rect x="348" width="50" height="45" rx="8" fill="#ffd36e"/><text x="373" y="30">J</text>
        <rect x="406" width="50" height="45" rx="8" fill="url(#key)"/><text x="431" y="30">K</text>
        <rect x="464" width="50" height="45" rx="8" fill="url(#key)"/><text x="489" y="30">L</text>
        <rect x="522" width="40" height="45" rx="8" fill="#ff8fb1"/><text x="542" y="30">;</text>
      </g>
      <!-- row 3 -->
      <g transform="translate(80 130)">
        <rect x="0" width="50" height="45" rx="8" fill="#7fe3ff"/><text x="25" y="30">Z</text>
        <rect x="58" width="50" height="45" rx="8" fill="#ffd36e"/><text x="83" y="30">X</text>
        <rect x="116" width="50" height="45" rx="8" fill="#ff8fb1"/><text x="141" y="30">C</text>
        <rect x="174" width="50" height="45" rx="8" fill="#b7ff8a"/><text x="199" y="30">V</text>
        <rect x="232" width="50" height="45" rx="8" fill="#7fe3ff"/><text x="257" y="30">B</text>
        <rect x="290" width="50" height="45" rx="8" fill="#ffd36e"/><text x="315" y="30">N</text>
        <rect x="348" width="50" height="45" rx="8" fill="#ff8fb1"/><text x="373" y="30">M</text>
        <rect x="406" width="50" height="45" rx="8" fill="url(#key)"/><text x="431" y="30">!</text>
      </g>
      <rect x="170" y="185" width="280" height="32" rx="8" fill="url(#key)"/>
    </g>
  </g>

  <!-- motion sparks around keyboard -->
  <g stroke="#ffd36e" stroke-width="3" stroke-linecap="round" opacity="0.8">
    <line x1="70" y1="330" x2="45" y2="310"/>
    <line x1="60" y1="380" x2="30" y2="380"/>
    <line x1="730" y1="330" x2="755" y2="310"/>
    <line x1="740" y1="380" x2="770" y2="380"/>
  </g>
</svg>
```
Keyboard Mash Birthday
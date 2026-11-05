<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2b1b5a"/>
      <stop offset="0.6" stop-color="#c25b9e"/>
      <stop offset="1" stop-color="#ffb36b"/>
    </linearGradient>
    <radialGradient id="moon" cx="0.4" cy="0.4" r="0.6">
      <stop offset="0" stop-color="#fff8d0"/>
      <stop offset="1" stop-color="#f2c94c"/>
    </radialGradient>
  </defs>

  <!-- Sky -->
  <rect width="800" height="600" fill="url(#sky)"/>

  <!-- Moon with rings -->
  <circle cx="620" cy="130" r="60" fill="url(#moon)"/>
  <ellipse cx="620" cy="130" rx="105" ry="18" fill="none" stroke="#ffe9a8" stroke-width="5" transform="rotate(-15 620 130)"/>

  <!-- Stars -->
  <g fill="#fff">
    <circle cx="80" cy="60" r="2"/><circle cx="200" cy="110" r="3"/>
    <circle cx="340" cy="50" r="2"/><circle cx="460" cy="90" r="2.5"/>
    <circle cx="740" cy="250" r="2"/><circle cx="130" cy="180" r="1.5"/>
  </g>

  <!-- Rolling hills -->
  <path d="M0 420 Q150 340 300 410 T600 400 T800 380 V600 H0Z" fill="#3f8f6b"/>
  <path d="M0 480 Q200 420 400 480 T800 470 V600 H0Z" fill="#2c6b50"/>

  <!-- Wobbly rail track -->
  <path d="M0 540 C200 500 300 580 500 530 S750 510 800 520" fill="none" stroke="#5a3a22" stroke-width="10"/>
  <path d="M0 560 C200 520 300 600 500 550 S750 530 800 540" fill="none" stroke="#5a3a22" stroke-width="10"/>

  <!-- Bloock creature -->
  <g transform="translate(170 360)">
    <rect x="-55" y="-60" width="110" height="110" rx="25" fill="#ff7a59"/>
    <circle cx="-20" cy="-20" r="16" fill="#fff"/><circle cx="-17" cy="-18" r="7" fill="#222"/>
    <circle cx="22" cy="-22" r="10" fill="#fff"/><circle cx="24" cy="-21" r="4" fill="#222"/>
    <path d="M-25 15 Q0 35 25 15" stroke="#222" stroke-width="5" fill="none" stroke-linecap="round"/>
    <line x1="-30" y1="-60" x2="-45" y2="-100" stroke="#ff7a59" stroke-width="6"/>
    <circle cx="-45" cy="-104" r="9" fill="#ffe14d"/>
    <rect x="-40" y="48" width="18" height="30" rx="8" fill="#e05a3c"/>
    <rect x="22" y="48" width="18" height="30" rx="8" fill="#e05a3c"/>
  </g>

  <!-- Troupwead tall swaying plant-creature -->
  <g transform="translate(400 420)">
    <path d="M0 0 C-30 -80 40 -140 0 -220" stroke="#8be36a" stroke-width="14" fill="none" stroke-linecap="round"/>
    <ellipse cx="0" cy="-235" rx="40" ry="28" fill="#b46bff"/>
    <circle cx="-14" cy="-240" r="8" fill="#fff"/><circle cx="-13" cy="-240" r="3.5" fill="#222"/>
    <circle cx="14" cy="-240" r="8" fill="#fff"/><circle cx="15" cy="-240" r="3.5" fill="#222"/>
    <path d="M-10 -222 Q0 -214 10 -222" stroke="#222" stroke-width="3" fill="none"/>
    <path d="M-5 -110 Q-50 -130 -60 -100" stroke="#8be36a" stroke-width="8" fill="none" stroke-linecap="round"/>
    <path d="M5 -160 Q55 -175 60 -145" stroke="#8be36a" stroke-width="8" fill="none" stroke-linecap="round"/>
  </g>

  <!-- Skoop blob riding the rail -->
  <g transform="translate(610 470)">
    <path d="M-60 40 Q-70 -40 0 -50 Q70 -40 60 40Z" fill="#4dd0e1"/>
    <circle cx="-18" cy="-10" r="12" fill="#fff"/><circle cx="-16" cy="-8" r="5" fill="#222"/>
    <circle cx="18" cy="-10" r="12" fill="#fff"/><circle cx="20" cy="-8" r="5" fill="#222"/>
    <ellipse cx="0" cy="15" rx="12" ry="8" fill="#1d6f7a"/>
    <circle cx="-38" cy="45" r="14" fill="#333"/><circle cx="38" cy="45" r="14" fill="#333"/>
    <circle cx="-38" cy="45" r="5" fill="#aaa"/><circle cx="38" cy="45" r="5" fill="#aaa"/>
  </g>

  <!-- Floating bubbles (blooblol glu) -->
  <g fill="none" stroke="#ffffffaa" stroke-width="3">
    <circle cx="520" cy="250" r="14"/><circle cx="545" cy="215" r="9"/>
    <circle cx="560" cy="185" r="6"/><circle cx="280" cy="230" r="11"/>
    <circle cx="300" cy="200" r="7"/>
  </g>
</svg>

The Bloock, the Troupwead, and the Skoop on the Railboobryck Line
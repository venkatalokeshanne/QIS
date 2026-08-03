// Static snapshot of the user's own broker watchlists (Quantum, AI Core,
// AI Beta, Research) -- lets the header's ticker picker select a whole
// category at once instead of typing each symbol in one at a time.
// Edit this list directly if the underlying watchlists change; there's
// no live sync to the broker.
export const WATCHLISTS = [
  {
    name: 'Quantum',
    tickers: ['IONQ', 'RGTI', 'QBTS', 'INFQ', 'QUBT', 'QNT', 'IQMX'],
  },
  {
    name: 'AI Core',
    tickers: [
      'NVDA', 'MSFT', 'TSLA', 'PLTR', 'AMZN', 'AMD', 'GOOG', 'AAPL', 'META',
      'CRWV', 'TSM', 'ORCL', 'DOCU', 'IBM', 'AVGO', 'ADBE', 'MU', 'CHTR',
      'AXON', 'DDOG', 'ACN', 'NOW', 'MDB', 'NFLX', 'CRWD', 'SNOW', 'ARM',
      'ASML', 'BLK', 'INTU', 'PATH', 'DELL', 'INTC', 'GLW', 'SKHY', 'FIG',
    ],
  },
  {
    name: 'AI Beta',
    tickers: [
      'ALAB', 'GRCE', 'LAES', 'YDDL', 'FROG', 'SOUN', 'INOD', 'BBAI', 'AI',
      'NBIS', 'IREN', 'RZLV', 'REKR', 'DVLT', 'ADMA', 'EOSE', 'FIVN', 'QCOM',
      'SNDK', 'CALX', 'WULF', 'APLD', 'GRRR',
    ],
  },
  {
    name: 'Research',
    tickers: ['RDW', 'SPCE', 'CRDO', 'HPE', 'RKLB', 'ASTS', 'SOFI', 'LMND', 'HIMS', 'WQTM', 'SPCX'],
  },
]

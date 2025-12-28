const { randomUUID } = require('crypto');

const roles = ['player', 'admin', 'treasurer'];

const users = [
  {
    id: randomUUID(),
    name: 'Max Mustermann',
    email: 'max@example.com',
    playerNumber: 'P001',
    role: 'admin',
    wallet: 1250.5,
  },
  {
    id: randomUUID(),
    name: 'Mia Musterfrau',
    email: 'mia@example.com',
    playerNumber: 'P002',
    role: 'treasurer',
    wallet: 840.0,
  },
  {
    id: randomUUID(),
    name: 'Alex Beispiel',
    email: 'alex@example.com',
    playerNumber: 'P003',
    role: 'player',
    wallet: 50.0,
  },
];

const finesCatalog = [
  { id: randomUUID(), reason: 'Zu spät gekommen', amount: 5 },
  { id: randomUUID(), reason: 'Trikot vergessen', amount: 3 },
];

const events = [
  {
    id: randomUUID(),
    type: 'training',
    title: 'Wochen­training',
    location: 'Sportplatz Hauptstraße',
    dateTime: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
    requiresResponse: true,
    responses: {},
    lineup: [],
    status: 'planned',
    notes: '',
  },
  {
    id: randomUUID(),
    type: 'match',
    title: 'Liga: FC Stadtmitte vs Verein24',
    location: 'Sportpark Zentrum',
    dateTime: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000).toISOString(),
    requiresResponse: true,
    responses: {},
    lineup: [],
    status: 'planned',
    notes: '',
  },
];

const drinkProducts = [
  { id: randomUUID(), name: 'Wasser 0.5l', price: 1.0, stock: 60 },
  { id: randomUUID(), name: 'Isodrink', price: 2.5, stock: 40 },
  { id: randomUUID(), name: 'Kaffee', price: 1.5, stock: 25 },
];

const drinkBookings = [];

const ledger = [
  {
    id: randomUUID(),
    userId: users[0].id,
    kind: 'balance',
    description: 'Anfangsbestand Vereinskasse',
    amount: 1250.5,
    createdAt: new Date().toISOString(),
  },
];

const liveTicker = {
  current: {
    matchId: randomUUID(),
    home: 'FC Stadtmitte',
    away: 'Verein24',
    status: 'FT',
    score: { home: 1, away: 1 },
    events: [
      { id: randomUUID(), minute: 12, type: 'goal', team: 'home', player: 'Müller', note: 'Elfmeter' },
      { id: randomUUID(), minute: 44, type: 'card_yellow', team: 'away', player: 'Weber', note: 'Foul' },
      { id: randomUUID(), minute: 77, type: 'goal', team: 'away', player: 'Becker', note: 'Kopfball' },
    ],
  },
};
liveTicker[liveTicker.current.matchId] = liveTicker.current;

const subscriptions = [
  {
    id: randomUUID(),
    club: 'Verein24',
    plan: 'premium',
    interval: 'yearly',
    active: true,
    startedAt: new Date().toISOString(),
    seats: 40,
  },
];

function findUserById(id) {
  return users.find((user) => user.id === id);
}

function addLedgerEntry({ userId, kind, description, amount }) {
  const entry = {
    id: randomUUID(),
    userId,
    kind,
    description,
    amount,
    createdAt: new Date().toISOString(),
  };
  ledger.push(entry);
  const user = findUserById(userId);
  if (user) {
    user.wallet = Math.round((user.wallet + amount) * 100) / 100;
  }
  return entry;
}

function recordDrinkBooking({ userId, productId, quantity }) {
  const product = drinkProducts.find((item) => item.id === productId);
  if (!product) return { error: 'Produkt nicht gefunden' };
  if (product.stock < quantity) return { error: 'Nicht genügend Bestand' };
  product.stock -= quantity;
  const booking = {
    id: randomUUID(),
    userId,
    productId,
    quantity,
    total: Math.round(product.price * quantity * 100) / 100,
    bookedAt: new Date().toISOString(),
  };
  drinkBookings.push(booking);
  addLedgerEntry({
    userId,
    kind: 'drink',
    description: `Getränk: ${product.name} x${quantity}`,
    amount: -booking.total,
  });
  return booking;
}

function assignFine({ userId, fineId }) {
  const fineTemplate = finesCatalog.find((fine) => fine.id === fineId);
  if (!fineTemplate) return { error: 'Strafe nicht gefunden' };
  return addLedgerEntry({
    userId,
    kind: 'fine',
    description: `Strafe: ${fineTemplate.reason}`,
    amount: -fineTemplate.amount,
  });
}

function updateLiveTickerEvent(matchId, payload) {
  if (!liveTicker[matchId]) {
    liveTicker[matchId] = {
      matchId,
      home: payload.home || 'Heim',
      away: payload.away || 'Gast',
      status: 'LIVE',
      score: { home: 0, away: 0 },
      events: [],
    };
  }
  const entry = { id: randomUUID(), ...payload };
  liveTicker[matchId].events.push(entry);
  if (payload.type === 'goal') {
    if (payload.team === 'home') liveTicker[matchId].score.home += 1;
    if (payload.team === 'away') liveTicker[matchId].score.away += 1;
  }
  return liveTicker[matchId];
}

function computeStats() {
  const attendance = events.map((event) => {
    const counts = Object.values(event.responses || {}).reduce(
      (acc, response) => {
        acc[response.status] = (acc[response.status] || 0) + 1;
        return acc;
      },
      {}
    );
    return {
      id: event.id,
      title: event.title,
      type: event.type,
      dateTime: event.dateTime,
      responses: counts,
      lineupSize: event.lineup?.length || 0,
    };
  });

  const drinkByPlayer = users.map((user) => {
    const bookings = drinkBookings.filter((booking) => booking.userId === user.id);
    const total = bookings.reduce((sum, booking) => sum + booking.total, 0);
    return {
      userId: user.id,
      name: user.name,
      totalDrinks: bookings.length,
      spend: Math.round(total * 100) / 100,
    };
  });

  const walletRanking = [...users]
    .sort((a, b) => b.wallet - a.wallet)
    .map((user, index) => ({ rank: index + 1, userId: user.id, name: user.name, balance: user.wallet }));

  return { attendance, drinkByPlayer, walletRanking };
}

module.exports = {
  roles,
  users,
  events,
  drinkProducts,
  drinkBookings,
  ledger,
  finesCatalog,
  liveTicker,
  subscriptions,
  recordDrinkBooking,
  assignFine,
  addLedgerEntry,
  updateLiveTickerEvent,
  computeStats,
  findUserById,
};

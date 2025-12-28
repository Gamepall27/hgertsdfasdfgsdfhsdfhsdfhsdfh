const http = require('http');
const { URL } = require('url');
const crypto = require('crypto');
const {
  users,
  events,
  drinkProducts,
  ledger,
  finesCatalog,
  liveTicker,
  subscriptions,
  roles,
  recordDrinkBooking,
  assignFine,
  addLedgerEntry,
  updateLiveTickerEvent,
  computeStats,
  findUserById,
} = require('./data');

const PORT = process.env.PORT || 3000;

function sendJson(res, status, payload) {
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,PATCH,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(JSON.stringify(payload));
}

async function parseBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req
      .on('data', (chunk) => chunks.push(chunk))
      .on('end', () => {
        if (!chunks.length) {
          resolve({});
          return;
        }
        try {
          const body = JSON.parse(Buffer.concat(chunks).toString());
          resolve(body);
        } catch (err) {
          reject(err);
        }
      })
      .on('error', reject);
  });
}

function allowOptions(req, res) {
  if (req.method === 'OPTIONS') {
    sendJson(res, 200, { ok: true });
    return true;
  }
  return false;
}

function route(req, res) {
  if (allowOptions(req, res)) return;

  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;

  if (path === '/api/health' && req.method === 'GET') {
    sendJson(res, 200, { status: 'ok', timestamp: new Date().toISOString() });
    return;
  }

  if (path === '/api/roles' && req.method === 'GET') {
    sendJson(res, 200, { roles });
    return;
  }

  if (path === '/api/users' && req.method === 'GET') {
    sendJson(res, 200, { users });
    return;
  }

  if (path === '/api/users' && req.method === 'POST') {
    return parseBody(req)
      .then((body) => {
        if (!body.name || !body.email || !body.playerNumber) {
          sendJson(res, 400, { error: 'name, email und playerNumber sind Pflichtfelder' });
          return;
        }
        const role = roles.includes(body.role) ? body.role : 'player';
        const user = {
          id: crypto.randomUUID(),
          name: body.name,
          email: body.email,
          playerNumber: body.playerNumber,
          role,
          wallet: body.wallet || 0,
        };
        users.push(user);
        sendJson(res, 201, { user });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path === '/api/auth/login' && req.method === 'POST') {
    return parseBody(req)
      .then((body) => {
        const identifier = body.email || body.playerNumber;
        const user = users.find(
          (entry) => entry.email === identifier || entry.playerNumber === identifier
        );
        if (!user) {
          sendJson(res, 401, { error: 'Nutzer nicht gefunden' });
          return;
        }
        sendJson(res, 200, {
          token: `demo-${user.id}`,
          user,
        });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path.startsWith('/api/users/') && req.method === 'PATCH') {
    const [, , , userId, action] = path.split('/');
    if (action !== 'role') {
      sendJson(res, 404, { error: 'Route nicht gefunden' });
      return;
    }
    return parseBody(req)
      .then((body) => {
        const user = users.find((entry) => entry.id === userId);
        if (!user) {
          sendJson(res, 404, { error: 'Nutzer nicht gefunden' });
          return;
        }
        if (!roles.includes(body.role)) {
          sendJson(res, 400, { error: 'Ungültige Rolle' });
          return;
        }
        user.role = body.role;
        sendJson(res, 200, { user });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path === '/api/events' && req.method === 'GET') {
    sendJson(res, 200, { events });
    return;
  }

  if (path === '/api/events' && req.method === 'POST') {
    return parseBody(req)
      .then((body) => {
        const required = ['type', 'title', 'location', 'dateTime'];
        const missing = required.filter((key) => !body[key]);
        if (missing.length) {
          sendJson(res, 400, { error: `Fehlende Felder: ${missing.join(', ')}` });
          return;
        }
        const event = {
          id: crypto.randomUUID(),
          type: body.type,
          title: body.title,
          location: body.location,
          dateTime: body.dateTime,
          requiresResponse: !!body.requiresResponse,
          responses: {},
          lineup: [],
          status: body.status || 'planned',
          notes: body.notes || '',
        };
        events.push(event);
        sendJson(res, 201, { event });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path.startsWith('/api/events/') && path.endsWith('/rsvp') && req.method === 'POST') {
    const [, , , eventId] = path.split('/');
    return parseBody(req)
      .then((body) => {
        const event = events.find((entry) => entry.id === eventId);
        if (!event) {
          sendJson(res, 404, { error: 'Termin nicht gefunden' });
          return;
        }
        if (!body.userId || !body.status) {
          sendJson(res, 400, { error: 'userId und status sind Pflichtfelder' });
          return;
        }
        event.responses[body.userId] = {
          status: body.status,
          note: body.note || '',
          at: new Date().toISOString(),
        };
        sendJson(res, 200, { event });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path.startsWith('/api/events/') && path.endsWith('/lineup') && req.method === 'POST') {
    const [, , , eventId] = path.split('/');
    return parseBody(req)
      .then((body) => {
        const event = events.find((entry) => entry.id === eventId);
        if (!event) {
          sendJson(res, 404, { error: 'Termin nicht gefunden' });
          return;
        }
        const lineup = Array.isArray(body.lineup) ? body.lineup : [];
        event.lineup = lineup;
        sendJson(res, 200, { event });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path === '/api/drinks' && req.method === 'GET') {
    sendJson(res, 200, { products: drinkProducts });
    return;
  }

  if (path === '/api/drinks' && req.method === 'POST') {
    return parseBody(req)
      .then((body) => {
        if (!body.name || typeof body.price !== 'number') {
          sendJson(res, 400, { error: 'name und price sind Pflichtfelder' });
          return;
        }
        const product = {
          id: crypto.randomUUID(),
          name: body.name,
          price: body.price,
          stock: body.stock ?? 0,
        };
        drinkProducts.push(product);
        sendJson(res, 201, { product });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path.startsWith('/api/drinks/') && path.endsWith('/book') && req.method === 'POST') {
    const [, , , productId] = path.split('/');
    return parseBody(req)
      .then((body) => {
        if (!body.userId || typeof body.quantity !== 'number') {
          sendJson(res, 400, { error: 'userId und quantity sind Pflichtfelder' });
          return;
        }
        const result = recordDrinkBooking({ userId: body.userId, productId, quantity: body.quantity });
        if (result.error) {
          sendJson(res, 400, { error: result.error });
          return;
        }
        sendJson(res, 201, { booking: result });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path === '/api/ledger' && req.method === 'GET') {
    sendJson(res, 200, { ledger });
    return;
  }

  if (path === '/api/ledger' && req.method === 'POST') {
    return parseBody(req)
      .then((body) => {
        const required = ['userId', 'kind', 'description', 'amount'];
        const missing = required.filter((key) => body[key] === undefined);
        if (missing.length) {
          sendJson(res, 400, { error: `Fehlende Felder: ${missing.join(', ')}` });
          return;
        }
        const entry = addLedgerEntry({
          userId: body.userId,
          kind: body.kind,
          description: body.description,
          amount: Number(body.amount),
        });
        sendJson(res, 201, { entry });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path.startsWith('/api/wallet/') && req.method === 'GET') {
    const userId = path.split('/')[3];
    const user = findUserById(userId);
    if (!user) {
      sendJson(res, 404, { error: 'Nutzer nicht gefunden' });
      return;
    }
    const entries = ledger.filter((entry) => entry.userId === userId);
    const balance = user.wallet;
    sendJson(res, 200, { user, balance, entries });
    return;
  }

  if (path === '/api/fines' && req.method === 'GET') {
    sendJson(res, 200, { catalog: finesCatalog });
    return;
  }

  if (path.startsWith('/api/fines/') && req.method === 'POST') {
    const [, , , fineId, action] = path.split('/');
    if (action !== 'assign') {
      sendJson(res, 404, { error: 'Route nicht gefunden' });
      return;
    }
    return parseBody(req)
      .then((body) => {
        if (!body.userId) {
          sendJson(res, 400, { error: 'userId ist erforderlich' });
          return;
        }
        const result = assignFine({ userId: body.userId, fineId });
        if (result.error) {
          sendJson(res, 400, { error: result.error });
          return;
        }
        sendJson(res, 201, { entry: result });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path.startsWith('/api/live/') && req.method === 'GET') {
    const matchId = path.split('/')[3];
    const ticker = liveTicker[matchId] || null;
    if (!ticker) {
      sendJson(res, 404, { error: 'Match nicht gefunden' });
      return;
    }
    sendJson(res, 200, { ticker });
    return;
  }

  if (path.startsWith('/api/live/') && req.method === 'POST') {
    const matchId = path.split('/')[3];
    return parseBody(req)
      .then((body) => {
        const ticker = updateLiveTickerEvent(matchId, body);
        sendJson(res, 201, { ticker });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path === '/api/stats' && req.method === 'GET') {
    sendJson(res, 200, computeStats());
    return;
  }

  if (path === '/api/subscriptions' && req.method === 'GET') {
    sendJson(res, 200, { subscriptions });
    return;
  }

  if (path === '/api/subscriptions' && req.method === 'POST') {
    return parseBody(req)
      .then((body) => {
        const required = ['club', 'plan', 'interval'];
        const missing = required.filter((key) => !body[key]);
        if (missing.length) {
          sendJson(res, 400, { error: `Fehlende Felder: ${missing.join(', ')}` });
          return;
        }
        const subscription = {
          id: crypto.randomUUID(),
          club: body.club,
          plan: body.plan,
          interval: body.interval,
          active: true,
          startedAt: new Date().toISOString(),
          seats: body.seats || 30,
        };
        subscriptions.push(subscription);
        sendJson(res, 201, { subscription });
      })
      .catch(() => sendJson(res, 400, { error: 'Ungültiger Body' }));
  }

  if (path === '/api/dashboard' && req.method === 'GET') {
    const nextEvent = events
      .filter((event) => new Date(event.dateTime) > new Date())
      .sort((a, b) => new Date(a.dateTime) - new Date(b.dateTime))[0];
    const pendingResponses = events.map((event) => ({
      eventId: event.id,
      title: event.title,
      awaiting: users.length - Object.keys(event.responses).length,
    }));

    sendJson(res, 200, {
      nextEvent: nextEvent || null,
      pendingResponses,
      ledgerTotal: ledger.reduce((sum, entry) => sum + entry.amount, 0),
      live: liveTicker.current,
    });
    return;
  }

  sendJson(res, 404, { error: 'Route nicht gefunden' });
}

const server = http.createServer((req, res) => {
  route(req, res);
});

server.listen(PORT, () => {
  console.log(`Vereins-App API läuft auf http://localhost:${PORT}`);
});

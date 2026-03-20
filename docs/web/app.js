const API_BASE = 'https://api.mail.tm';

const dom = {
  generateIdentity: document.getElementById('generate-identity'),
  createAccount: document.getElementById('create-account'),
  login: document.getElementById('login'),
  refresh: document.getElementById('refresh'),
  email: document.getElementById('email'),
  password: document.getElementById('password'),
  togglePassword: document.getElementById('toggle-password'),
  status: document.getElementById('status'),
  messageList: document.getElementById('message-list'),
  msgMeta: document.getElementById('msg-meta'),
  msgBody: document.getElementById('msg-body'),
  idFields: {
    name: document.getElementById('id-name'),
    username: document.getElementById('id-username'),
    gender: document.getElementById('id-gender'),
    address: document.getElementById('id-address'),
    city: document.getElementById('id-city'),
    country: document.getElementById('id-country'),
    zip: document.getElementById('id-zip'),
    phone: document.getElementById('id-phone'),
    birthdate: document.getElementById('id-birthdate'),
    job: document.getElementById('id-job')
  }
};

const state = {
  domains: [],
  token: null,
  messages: [],
  activeMessageId: null
};

function setStatus(text, isError = false) {
  dom.status.textContent = text;
  dom.status.style.background = isError ? '#f5d6d6' : '#efe6d8';
  dom.status.style.color = isError ? '#8b1e1e' : '#3b352d';
}

function getFaker() {
  if (window.faker && window.faker.faker) return window.faker.faker;
  if (window.faker) return window.faker;
  return null;
}

function randomString(length) {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let out = '';
  for (let i = 0; i < length; i += 1) {
    out += chars[Math.floor(Math.random() * chars.length)];
  }
  return out;
}

function randomItem(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function generateIdentity() {
  const faker = getFaker();
  const gender = Math.random() > 0.5 ? 'Male' : 'Female';
  const data = faker
    ? {
        name: faker.person.fullName(),
        username: faker.internet.userName(),
        gender,
        address: faker.location.streetAddress(),
        city: faker.location.city(),
        country: faker.location.country(),
        zip: faker.location.zipCode(),
        phone: faker.phone.number(),
        birthdate: faker.date.birthdate().toISOString().slice(0, 10),
        job: faker.person.jobTitle()
      }
    : (() => {
        const firstNames = ['Alex', 'Jamie', 'Chris', 'Taylor', 'Jordan', 'Morgan', 'Casey', 'Riley'];
        const lastNames = ['Preston', 'Pham', 'Bass', 'Schultz', 'Williams', 'Wolfe', 'Powell', 'Afton'];
        const name = `${randomItem(firstNames)} ${randomItem(lastNames)}`;
        return {
          name,
          username: `${name.toLowerCase().replace(/\s+/g, '')}${Math.floor(Math.random() * 90 + 10)}`,
          gender,
          address: `${Math.floor(Math.random() * 999)} Main St`,
          city: 'Sample City',
          country: 'Sampleland',
          zip: String(10000 + Math.floor(Math.random() * 89999)),
          phone: `+1-${Math.floor(100 + Math.random() * 900)}-${Math.floor(100 + Math.random() * 900)}-${Math.floor(1000 + Math.random() * 9000)}`,
          birthdate: '1990-01-01',
          job: 'Generalist'
        };
      })();

  dom.idFields.name.value = data.name;
  dom.idFields.username.value = data.username;
  dom.idFields.gender.value = data.gender;
  dom.idFields.address.value = data.address;
  dom.idFields.city.value = data.city;
  dom.idFields.country.value = data.country;
  dom.idFields.zip.value = data.zip;
  dom.idFields.phone.value = data.phone;
  dom.idFields.birthdate.value = data.birthdate;
  dom.idFields.job.value = data.job;
}

async function fetchJson(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set('Content-Type', 'application/json');
  if (state.token) headers.set('Authorization', `Bearer ${state.token}`);

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json();
}

async function loadDomains() {
  try {
    const data = await fetchJson('/domains', { method: 'GET' });
    state.domains = data['hydra:member'] || [];
    if (state.domains.length === 0) {
      setStatus('No domains available from mail.tm', true);
      return;
    }
    setStatus(`Domains loaded: ${state.domains.length}`);
  } catch (err) {
    setStatus(`Domain load error. Possible CORS or network issue. ${err.message}`, true);
  }
}

async function createAccount() {
  if (!state.domains.length) {
    setStatus('Domains not loaded yet.', true);
    return;
  }

  const faker = getFaker();
  const username = randomString(12);
  const password = faker ? faker.internet.password({ length: 12 }) : randomString(12);
  const domain = state.domains[0].domain;
  const address = `${username}@${domain}`;

  try {
    await fetchJson('/accounts', {
      method: 'POST',
      body: JSON.stringify({ address, password })
    });
    dom.email.value = address;
    dom.password.value = password;
    setStatus('Account created. You can login now.');
  } catch (err) {
    setStatus(`Create account error: ${err.message}`, true);
  }
}

async function login() {
  const address = dom.email.value.trim();
  const password = dom.password.value.trim();
  if (!address || !password) {
    setStatus('Email and password required.', true);
    return;
  }

  try {
    const data = await fetchJson('/token', {
      method: 'POST',
      body: JSON.stringify({ address, password })
    });
    state.token = data.token;
    setStatus('Logged in.');
  } catch (err) {
    setStatus(`Login error: ${err.message}`, true);
  }
}

function clearMessageView() {
  dom.msgMeta.textContent = '';
  dom.msgBody.textContent = '';
}

function renderMessages() {
  dom.messageList.innerHTML = '';
  clearMessageView();
  state.messages.forEach((msg) => {
    const li = document.createElement('li');
    li.dataset.id = msg.id;
    li.textContent = `${msg.from?.address || 'Unknown'} - ${msg.subject || 'No subject'}`;
    li.addEventListener('click', () => selectMessage(msg.id, li));
    dom.messageList.appendChild(li);
  });
}

function setActiveListItem(target) {
  const items = dom.messageList.querySelectorAll('li');
  items.forEach((item) => item.classList.remove('active'));
  if (target) target.classList.add('active');
}

function extractTextFromHtml(html) {
  if (!html) return '';
  const wrapper = document.createElement('div');
  wrapper.innerHTML = html;
  return wrapper.textContent || '';
}

async function selectMessage(messageId, li) {
  setActiveListItem(li);
  state.activeMessageId = messageId;
  try {
    const message = await fetchJson(`/messages/${messageId}`, { method: 'GET' });
    const from = message.from?.address || 'Unknown sender';
    const subject = message.subject || 'No subject';
    const date = message.createdAt ? new Date(message.createdAt).toLocaleString() : '';
    dom.msgMeta.textContent = `${from} | ${subject} | ${date}`;

    let body = message.text || message.intro || '';
    if (!body && Array.isArray(message.html) && message.html.length) {
      body = extractTextFromHtml(message.html[0]);
    }
    dom.msgBody.textContent = body || 'Empty message.';
  } catch (err) {
    setStatus(`Message load error: ${err.message}`, true);
  }
}

async function refreshInbox() {
  if (!state.token) {
    setStatus('Login required before inbox refresh.', true);
    return;
  }
  try {
    const data = await fetchJson('/messages', { method: 'GET' });
    state.messages = data['hydra:member'] || [];
    renderMessages();
    setStatus(`Inbox loaded: ${state.messages.length} message(s).`);
  } catch (err) {
    setStatus(`Inbox error: ${err.message}`, true);
  }
}

function wireEvents() {
  dom.generateIdentity.addEventListener('click', generateIdentity);
  dom.createAccount.addEventListener('click', createAccount);
  dom.login.addEventListener('click', login);
  dom.refresh.addEventListener('click', refreshInbox);
  dom.togglePassword.addEventListener('click', () => {
    const isHidden = dom.password.type === 'password';
    dom.password.type = isHidden ? 'text' : 'password';
    dom.togglePassword.textContent = isHidden ? 'Hide' : 'Show';
  });
}

wireEvents();
loadDomains();

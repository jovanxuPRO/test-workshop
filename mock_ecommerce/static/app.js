/* Shared frontend utilities */
const API = {
  token: () => localStorage.getItem('token'),
  headers: (hasBody) => {
    const h = hasBody ? {'Content-Type':'application/json'} : {};
    if(API.token()) h['Authorization'] = 'Bearer ' + API.token();
    return h;
  },
  get: async (url) => {
    const r = await fetch(url, {headers: API.headers()});
    if (r.status === 401) { logout(); throw new Error('401'); }
    return r;
  },
  post: async (url, body) => {
    const r = await fetch(url, {method:'POST',headers:API.headers(true),body:JSON.stringify(body)});
    if (r.status === 401) { logout(); throw new Error('401'); }
    return r;
  },
  put: async (url, body) => {
    const r = await fetch(url, {method:'PUT',headers:API.headers(true),body:body?JSON.stringify(body):undefined});
    if (r.status === 401) { logout(); throw new Error('401'); }
    return r;
  },
  del: async (url) => {
    const r = await fetch(url, {method:'DELETE',headers:API.headers()});
    if (r.status === 401) { logout(); throw new Error('401'); }
    return r;
  }
};

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location = '/login';
}

function checkAuth() {
  if (!API.token()) window.location = '/login';
  const u = JSON.parse(localStorage.getItem('user')||'{}');
  if (u.name) document.getElementById('nav-user-name').textContent = u.name + ' (' + u.role + ')';
}

function toast(msg, type='info') {
  const t = document.createElement('div');
  t.className = 'toast';
  t.style.background = type==='success'?'#059669':type==='error'?'#DC2626':'#4F46E5';
  t.style.color = '#fff';
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

function formatMoney(n) { return '¥' + Number(n).toFixed(2); }
function formatDate(s) { return new Date(s).toLocaleDateString('zh-CN'); }
function trunc(s, n) { return (s||'').length > n ? s.slice(0,n)+'...' : s; }

// Active nav link
(function(){
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });
})();

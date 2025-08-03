const API = window.location.origin;

// switch tabs
function showTab(id){
  document.querySelectorAll("main .tab")
    .forEach(s=>s.style.display = s.id===id ? "block" : "none");
  if(id==="users")     loadUsers();
  if(id==="sessions")  loadSessions();
  if(id==="keys")      loadKeys();
}

// fetch helper
async function call(path, opts={}){
  const res = await fetch(API+path, opts);
  if(!res.ok) throw Error(await res.text());
  return res.json();
}

// USERS
async function loadUsers(){
  const data = await call("/admin/users");
  const tb = document.querySelector("#users tbody");
  tb.innerHTML = "";
  data.forEach(u=>{
    tb.innerHTML += `<tr>
      <td>${u.id}</td>
      <td>${u.username}</td>
      <td>${u.is_admin}</td>
      <td>${u.active}</td>
      <td><button onclick="deleteUser(${u.id})">✖️</button></td>
    </tr>`;
  });
}
async function deleteUser(id){
  await call(`/admin/users/${id}`, {method:"DELETE"});
  loadUsers();
}

// SESSIONS
async function loadSessions(){
  const data = await call("/admin/sessions");
  const tb = document.querySelector("#sessions tbody");
  tb.innerHTML = "";
  data.forEach(s=>{
    tb.innerHTML += `<tr>
      <td>${s.id}</td>
      <td>${s.user_id||""}</td>
      <td>${s.ip_address}</td>
      <td>${s.user_agent||""}</td>
      <td>${new Date(s.timestamp).toLocaleString()}</td>
    </tr>`;
  });
}

// KEYS
async function loadKeys(){
  const data = await call("/admin/keys");
  const tb = document.querySelector("#keys tbody");
  tb.innerHTML = "";
  data.forEach(k=>{
    tb.innerHTML += `<tr>
      <td>${k.id}</td>
      <td>${k.user_id}</td>
      <td>${k.key.slice(0,8)}…</td>
      <td>${k.usage_count}</td>
      <td>${k.revoked}</td>
      <td><button onclick="revokeKey('${k.key}')">✖️</button></td>
    </tr>`;
  });
}
async function createKey(e){
  e.preventDefault();
  const uid = document.getElementById("newKeyUser").value;
  await call(`/admin/keys/${uid}`, {method:"POST"});
  loadKeys();
}
async function revokeKey(key){
  await call(`/admin/keys/${key}`, {method:"DELETE"});
  loadKeys();
}

// on first load show users
window.onload = ()=> showTab("users");

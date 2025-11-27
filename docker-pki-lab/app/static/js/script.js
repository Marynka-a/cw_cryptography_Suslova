async function apiRun(action){
  const res = await fetch(`/api/run/${action}`, {method: "POST"});
  return res.json();
}

async function refreshLogs(){
  const res = await fetch('/api/logs');
  const j = await res.json();
  document.getElementById('logBox').textContent = j.log || "(пусто)";
}

async function refreshCerts(){
  const res = await fetch('/api/list_certs');
  const list = await res.json();
  const ul = document.getElementById('certList');
  ul.innerHTML = '';
  if(!list || list.length===0){
    ul.innerHTML = '<li class="list-group-item">Сертифікатів не знайдено</li>';
    return;
  }
  list.forEach(f=>{
    const li = document.createElement('li');
    li.className = 'list-group-item';
    const span = document.createElement('span');
    span.textContent = f;
    const a = document.createElement('a');
    a.href = `/certs/${encodeURIComponent(f)}`;
    a.textContent = 'Завантажити';
    li.appendChild(span);
    li.appendChild(a);
    ul.appendChild(li);
  });
}

document.getElementById('btnRoot').onclick = async ()=>{
  document.getElementById('statusBox').textContent = 'Запуск...';
  const r = await apiRun('create_root');
  await refreshLogs(); await refreshCerts();
  document.getElementById('statusBox').textContent = r.ok ? 'Root CA створено' : 'Помилка';
  alert(r.ok ? 'Root CA створено' : `Помилка: ${r.out}`);
};

document.getElementById('btnInter').onclick = async ()=>{
  document.getElementById('statusBox').textContent = 'Запуск...';
  const r = await apiRun('create_intermediate');
  await refreshLogs(); await refreshCerts();
  document.getElementById('statusBox').textContent = r.ok ? 'Intermediate CA створено' : 'Помилка';
  alert(r.ok ? 'Intermediate CA створено' : `Помилка: ${r.out}`);
};

document.getElementById('btnServer').onclick = async ()=>{
  document.getElementById('statusBox').textContent = 'Запуск...';
  const r = await apiRun('create_server');
  await refreshLogs(); await refreshCerts();
  document.getElementById('statusBox').textContent = r.ok ? 'Server cert створено' : 'Помилка';
  alert(r.ok ? 'Server cert створено' : `Помилка: ${r.out}`);
};

document.getElementById('btnClient').onclick = async ()=>{
  document.getElementById('statusBox').textContent = 'Запуск...';
  const r = await apiRun('create_client');
  await refreshLogs(); await refreshCerts();
  document.getElementById('statusBox').textContent = r.ok ? 'Client cert створено' : 'Помилка';
  alert(r.ok ? 'Client cert створено' : `Помилка: ${r.out}`);
};

document.getElementById('btnRefreshLogs').onclick = refreshLogs;
document.getElementById('btnRefreshCerts').onclick = refreshCerts;

window.onload = async ()=>{
  await refreshLogs();
  await refreshCerts();
};

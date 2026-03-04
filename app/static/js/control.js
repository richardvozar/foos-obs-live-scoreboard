let editing = false;
let editTimer = null;

function markEditing(){
  editing = true;
  if (editTimer) clearTimeout(editTimer);
  editTimer = setTimeout(() => { editing = false; }, 1500);
}

function setValueIfNotEditing(el, value){
  if (!el) return;
  if (editing) return;

  if (el.type === 'checkbox'){
    const v = !!value;
    if (el.checked !== v) el.checked = v;
  } else {
    const v = String(value ?? "");
    if (el.value !== v) el.value = v;
  }
}

async function fetchState(){
  const r = await fetch('/state', {cache:'no-store'});
  return await r.json();
}

async function post(action, data){
  await fetch('/action', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({action, ...(data || {})})
  });
}

function fmt(s){
  return `${s.match.teams.left} ${s.score.sets_left}-${s.score.sets_right} ${s.match.teams.right}  |  Gól: ${s.score.goals_left}-${s.score.goals_right}`;
}

function detail(s){
  const reqL = s.match.required_sets_left;
  const reqR = s.match.required_sets_right;
  const consL = s.match.from_consolation_left ? " (vigasz +1 szett)" : "";
  const consR = s.match.from_consolation_right ? " (vigasz +1 szett)" : "";
  return `Formátum: ${s.match.bo} | Nyerni kell: Bal ${reqL}${consL}, Jobb ${reqR}${consR} | Időkérés: Bal ${s.score.timeouts_left}/2, Jobb ${s.score.timeouts_right}/2`;
}

async function refresh(){
  const s = await fetchState();

  document.getElementById('scoreLine').textContent = fmt(s);
  document.getElementById('detailLine').textContent = detail(s);
  document.getElementById('msgLine').textContent = s.meta.message ? ("Utolsó: " + s.meta.message) : "";

  const bo = document.getElementById('bo');
  const teamUrl = document.getElementById('teamUrl');
  const teamEnabled = document.getElementById('teamEnabled');
  const leftName = document.getElementById('leftName');
  const rightName = document.getElementById('rightName');
  const consLeft = document.getElementById('consLeft');
  const consRight = document.getElementById('consRight');

  setValueIfNotEditing(bo, s.match.bo);
  setValueIfNotEditing(teamUrl, s.match.team_source_url || "");
  setValueIfNotEditing(teamEnabled, s.match.team_source_enabled ? "1" : "0");
  setValueIfNotEditing(leftName, s.match.teams.left);
  setValueIfNotEditing(rightName, s.match.teams.right);

  if (!editing){
    consLeft.checked = !!s.match.from_consolation_left;
    consRight.checked = !!s.match.from_consolation_right;

    consLeft.disabled = !!s.match.from_consolation_right || (s.match.bo === "BO1");
    consRight.disabled = !!s.match.from_consolation_left || (s.match.bo === "BO1");
  }

  const okTs = s.match.team_source_last_ok_ts ? new Date(s.match.team_source_last_ok_ts).toLocaleTimeString() : "—";
  const err = s.match.team_source_last_error ? (" | Hiba: " + s.match.team_source_last_error) : "";
  document.getElementById('apiStatus').textContent =
    `API névforrás: ${s.match.team_source_enabled ? "ON" : "OFF"} | Utolsó OK: ${okTs}${err}`;
}

function wireEditingGuards(){
  const ids = ['bo','teamUrl','teamEnabled','leftName','rightName','consLeft','consRight'];
  for (const id of ids){
    const el = document.getElementById(id);
    if (!el) continue;
    el.addEventListener('focus', markEditing);
    el.addEventListener('input', markEditing);
    el.addEventListener('change', markEditing);
  }
}

function wireButtons(){
  document.getElementById('saveBtn').addEventListener('click', async () => {
    const payload = {
      bo: document.getElementById('bo').value,
      team_source_url: document.getElementById('teamUrl').value || "",
      team_source_enabled: document.getElementById('teamEnabled').value === "1",
      left: document.getElementById('leftName').value || "Bal",
      right: document.getElementById('rightName').value || "Jobb",
      consLeft: document.getElementById('consLeft').checked,
      consRight: document.getElementById('consRight').checked,
    };
    await post('set_settings', payload);
    editing = false; // mentés után engedjük a sync-et
    await refresh();
  });

  document.getElementById('bo').addEventListener('change', async () => {
    const payload = {
      bo: document.getElementById('bo').value,
      team_source_url: document.getElementById('teamUrl').value || "",
      team_source_enabled: document.getElementById('teamEnabled').value === "1",
      left: document.getElementById('leftName').value || "Bal",
      right: document.getElementById('rightName').value || "Jobb",
      consLeft: document.getElementById('consLeft').checked,
      consRight: document.getElementById('consRight').checked,
    };
    await post('set_settings', payload);
    editing = false; // mentés után engedjük a sync-et
    await refresh();
  });

  document.getElementById('teamEnabled').addEventListener('change', async () => {
    const payload = {
      bo: document.getElementById('bo').value,
      team_source_url: document.getElementById('teamUrl').value || "",
      team_source_enabled: document.getElementById('teamEnabled').value === "1",
      left: document.getElementById('leftName').value || "Bal",
      right: document.getElementById('rightName').value || "Jobb",
      consLeft: document.getElementById('consLeft').checked,
      consRight: document.getElementById('consRight').checked,
    };
    await post('set_settings', payload);
    editing = false; // mentés után engedjük a sync-et
    await refresh();
  });

  document.getElementById('swapBtn').addEventListener('click', async () => { await post('swap_sides'); await refresh(); });
  document.getElementById('resetMatchBtn').addEventListener('click', async () => { await post('reset_match'); await refresh(); });

  document.getElementById('goalLeftBtn').addEventListener('click', async () => { await post('goal_left'); await refresh(); });
  document.getElementById('goalRightBtn').addEventListener('click', async () => { await post('goal_right'); await refresh(); });
  document.getElementById('goalLeftMinusBtn').addEventListener('click', async () => { await post('goal_left_minus'); await refresh(); });
  document.getElementById('goalRightMinusBtn').addEventListener('click', async () => { await post('goal_right_minus'); await refresh(); });

  document.getElementById('undoBtn').addEventListener('click', async () => { await post('undo'); await refresh(); });
  document.getElementById('timeoutLeftBtn').addEventListener('click', async () => { await post('timeout_left'); await refresh(); });
  document.getElementById('timeoutRightBtn').addEventListener('click', async () => { await post('timeout_right'); await refresh(); });
  document.getElementById('resetSetBtn').addEventListener('click', async () => { await post('reset_set'); await refresh(); });

  document.getElementById('consLeft').addEventListener('change', async (e) => {
    await post('set_consolation', {side:'left', value: e.target.checked});
    editing = false;
    await refresh();
  });

  document.getElementById('consRight').addEventListener('change', async (e) => {
    await post('set_consolation', {side:'right', value: e.target.checked});
    editing = false;
    await refresh();
  });

  document.addEventListener('keydown', async (e) => {
    if (e.repeat) return;
    const k = e.key.toLowerCase();
    if (k === 'a') { await post('goal_left'); await refresh(); }
    if (k === 'l') { await post('goal_right'); await refresh(); }
    if (k === 'z') { await post('undo'); await refresh(); }
    if (k === 'q') { await post('timeout_left'); await refresh(); }
    if (k === 'w') { await post('timeout_right'); await refresh(); }
    if (k === 'r') { await post('reset_set'); await refresh(); }
    if (k === 's') { await post('swap_sides'); await refresh(); }
  });
}

(async function init(){
  wireEditingGuards();
  wireButtons();
  await refresh();
  setInterval(refresh, 500);
})();
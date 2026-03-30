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

function detail_format(s){
  return `Formátum: ${s.match.bo}`;
}

function detail_sets_to_win(s){
  const reqL = s.match.required_sets_left;
  const reqR = s.match.required_sets_right;
  const consL = s.match.from_consolation_left ? " (vigasz +1 szett)" : "";
  const consR = s.match.from_consolation_right ? " (vigasz +1 szett)" : "";
  return `Győzelemhez szükséges szettek (Bal - Jobb): ${reqL}${consL} - ${reqR}${consR}`;
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

async function refresh(){
  const s = await fetchState();

  // top info
  document.getElementById('detailFormat').textContent = detail_format(s);
  document.getElementById('detailSetsToWin').textContent = detail_sets_to_win(s);
  document.getElementById('msgLine').textContent = s.meta.message ? ("Utolsó: " + s.meta.message) : "";

  // settings fields (guarded)
  setValueIfNotEditing(document.getElementById('bo'), s.match.bo);
  setValueIfNotEditing(document.getElementById('teamUrl'), s.match.team_source_url || "");
  setValueIfNotEditing(document.getElementById('teamEnabled'), s.match.team_source_enabled ? "1" : "0");
  setValueIfNotEditing(document.getElementById('leftName'), s.match.teams.left);
  setValueIfNotEditing(document.getElementById('rightName'), s.match.teams.right);

  // consolation toggles
  const consLeft = document.getElementById('consLeft');
  const consRight = document.getElementById('consRight');
  if (!editing){
    consLeft.checked = !!s.match.from_consolation_left;
    consRight.checked = !!s.match.from_consolation_right;
    consLeft.disabled = !!s.match.from_consolation_right || (s.match.bo === "BO1");
    consRight.disabled = !!s.match.from_consolation_left || (s.match.bo === "BO1");
  }

  // API status line
  const okTs = s.match.team_source_last_ok_ts ? new Date(s.match.team_source_last_ok_ts).toLocaleTimeString() : "—";
  const err = s.match.team_source_last_error ? (" | Hiba: " + s.match.team_source_last_error) : "";
  document.getElementById('apiStatus').textContent =
    `API névforrás: ${s.match.team_source_enabled ? "ON" : "OFF"} | Utolsó OK: ${okTs}${err}`;

  // left column
  document.getElementById('leftTitle').textContent = s.match.teams.left;
  document.getElementById('leftSets').textContent = String(s.score.sets_left);
  document.getElementById('leftGoals').textContent = String(s.score.goals_left);
  document.getElementById('leftTO').textContent = String(s.score.timeouts_left);
  document.getElementById('leftMeta').textContent =
    `Nyerni kell: ${s.match.required_sets_left} | BO: ${s.match.bo}`;

  // right column
  document.getElementById('rightTitle').textContent = s.match.teams.right;
  document.getElementById('rightSets').textContent = String(s.score.sets_right);
  document.getElementById('rightGoals').textContent = String(s.score.goals_right);
  document.getElementById('rightTO').textContent = String(s.score.timeouts_right);
  document.getElementById('rightMeta').textContent =
    `Nyerni kell: ${s.match.required_sets_right} | BO: ${s.match.bo}`;
}

function wireButtons(){
  // settings top actions
  document.getElementById('swapBtnTop').addEventListener('click', async () => { await post('swap_sides'); await refresh(); });
  document.getElementById('resetMatchBtnTop').addEventListener('click', async () => { await post('reset_match'); await refresh(); });

  // game format
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

  // API team name update
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

  // save settings
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
    editing = false;
    await refresh();
  });

  // top quick actions
  document.getElementById('undoBtnTop').addEventListener('click', async () => { await post('undo'); await refresh(); });
  document.getElementById('resetSetBtnTop').addEventListener('click', async () => { await post('reset_set'); await refresh(); });

  // left team buttons
  document.getElementById('goalLeftBtn').addEventListener('click', async () => { await post('goal_left'); await refresh(); });
  document.getElementById('timeoutLeftBtn').addEventListener('click', async () => { await post('timeout_left'); await refresh(); });
  document.getElementById('goalLeftMinusBtn').addEventListener('click', async () => { await post('goal_left_minus'); await refresh(); });

  // right team buttons
  document.getElementById('goalRightBtn').addEventListener('click', async () => { await post('goal_right'); await refresh(); });
  document.getElementById('timeoutRightBtn').addEventListener('click', async () => { await post('timeout_right'); await refresh(); });
  document.getElementById('goalRightMinusBtn').addEventListener('click', async () => { await post('goal_right_minus'); await refresh(); });

  // mutual exclusion checkboxes (immediate)
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

  // custom functions
  document.getElementById('fn1').addEventListener('click', async () => { await post('button_function_1'); });
  document.getElementById('fn2').addEventListener('click', async () => { await post('button_function_2'); });
  document.getElementById('fn3').addEventListener('click', async () => { await post('button_function_3'); });
  document.getElementById('fn4').addEventListener('click', async () => { await post('button_function_4'); });
  document.getElementById('fn5').addEventListener('click', async () => { await post('button_function_5'); });
  document.getElementById('fn6').addEventListener('click', async () => { await post('button_function_6'); });
  document.getElementById('fn7').addEventListener('click', async () => { await post('button_function_7'); });
  document.getElementById('fn8').addEventListener('click', async () => { await post('button_function_8'); });
  document.getElementById('fn9').addEventListener('click', async () => { await post('button_function_9'); });
  document.getElementById('fn10').addEventListener('click', async () => { await post('button_function_10'); });
  document.getElementById('fn11').addEventListener('click', async () => { await post('button_function_11'); });
  document.getElementById('fn12').addEventListener('click', async () => { await post('button_function_12'); });
  document.getElementById('fn13').addEventListener('click', async () => { await post('button_function_13'); });
  document.getElementById('fn14').addEventListener('click', async () => { await post('button_function_14'); });
  document.getElementById('fn15').addEventListener('click', async () => { await post('button_function_15'); });

  // hotkeys
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
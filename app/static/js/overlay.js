async function pull(){
  const r = await fetch('/state', {cache:'no-store'});
  const s = await r.json();

  document.getElementById('ln').textContent = s.match.teams.left;
  document.getElementById('rn').textContent = s.match.teams.right;

  document.getElementById('sets').textContent = `${s.score.sets_left} - ${s.score.sets_right}`;
  document.getElementById('goals').textContent = `${s.score.goals_left} - ${s.score.goals_right}`;

  document.getElementById('lt').textContent = `Időkérés: ${s.score.timeouts_left}`;
  document.getElementById('rt').textContent = `Időkérés: ${s.score.timeouts_right}`;

  document.getElementById('bo').textContent = s.match.bo;
  document.getElementById('req').textContent = `Nyerni: ${s.match.required_sets_left} / ${s.match.required_sets_right}`;

  document.getElementById('msg').textContent = s.meta.message || '';
}

pull();
setInterval(pull, 300);
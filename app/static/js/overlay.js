let prev = null;

async function pull() {
  const r = await fetch('/state', { cache: 'no-store' });
  const s = await r.json();

  // Fejléc frissítése
  document.getElementById("match-header").textContent = `${s.match.category} - ${s.match.stage}`;

  // LIVE SCORE KAPCSOLÓ KEZELÉSE (ÚJ)
  const isLiveScore = s.match.live_score !== false;
  const overlayEl = document.querySelector(".overlay");
  if (overlayEl) {
    overlayEl.classList.toggle("no-score", !isLiveScore);
  }

  // Nézzük meg a gólállást a váltáshoz
  toggleSets(s.score.goals_left, s.score.goals_right);

  // Csapatok frissítése
  updateTeam("left", s, prev);
  updateTeam("right", s, prev);

  prev = s;
}

function toggleSets(goalsLeft, goalsRight) {
  const isZeroZero = goalsLeft === 0 && goalsRight === 0;

  const sgLeft = document.getElementById("sets-goals-left");
  const sgRight = document.getElementById("sets-goals-right");

  if (sgLeft && sgRight) {
    sgLeft.classList.toggle("visible", isZeroZero);
    sgRight.classList.toggle("visible", isZeroZero);
  }
}

function arraysEqual(a, b) {
  if (!a || !b) return false;
  if (a.length !== b.length) return false;
  return a.every((v, i) => v === b[i]);
}

function updateTeam(side, s, prev) {
  const name = s.match.teams[side];
  const score = s.score[`goals_${side}`];
  const sets = s.score[`sets_${side}`];
  const sets_history = s.score[`sets_history_${side}`];
  const timeouts = s.score[`timeouts_${side}`];

  // Csapatnév beállítása
  document.getElementById(side === "left" ? "ln" : "rn").textContent = name;

  // GÓLOK + Villanás animáció
  const scoreEl = document.getElementById(`score-${side}`);
  const prevScore = prev ? prev.score[`goals_${side}`] : null;

  if (prevScore !== null && score !== prevScore) {
    scoreEl.classList.add("pop");
    setTimeout(() => scoreEl.classList.remove("pop"), 150);
  }
  scoreEl.textContent = score;

  // SZETTEK SZÁMA
  document.getElementById(`sets-${side}`).textContent = sets;

  // KIS DOBOZOK GENERÁLÁSA (SZETT TÖRTÉNET)
  const setsGoalsEl = document.getElementById(`sets-goals-${side}`);
  const prevSets = prev ? prev.score[`sets_history_${side}`] : [];

  if (setsGoalsEl && !arraysEqual(sets_history, prevSets)) {
    setsGoalsEl.innerHTML = "";

    sets_history.slice(-6).forEach((setScore, i) => {
      const el = document.createElement("div");
      el.className = "set-box";
      el.textContent = setScore;
      setsGoalsEl.appendChild(el);

      // Kis késleltetéssel indítjuk a becsúszást, hogy elegáns legyen
      setTimeout(() => el.classList.add("visible"), i * 50);
    });
  }

  // IDŐKÉRÉSEK (TIMEOUTS) pöttyök frissítése
  const toEl = document.getElementById(`to-${side}`);
  if (toEl) {
    toEl.innerHTML = "";
    for (let i = 0; i < 2; i++) {
      const el = document.createElement("div");
      el.className = `to ${i < timeouts ? 'used' : ''}`;
      toEl.appendChild(el);
    }
  }
}

// Indítás
pull();
setInterval(pull, 300);
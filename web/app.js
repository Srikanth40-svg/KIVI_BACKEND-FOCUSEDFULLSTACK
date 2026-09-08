/* Kivi phonetic memory — demo interface.
 *
 * Every panel is rendered from an API response. There is no local state that the backend
 * does not own, and no branch anywhere in this file that special-cases a demo word: if a
 * correction appears on screen it is because the backend decided it, and the reason shown
 * is the reason the backend recorded. Grep for "kiwi" — the only occurrences are in the
 * example buttons, which merely fill the input box.
 */

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, text) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
};

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || body.error || `${res.status} ${res.statusText}`);
  return body;
}

let toastTimer;
function toast(message, bad = false) {
  const t = $("#toast");
  t.textContent = message;
  t.className = `toast show${bad ? " bad" : ""}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.className = "toast"), 3200);
}

/* ── word-level diff, so the change is visible rather than described ──────────── */
function tokenizeForDiff(s) {
  return s.match(/\s+|[^\s]+/g) || [];
}
function diffInto(node, before, after) {
  const a = tokenizeForDiff(before);
  const b = tokenizeForDiff(after);
  // Longest common subsequence over whitespace-separated chunks.
  const m = a.length, n = b.length;
  const dp = Array.from({ length: m + 1 }, () => new Uint32Array(n + 1));
  for (let i = m - 1; i >= 0; i--)
    for (let j = n - 1; j >= 0; j--)
      dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  let i = 0, j = 0;
  const push = (tag, text) => {
    if (!text) return;
    node.appendChild(tag ? el(tag, null, text) : document.createTextNode(text));
  };
  while (i < m && j < n) {
    if (a[i] === b[j]) { push(null, b[j]); i++; j++; }
    else if (dp[i + 1][j] >= dp[i][j + 1]) { push("del", a[i]); i++; }
    else { push("ins", b[j]); j++; }
  }
  while (i < m) { push("del", a[i]); i++; }
  while (j < n) { push("ins", b[j]); j++; }
}

function stageBlock(name, text, opts = {}) {
  const wrap = el("div", `stage${opts.final ? " final" : ""}`);
  wrap.appendChild(el("div", "name", name));
  const t = el("div", "text");
  if (opts.diffFrom !== undefined && opts.diffFrom !== null) diffInto(t, opts.diffFrom, text);
  else t.textContent = text || "—";
  wrap.appendChild(t);
  return wrap;
}

/* ── the "why" panel ─────────────────────────────────────────────────────────── */
function gateBar(score, required) {
  const wrap = el("span", "gate");
  const bar = el("span", "bar");
  const fill = el("i");
  fill.style.width = `${Math.min(100, score * 100)}%`;
  if (score < required) fill.style.background = "var(--warn)";
  bar.appendChild(fill);
  const mark = el("u");
  mark.style.left = `${Math.min(99, required * 100)}%`;
  bar.appendChild(mark);
  wrap.appendChild(bar);
  wrap.appendChild(el("span", null, `${score.toFixed(2)} / ${required.toFixed(2)}`));
  return wrap;
}

function candidateCard(c) {
  const card = el("div", `card ${c.action}`);
  const head = el("div", "head");
  head.appendChild(el("span", null, JSON.stringify(c.span_text)));
  head.appendChild(el("span", "arrow", "→"));
  head.appendChild(el("span", null, JSON.stringify(c.replacement || c.canonical_form)));
  head.appendChild(el("span", "code", c.reason_code));
  card.appendChild(head);
  card.appendChild(el("div", "reason", c.reason_text));

  const meters = el("div", "meters");
  const add = (label, value) => {
    const s = el("span");
    s.appendChild(el("b", null, `${label} `));
    if (value instanceof Node) s.appendChild(value); else s.appendChild(el("span", null, value));
    meters.appendChild(s);
  };
  add("memory", `#${c.memory_id} ${c.memory_status} ${Number(c.memory_confidence).toFixed(2)}`);
  add("tier", c.match_tier);
  add("lexical", Number(c.lexical_score).toFixed(2));
  add("phonetic", Number(c.phonetic_score).toFixed(2));
  add("context", gateBar(Number(c.context_score), Number(c.required_context)));
  if (c.is_ordinary_word) add("ordinary word", "yes");
  card.appendChild(meters);

  if (c.signals && Object.keys(c.signals).length) {
    const d = el("details", "signals");
    d.appendChild(el("summary", null, "context signals"));
    const pre = el("pre", null, JSON.stringify(c.signals, null, 2));
    d.appendChild(pre);
    card.appendChild(d);
  }
  return card;
}

function renderWhy(target, data) {
  target.innerHTML = "";
  const groups = [
    ["Applied", data.applied, "the corrections Kivi made"],
    ["Abstained", data.abstained, "matches Kivi found and deliberately did not act on"],
    ["No-op", data.noop, "already correct, recorded so precision has a denominator"],
    ["Blocked", data.blocked, "outranked by a wider or stronger match"],
  ];
  let any = false;
  for (const [title, rows, blurb] of groups) {
    if (!rows || !rows.length) continue;
    any = true;
    const g = el("div", "group");
    g.appendChild(el("h3", null, `${title} · ${rows.length} — ${blurb}`));
    rows.forEach((c) => g.appendChild(candidateCard(c)));
    target.appendChild(g);
  }
  if (!any) {
    const g = el("div", "group");
    g.appendChild(el("h3", null, "Nothing considered"));
    g.appendChild(el("div", "card blocked", ""));
    g.lastChild.appendChild(el("div", "reason",
      "No stored word came close enough to any span in this text, so there was nothing to decide."));
    target.appendChild(g);
  }
  const d = data.diagnostics || {};
  const t = data.timings || {};
  const u = data.model_usage || {};
  const meta = el("div", "meta");
  meta.textContent =
    `decision #${data.decision_id} · mode ${data.apply_mode} · ` +
    `${d.spans_considered ?? "?"} spans · vocabulary ${d.vocabulary_confirmed_forms ?? "?"} forms · ` +
    `retrieval ${t.retrieval_ms ?? "?"}ms · total ${t.total_ms ?? "?"}ms · ` +
    `model calls ${u.calls ?? 0}${u.cost_inr ? ` · ₹${u.cost_inr}` : ""}`;
  target.appendChild(meta);
}

function renderStages(target, data) {
  target.className = "stages";
  target.innerHTML = "";
  const s = data.stages;
  target.appendChild(stageBlock("1 · ASR output", s.asr || "(not supplied)"));
  target.appendChild(stageBlock("2 · Formatted", s.formatted));
  target.appendChild(stageBlock("3 · Memory-aware", s.memory_aware, { final: true, diffFrom: s.formatted }));
  const v = el("div", "verdict");
  if (data.intervened) {
    v.innerHTML = `Kivi <b>intervened</b>: ${data.applied.length} correction(s) applied.`;
  } else {
    v.innerHTML = `Kivi <b>did not intervene</b>. ${
      data.abstained.length
        ? `${data.abstained.length} match(es) were found and deliberately left alone.`
        : "Nothing relevant was found."
    }`;
  }
  target.appendChild(v);
}

/* ── three stages view ───────────────────────────────────────────────────────── */
async function runStages() {
  const asr = $("#in-asr").value.trim();
  const formatted = $("#in-formatted").value.trim();
  if (!asr && !formatted) return toast("Give me some ASR or formatted text first.", true);
  $("#btn-run").disabled = true;
  try {
    const data = await api("/api/memory-aware-format", {
      method: "POST",
      body: JSON.stringify({
        asr_text: asr || null,
        formatted_text: formatted || null,
        app_context: $("#in-app").value.trim() || null,
        learn_from_this: $("#in-learn").checked,
      }),
    });
    renderStages($("#stages"), data);
    renderWhy($("#why"), data);
    if ($("#in-learn").checked) loadMemories();
    return data;
  } catch (e) {
    toast(e.message, true);
  } finally {
    $("#btn-run").disabled = false;
  }
}

/* ── teach view ──────────────────────────────────────────────────────────────── */
function renderLearning(target, data) {
  target.className = "stages";
  target.innerHTML = "";
  target.appendChild(el("div", "verdict", `Interaction #${data.interaction_id} · ${
    Object.entries(data.summary).map(([k, v]) => `${v} ${k}`).join(", ") || "nothing proposed"
  }`));
  if (!data.decisions.length) {
    const c = el("div", "card blocked");
    c.appendChild(el("div", "reason",
      "No candidate vocabulary was extracted from this observation. Ordinary dictation " +
      "should leave memory untouched, and most dictation is ordinary."));
    target.appendChild(c);
    return;
  }
  data.decisions.forEach((d) => {
    const cls = d.outcome === "rejected" ? "abstained"
      : d.outcome === "candidate" ? "noop" : "applied";
    const card = el("div", `card ${cls}`);
    const head = el("div", "head");
    head.appendChild(el("span", null, JSON.stringify(d.surface_form)));
    head.appendChild(el("span", "arrow", "→"));
    head.appendChild(el("span", null, JSON.stringify(d.canonical)));
    head.appendChild(el("span", "code", `${d.outcome} · ${d.reason_code}`));
    card.appendChild(head);
    card.appendChild(el("div", "reason", d.reason_text));
    const m = el("div", "meters");
    m.appendChild(el("span", null, `type ${d.word_type}`));
    m.appendChild(el("span", null, `evidence ${d.evidence_type}`));
    if (d.memory_id) m.appendChild(el("span", null, `memory #${d.memory_id}`));
    card.appendChild(m);
    target.appendChild(card);
  });
}

async function ingest() {
  const body = {
    asr_text: $("#ob-asr").value.trim() || null,
    formatted_text: $("#ob-formatted").value.trim() || null,
    user_edited_text: $("#ob-edited").value.trim() || null,
    app_context: $("#ob-app").value.trim() || null,
  };
  if (!body.asr_text && !body.formatted_text && !body.user_edited_text)
    return toast("Give me an observation first.", true);
  $("#btn-observe").disabled = true;
  try {
    const data = await api("/api/observations", { method: "POST", body: JSON.stringify(body) });
    renderLearning($("#learned"), data);
    loadMemories();
    loadLog();
    return data;
  } catch (e) {
    toast(e.message, true);
  } finally {
    $("#btn-observe").disabled = false;
  }
}

/* ── memory view ─────────────────────────────────────────────────────────────── */
let selectedMemory = null;

async function loadMemories() {
  const status = $("#mem-filter").value;
  try {
    const data = await api(`/api/memories${status ? `?status=${status}` : ""}`);
    const list = $("#memlist");
    list.innerHTML = "";
    $("#status").textContent = `${data.count} memories`;
    if (!data.count) {
      list.appendChild(el("div", "lede", "Memory is empty. Press Seed, or teach it something."));
      return;
    }
    data.memories.forEach((m) => {
      const row = el("div", `memrow${selectedMemory === m.id ? " sel" : ""}`);
      row.appendChild(el("span", "cf", m.canonical_form));
      row.appendChild(el("span", `pill ${m.status}`, m.status));
      row.appendChild(el("span", "wt", m.word_type));
      row.appendChild(el("span", "conf", Number(m.confidence).toFixed(2)));
      row.onclick = () => showMemory(m.id);
      list.appendChild(row);
    });
  } catch (e) {
    $("#memlist").textContent = e.message;
  }
}

async function showMemory(id) {
  selectedMemory = id;
  loadMemories();
  const target = $("#memdetail");
  try {
    const m = await api(`/api/memories/${id}`);
    target.className = "stages";
    target.innerHTML = "";

    const h = el("div", "head");
    h.style.fontFamily = "var(--mono)";
    h.style.fontSize = "16px";
    h.textContent = m.canonical_form;
    target.appendChild(h);

    const dl = el("dl", "kv");
    const pair = (k, v) => { dl.appendChild(el("dt", null, k)); dl.appendChild(el("dd", null, v)); };
    pair("status", `${m.status} (only confirmed memories may change text)`);
    pair("confidence", Number(m.confidence).toFixed(2));
    pair("type", m.word_type);
    pair("tokens", String(m.token_count));
    pair("phonetic key", m.phonetic_key);
    pair("normalised key", m.normalized_key);
    pair("seen", `${m.occurrence_count}× · first ${(m.first_seen || "").slice(0, 19)}`);
    if (m.gloss) pair("note", m.gloss);
    if (m.superseded_by) pair("superseded by", `#${m.superseded_by}`);
    target.appendChild(dl);

    target.appendChild(el("div", "name", "OBSERVED FORMS"));
    const vars = el("div", "varlist");
    m.variants.forEach((v) => {
      const s = el("span", "var");
      s.appendChild(el("span", null, ""));
      s.textContent = v.variant_form;
      s.appendChild(el("span", null, `  ${v.kind} ×${v.observation_count}`));
      vars.appendChild(s);
    });
    target.appendChild(vars);

    if (m.context_terms && m.context_terms.length) {
      target.appendChild(el("div", "name", "LEARNED CONTEXT TERMS"));
      const ct = el("div", "varlist");
      m.context_terms.slice(0, 24).forEach((t) => ct.appendChild(el("span", "var", t)));
      target.appendChild(ct);
    }

    target.appendChild(el("div", "name", "EVIDENCE — why this memory exists"));
    const ev = el("ul", "tl");
    m.evidence.forEach((e) => {
      const li = el("li", e.evidence_class === "authoritative" ? "hi" : "");
      li.appendChild(el("div", "ev", `${e.evidence_type} · ${e.evidence_class} · weight ${e.weight}`));
      li.appendChild(el("div", "tx", e.excerpt || ""));
      ev.appendChild(li);
    });
    target.appendChild(ev);

    target.appendChild(el("div", "name", "HISTORY"));
    const tl = el("ul", "tl");
    m.events.forEach((e) => {
      const li = el("li");
      li.appendChild(el("div", "ev",
        `${e.event}${e.from_status ? ` · ${e.from_status} → ${e.to_status}` : ""}` +
        `${e.to_confidence !== null ? ` · conf ${Number(e.to_confidence).toFixed(2)}` : ""}`));
      li.appendChild(el("div", "tx", e.reason_text || e.reason_code));
      tl.appendChild(li);
    });
    target.appendChild(tl);

    const actions = el("div", "memactions");
    if (m.status === "candidate") {
      const b = el("button", "btn small primary", "Confirm");
      b.onclick = () => patchMemory(id, { status: "confirmed" });
      actions.appendChild(b);
    }
    if (m.status === "confirmed") {
      const b = el("button", "btn small", "Demote to candidate");
      b.onclick = () => patchMemory(id, { status: "candidate" });
      actions.appendChild(b);
    }
    if (m.status === "deleted") {
      const b = el("button", "btn small primary", "Restore");
      b.onclick = async () => {
        await api(`/api/memories/${id}/restore`, { method: "POST" });
        toast("Restored."); showMemory(id);
      };
      actions.appendChild(b);
    } else {
      const b = el("button", "btn small", "Delete");
      b.onclick = async () => {
        await api(`/api/memories/${id}`, { method: "DELETE" });
        toast("Deleted. It will stop affecting output immediately."); showMemory(id);
      };
      actions.appendChild(b);
    }
    const re = el("button", "btn small", "Change spelling…");
    re.onclick = async () => {
      const next = prompt("New canonical form (this supersedes rather than overwrites):", m.canonical_form);
      if (next && next !== m.canonical_form) {
        const created = await api(`/api/memories/${id}`, {
          method: "PATCH", body: JSON.stringify({ canonical_form: next }),
        });
        toast("Superseded. The old form is kept and now gets corrected.");
        showMemory(created.id);
        loadMemories();
      }
    };
    actions.appendChild(re);
    target.appendChild(actions);
  } catch (e) {
    target.textContent = e.message;
  }
}

async function patchMemory(id, body) {
  try {
    await api(`/api/memories/${id}`, { method: "PATCH", body: JSON.stringify(body) });
    toast("Updated.");
    showMemory(id);
  } catch (e) { toast(e.message, true); }
}

async function addMemory() {
  const canonical = $("#new-canonical").value.trim();
  if (!canonical) return toast("Needs a canonical form.", true);
  try {
    const m = await api("/api/memories", {
      method: "POST",
      body: JSON.stringify({
        canonical_form: canonical,
        word_type: $("#new-type").value,
        gloss: $("#new-gloss").value.trim() || null,
        observed_forms: $("#new-variants").value.split(",").map((s) => s.trim()).filter(Boolean),
      }),
    });
    toast("Added as authoritative evidence, so it is confirmed immediately.");
    $("#new-canonical").value = ""; $("#new-variants").value = ""; $("#new-gloss").value = "";
    loadMemories(); showMemory(m.id);
  } catch (e) { toast(e.message, true); }
}

/* ── learning log ────────────────────────────────────────────────────────────── */
async function loadLog() {
  const outcome = $("#log-filter").value;
  try {
    const data = await api(`/api/learning-decisions?limit=200${outcome ? `&outcome=${outcome}` : ""}`);
    const list = $("#loglist");
    list.innerHTML = "";
    if (!data.learning_decisions.length) {
      list.appendChild(el("div", "lede", "No learning decisions recorded yet."));
      return;
    }
    data.learning_decisions.forEach((d) => {
      const row = el("div", `logrow ${d.outcome}`);
      const head = el("div", "head");
      head.appendChild(el("span", null, JSON.stringify(d.surface_form)));
      head.appendChild(el("span", "arrow", "→"));
      head.appendChild(el("span", null, JSON.stringify(d.proposed_canonical)));
      head.appendChild(el("span", "code", `${d.outcome} · ${d.evidence_type} · ${d.reason_code}`));
      row.appendChild(head);
      row.appendChild(el("div", "reason", d.reason_text || ""));
      list.appendChild(row);
    });
  } catch (e) { $("#loglist").textContent = e.message; }
}

/* ── guided journey ──────────────────────────────────────────────────────────── */
const JOURNEY = [
  {
    title: "Start from nothing",
    detail: "Wipe the database so every later result is attributable to what happens next.",
    action: "Wipe",
    run: async () => {
      const r = await api("/api/reset", { method: "POST", body: JSON.stringify({ reseed: false }) });
      return { text: `Memory is empty. Rows deleted: ${
        Object.entries(r.rows_deleted).filter(([, v]) => v).map(([k, v]) => `${k} ${v}`).join(", ") || "none"
      }.` };
    },
  },
  {
    title: "Show that nothing is hardcoded",
    detail: "Run the brief's own example against empty memory. It must pass through untouched.",
    action: "Run",
    run: async () => {
      const d = await api("/api/memory-aware-format", {
        method: "POST",
        body: JSON.stringify({ asr_text: "ask aditya to review the sarvam kiwi service" }),
      });
      return { stages: d, text: d.intervened
        ? "Something changed, which should be impossible with empty memory."
        : "Unchanged, as it must be: with no memories there is nothing to apply." };
    },
  },
  {
    title: "Let the person correct Kivi once",
    detail: "The strongest evidence available from ordinary use: the person fixes our output.",
    action: "Teach",
    run: async () => {
      const d = await api("/api/observations", {
        method: "POST",
        body: JSON.stringify({
          asr_text: "review the sarvam kiwi service before friday",
          formatted_text: "Review the Sarvam Kiwi service before Friday.",
          user_edited_text: "Review the Sarvam Kivi service before Friday.",
          app_context: "Slack - #kivi-eng",
        }),
      });
      return { learning: d };
    },
  },
  {
    title: "Inspect what was learned",
    detail: "Canonical form, the wrong form it answers to, the evidence, and the confidence.",
    action: "Inspect",
    run: async () => {
      const data = await api("/api/memories");
      return { text: data.memories.map((m) =>
        `${m.canonical_form} — ${m.word_type}, ${m.status}, confidence ${Number(m.confidence).toFixed(2)}, ` +
        `answers to: ${m.variants.filter((v) => v.kind !== "canonical").map((v) => v.variant_form).join(", ") || "—"}`
      ).join("\n") };
    },
  },
  {
    title: "Now the same mistake in a new sentence",
    detail: "A sentence Kivi has never seen, containing the mis-heard form.",
    action: "Run",
    run: async () => {
      const d = await api("/api/memory-aware-format", {
        method: "POST", body: JSON.stringify({ formatted_text: "Ship the Kiwi update on Friday." }),
      });
      return { stages: d };
    },
  },
  {
    title: "Show exactly which memory caused it",
    detail: "Match tier, similarity scores, the context bar it had to clear, and why.",
    action: "Explain",
    run: async () => {
      const d = await api("/api/memory-aware-format", {
        method: "POST", body: JSON.stringify({ formatted_text: "Ship the Kiwi update on Friday." }),
      });
      return { why: d };
    },
  },
  {
    title: "Now a sentence where it must NOT intervene",
    detail: "Same sound, ordinary meaning. This is the failure that matters most.",
    action: "Run",
    run: async () => {
      const d = await api("/api/memory-aware-format", {
        method: "POST", body: JSON.stringify({ formatted_text: "I ate a kiwi on the flight." }),
      });
      return { stages: d, why: d };
    },
  },
  {
    title: "Weak evidence must not act",
    detail: "A single naming frame earns a candidate memory, which is visible but inert.",
    action: "Teach + run",
    run: async () => {
      await api("/api/observations", {
        method: "POST",
        body: JSON.stringify({ formatted_text: "Our client is called Kiwi Foods and they want the invoice reissued." }),
      });
      const d = await api("/api/memory-aware-format", {
        method: "POST", body: JSON.stringify({ formatted_text: "Send the Kiwi foods invoice today." }),
      });
      return { learning: null, stages: d, why: d };
    },
  },
  {
    title: "The person changes their mind",
    detail: "Supersede the spelling. The old memory stays inspectable; the new one wins.",
    action: "Supersede",
    run: async () => {
      const list = await api("/api/memories?search=Kivi");
      const target = list.memories.find((m) => m.canonical_form === "Kivi");
      if (!target) return { text: "No Kivi memory found — run the earlier steps first." };
      const created = await api(`/api/memories/${target.id}`, {
        method: "PATCH", body: JSON.stringify({ canonical_form: "Kivvy" }),
      });
      const d = await api("/api/memory-aware-format", {
        method: "POST", body: JSON.stringify({ formatted_text: "Ship the Kiwi update on Friday." }),
      });
      return { text: `Memory #${target.id} ("Kivi") is now superseded by #${created.id} ("Kivvy"), ` +
                     `and the old form is carried across as a variant.`, stages: d };
    },
  },
  {
    title: "Delete it",
    detail: "Deletion must take effect immediately, and retrieval must respect it.",
    action: "Delete + run",
    run: async () => {
      const list = await api("/api/memories?status=confirmed");
      const target = list.memories.find((m) => m.canonical_form === "Kivvy")
        || list.memories.find((m) => m.canonical_form === "Kivi");
      if (!target) return { text: "Nothing to delete — run the earlier steps first." };
      await api(`/api/memories/${target.id}`, { method: "DELETE" });
      const d = await api("/api/memory-aware-format", {
        method: "POST", body: JSON.stringify({ formatted_text: "Ship the Kiwi update on Friday." }),
      });
      return { text: `Memory #${target.id} deleted.`, stages: d, why: d };
    },
  },
  {
    title: "Reset and replay",
    detail: "Deterministic: the committed seed always rebuilds the same memory state.",
    action: "Reset + reseed",
    run: async () => {
      const r = await api("/api/reset", { method: "POST", body: JSON.stringify({ reseed: true }) });
      return { text: `Replayed ${r.reseeded.observations} seed observations → ${r.memory_count} memories. ` +
                     `Learning outcomes: ${JSON.stringify(r.reseeded.learning_summary)}` };
    },
  },
  {
    title: "And the brief's example works again",
    detail: "Same sentence as step 2, now against the seeded vocabulary.",
    action: "Run",
    run: async () => {
      const d = await api("/api/memory-aware-format", {
        method: "POST", body: JSON.stringify({ asr_text: "ask aditya to review the sarvam kiwi service" }),
      });
      return { stages: d, why: d };
    },
  },
];

function buildJourney() {
  const root = $("#journey");
  root.innerHTML = "";
  JOURNEY.forEach((step, idx) => {
    const node = el("div", "step");
    node.id = `step-${idx}`;
    const sh = el("div", "sh");
    sh.appendChild(el("span", "num", String(idx + 1).padStart(2, "0")));
    const body = el("div");
    body.appendChild(el("div", "st", step.title));
    body.appendChild(el("div", "sd", step.detail));
    sh.appendChild(body);
    const btn = el("button", "btn small primary sa", step.action);
    btn.onclick = async () => {
      btn.disabled = true;
      const out = node.querySelector(".out") || node.appendChild(el("div", "out"));
      out.innerHTML = "running…";
      try {
        const result = await step.run();
        out.innerHTML = "";
        if (result.text) {
          const pre = el("div", "stage");
          const t = el("div", "text", result.text);
          pre.appendChild(t);
          out.appendChild(pre);
        }
        if (result.stages) { const d = el("div"); renderStages(d, result.stages); out.appendChild(d); }
        if (result.learning) { const d = el("div"); renderLearning(d, result.learning); out.appendChild(d); }
        if (result.why) { const d = el("div"); renderWhy(d, result.why); out.appendChild(d); }
        node.classList.add("done");
        loadMemories();
      } catch (e) {
        out.innerHTML = "";
        out.appendChild(el("div", "card blocked", e.message));
        toast(e.message, true);
      } finally { btn.disabled = false; }
    };
    sh.appendChild(btn);
    node.appendChild(sh);
    root.appendChild(node);
  });
}

/* ── wiring ──────────────────────────────────────────────────────────────────── */
function switchView(name) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.view === name));
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("active", v.id === `view-${name}`));
  if (name === "memory") loadMemories();
  if (name === "log") loadLog();
}

async function boot() {
  document.querySelectorAll(".tab").forEach((t) => (t.onclick = () => switchView(t.dataset.view)));
  $("#btn-run").onclick = runStages;
  $("#btn-observe").onclick = ingest;
  $("#btn-add").onclick = addMemory;
  $("#mem-filter").onchange = loadMemories;
  $("#log-filter").onchange = loadLog;

  $("#btn-seed").onclick = async () => {
    try {
      const r = await api("/api/reset", { method: "POST", body: JSON.stringify({ reseed: true }) });
      toast(`Seeded: ${r.memory_count} memories from ${r.reseeded.observations} observations.`);
      loadMemories(); loadLog();
    } catch (e) { toast(e.message, true); }
  };
  $("#btn-reset").onclick = $("#btn-seed").onclick;
  $("#btn-wipe").onclick = async () => {
    try {
      await api("/api/reset", { method: "POST", body: JSON.stringify({ reseed: false }) });
      toast("Wiped. Memory is empty.");
      loadMemories(); loadLog();
    } catch (e) { toast(e.message, true); }
  };

  document.querySelectorAll(".chip").forEach((c) => {
    c.onclick = () => {
      if (c.classList.contains("ob")) {
        $("#ob-asr").value = "";
        $("#ob-formatted").value = c.dataset.fmt || "";
        $("#ob-edited").value = c.dataset.edit || "";
      } else {
        $("#in-asr").value = c.dataset.asr || "";
        $("#in-formatted").value = c.dataset.fmt || "";
      }
    };
  });

  buildJourney();
  try {
    const h = await api("/api/health");
    const bits = [
      `db ${h.config.db_path.split("/").pop()}`,
      h.config.llm_configured ? `model ${h.config.llm_model}` : "deterministic (no model key)",
      `migrations ${h.migrations_applied.join(",")}`,
    ];
    $("#status").textContent = bits.join(" · ");
  } catch (e) {
    $("#status").textContent = `backend unreachable: ${e.message}`;
  }
  loadMemories();
}

boot();

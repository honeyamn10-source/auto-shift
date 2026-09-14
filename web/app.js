"use strict";
const $ = (id) => document.getElementById(id);
const params = new URLSearchParams(location.hash.slice(1));
let token = params.get("token") || sessionStorage.getItem("autoshift-token") || "";
if (token) sessionStorage.setItem("autoshift-token", token);
history.replaceState(null, "", location.pathname);
let current = null;
let inFlight = false;
let approvalId = null;
let lastImage = null;

function notice(message = "") { $("notice").textContent = message; }
async function api(path, body) {
  const response = await fetch("/api/" + path, {
    method: body === undefined ? "GET" : "POST",
    headers: { "Content-Type": "application/json", "X-Autoshift-Token": token },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store"
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Request failed.");
  return data;
}
function render(state) {
  current = state;
  $("status").textContent = state.status.replaceAll("_", " ");
  $("status").dataset.state = state.status;
  const busy = ["running", "awaiting_approval"].includes(state.status);
  $("open").disabled = state.browser_open || inFlight;
  $("close").disabled = !state.browser_open || inFlight;
  $("start").disabled = !state.browser_open || busy || inFlight;
  $("stop").disabled = !busy || inFlight;
  $("domains").disabled = state.browser_open;
  $("approval").hidden = !state.pending;
  approvalId = state.pending?.id || null;
  $("approve").disabled = inFlight;
  $("reject").disabled = inFlight;
  if (state.pending) {
    $("goal").textContent = state.pending.goal || "Review the next action";
    $("actions").textContent = JSON.stringify(state.pending.actions, null, 2);
  }
  $("page-url").textContent = state.url || "The latest reviewed step appears here.";
  if (lastImage !== state.screenshot) {
    lastImage = state.screenshot;
    $("screenshot").hidden = !lastImage;
    $("empty-preview").hidden = !!lastImage;
    if (lastImage) $("screenshot").src = "data:image/png;base64," + lastImage;
    else $("screenshot").removeAttribute("src");
  }
  $("events").replaceChildren(...state.events.map((event) => {
    const li = document.createElement("li");
    li.textContent = event.time + " — " + event.message;
    return li;
  }));
  $("result").textContent = state.result || "";
  $("export").disabled = !state.result;
}
async function refresh() {
  try { render(await api("state")); }
  catch (error) { notice(error.message); $("status").textContent = "Disconnected"; }
}
async function action(fn) {
  if (inFlight) return;
  inFlight = true;
  if (current) render(current);
  notice("");
  try { await fn(); } catch (error) { notice(error.message); }
  finally { inFlight = false; await refresh(); }
}
$("open").addEventListener("click", () => action(() => api("browser", {
  domains: $("domains").value.split(",").map((s) => s.trim()).filter(Boolean)
})));
$("close").addEventListener("click", () => action(() => api("close", {})));
$("stop").addEventListener("click", () => action(() => api("stop", {})));
$("start").addEventListener("click", () => action(async () => {
  const key = $("key").value;
  $("key").value = "";
  await api("tasks", {
    task: $("task").value.trim(), provider: $("provider").value,
    model: $("model").value.trim(), api_key: key,
    max_steps: Number($("steps").value), vision: $("vision").checked
  });
}));
for (const [id, approve] of [["approve", true], ["reject", false]]) {
  $(id).addEventListener("click", () => {
    const idToApprove = approvalId;
    if (!idToApprove) return;
    action(() => api("decision", { approval_id: idToApprove, approve }));
  });
}
$("provider").addEventListener("change", () => {
  const local = $("provider").value === "ollama";
  $("key-section").hidden = local;
  $("ollama-note").hidden = !local;
  $("model").placeholder = local ? "Exact name of your installed Ollama model" : "Enter a model available to your account";
});
$("export").addEventListener("click", () => {
  const blob = new Blob([current?.result || ""], {type: "text/plain;charset=utf-8"});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url; link.download = "auto-shift-result.txt"; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
async function poll() { await refresh(); setTimeout(poll, 1800); }
poll();

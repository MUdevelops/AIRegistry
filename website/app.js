const C = window.AIREGISTRY || {};
const $ = (id) => document.getElementById(id);
const h = (t, p = {}, ...k) => {
  const e = document.createElement(t);
  Object.assign(e, p);
  e.append(...k);
  return e;
};

let all = [];
let cat = "";
let authUser = null;

function latest(m) {
  return [...(m.versions || [])].sort((a, b) => compareVersions(b.version, a.version))[0];
}
function compareVersions(a, b) {
  const av = a.split(".").map(Number), bv = b.split(".").map(Number);
  for (let i = 0; i < 3; i++) if (av[i] !== bv[i]) return av[i] - bv[i];
  return 0;
}
function selectedComponent() {
  const raw = location.hash.slice(2).split("?")[0];
  if (!raw) return null;
  return all.find((m) => m.name === raw);
}
function card(m) {
  const v = latest(m);
  return h("a", { className: "card", href: "#/" + m.name },
    h("h3", {}, m.name, h("small", {}, " v" + v.version)),
    h("p", {}, m.description),
    h("div", {}, ...(m.tags || []).map((t) => h("span", { className: "tag" }, t)))
  );
}
function render() {
  const q = $("q").value.toLowerCase().split(/\s+/).filter(Boolean);
  const list = all.filter((m) => {
    const v = latest(m);
    return (!cat || m.category === cat) && q.every((t) =>
      [m.name, m.description, m.category, ...(m.tags || [])].join(" ").toLowerCase().includes(t)
    );
  });
  $("grid").replaceChildren(...(list.length ? list.map(card) : [h("p", {}, "No matches.")]));
  const cats = ["", ...new Set(all.map((m) => m.category))].sort();
  $("cats").replaceChildren(...cats.map((c) => h("button", {
    className: c === cat ? "on" : "",
    onclick: () => { cat = c; render(); }
  }, c || "all")));
}
function detail(m) {
  const versions = [...m.versions].sort((a, b) => compareVersions(b.version, a.version));
  const requested = new URLSearchParams(location.hash.includes("?") ? location.hash.split("?")[1] : "").get("version");
  const v = versions.find((x) => x.version === requested) || versions[0];
  const rows = [
    ["Category", v.category], ["Runtime", v.runtime], ["License", v.license],
    ["Tags", (v.tags || []).join(", ") || "none"],
    ["Dependencies", (v.dependencies || []).join(", ") || "none"],
    ["Files", (v.files || []).join(", ")]
  ];
  const versionLinks = versions.map((x) => h("option", { value: x.version }, x.version));
  const select = h("select", { onchange: () => {
    location.hash = `/${m.name}?version=${encodeURIComponent(select.value)}`;
  }}, ...versionLinks);
  select.value = v.version;

  $("detail").replaceChildren(
    h("a", { href: "#/" }, "← all components"),
    h("h1", {}, m.name, h("small", {}, " v" + v.version)),
    h("p", {}, v.description),
    h("p", {}, "Latest release: " + m.latest_version),
    h("label", {}, "Version ", select),
    h("pre", {}, "$ ai add " + m.name + "@" + v.version),
    v.release_notes ? h("section", {}, h("h2", {}, "Release notes"), h("p", {}, v.release_notes)) : "",
    h("dl", {}, ...rows.flatMap(([a, b]) => [h("dt", {}, a), h("dd", {}, b)]))
  );
}
function route() {
  const path = location.hash.slice(1);
  if (path === "/submit") {
    $("home").hidden = true; $("detail").hidden = true; $("submit").hidden = false; return;
  }
  const m = selectedComponent();
  $("home").hidden = !!m; $("detail").hidden = !m; $("submit").hidden = true;
  if (m) detail(m);
}
async function renderAuth() {
  const box = $("auth"); if (!box) return;
  box.replaceChildren(); authUser = null;
  const base = (C.AUTH_URL || "").replace(/\/$/, "");
  if (!base) return;
  try {
    const response = await fetch(base + "/me", { credentials: "same-origin", cache: "no-store", headers: { Accept: "application/json" } });
    const data = await response.json();
    if (data.authenticated && data.login) {
      authUser = data.login;
      box.append(h("span", { className: "auth-user" }, "✓ " + data.login + " "),
                 h("a", { className: "auth-link", href: base + "/logout" }, "Sign out"));
      return;
    }
  } catch (_) {}
  box.append(h("a", { className: "auth-link", href: base + "/login" }, "Sign in with GitHub"));
}
function csvTags(value) {
  return value.split(",").map((x) => x.trim().toLowerCase()).filter(Boolean);
}
function renderDependencyOptions() {
  let datalist = $("registry-dependencies");
  if (!datalist) {
    datalist = document.createElement("datalist");
    datalist.id = "registry-dependencies";
    document.body.appendChild(datalist);
  }
  const currentName = $("component-name")?.value.trim().toLowerCase() || "";
  datalist.replaceChildren(...all.filter((m) => m.name !== currentName).sort((a,b) => a.name.localeCompare(b.name))
    .flatMap((m) => (m.versions || []).map((v) => h("option", { value: `${m.name}@${v.version}` }))));
}
function addDependency(value = "") {
  const row = h("div", { className: "dependency-row" });
  const input = h("input", { className: "dependency-input", placeholder: "component@1.0.0", value });
  input.setAttribute("list", "registry-dependencies");
  const optional = h("label", { className: "optional-check" }, h("input", { type: "checkbox" }), "Optional");
  const remove = h("button", { type: "button", className: "remove-btn", onclick: () => row.remove() }, "Remove");
  row.append(input, optional, remove); $("dependencies-list").appendChild(row);
}
function collectDependencies() {
  return [...document.querySelectorAll(".dependency-row")].map((row) => {
    const name = row.querySelector(".dependency-input").value.trim().toLowerCase();
    if (!name) return "";
    return row.querySelector('input[type="checkbox"]').checked ? `${name} (optional)` : name;
  }).filter(Boolean);
}
function addFile(path = "", content = "") {
  const row = h("div", { className: "file-row" });
  const top = h("div", { className: "file-row-top" });
  const pathInput = h("input", { className: "file-path", placeholder: "src/main.py", value: path });
  const remove = h("button", { type: "button", className: "remove-btn", onclick: () => row.remove() }, "Remove");
  const textarea = h("textarea", { className: "file-content", placeholder: "File content...", rows: 12 });
  textarea.value = content; top.append(pathInput, remove); row.append(top, textarea); $("files-list").appendChild(row);
}
function collectFiles() {
  return [...document.querySelectorAll(".file-row")].map((row) => ({
    path: row.querySelector(".file-path").value.trim(),
    content: row.querySelector(".file-content").value
  })).filter((file) => file.path);
}
function syncPublishMode() {
  const mode = $("publish-mode").value;
  const releaseHint = $("release-component");
  const name = $("component-name");
  if (mode === "release") {
    releaseHint.hidden = false;
    name.placeholder = "Existing component name";
  } else {
    releaseHint.hidden = true;
    name.placeholder = "my-component";
  }
}
function submitComponent(event) {
  event.preventDefault();
  const status = $("submit-status");
  const button = event.submitter;
  status.textContent = "";
  if (!authUser) {
    status.textContent = "Please sign in with GitHub first.";
    window.location.href = ((C.AUTH_URL || "/auth").replace(/\/$/, "")) + "/login";
    return;
  }
  const files = collectFiles();
  const dependencies = collectDependencies();
  const currentName = $("component-name").value.trim().toLowerCase();
  const dependencyNames = dependencies.map((d) => d.replace(/ \(optional\)$/, ""));
  if (new Set(dependencyNames).size !== dependencyNames.length) { status.textContent = "Duplicate dependencies are not allowed."; return; }
  for (const dep of dependencyNames) {
    if (dep.startsWith(currentName + "@")) { status.textContent = "A component cannot depend on itself."; return; }
    const at = dep.lastIndexOf("@");
    if (at < 1 || !all.some((m) => m.name === dep.slice(0, at) && m.versions.some((v) => v.version === dep.slice(at + 1)))) {
      status.textContent = `Dependency '${dep}' was not found in the registry.`; return;
    }
  }
  if (!files.some((f) => f.path === "README.md")) { status.textContent = "README.md is required."; return; }
  if (!files.some((f) => f.path.startsWith("src/"))) { status.textContent = "At least one src/ file is required."; return; }

  button.disabled = true; button.textContent = "Submitting...";
  const payload = {
    publish_mode: $("publish-mode").value,
    name: $("component-name").value.trim(),
    version: $("component-version").value.trim(),
    description: $("component-description").value.trim(),
    category: $("component-category").value.trim().toLowerCase(),
    runtime: $("component-runtime").value.trim(),
    license: $("component-license").value.trim(),
    tags: csvTags($("component-tags").value),
    dependencies,
    release_notes: $("component-release-notes").value.trim(),
    files
  };
  fetch("/api/publisher/submit", {
    method: "POST", credentials: "same-origin",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(payload)
  }).then(async (response) => {
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || data.error || "Submission failed.");
    status.textContent = `Submitted ${data.component}@${data.version}. Pull Request created.`;
    if (data.pull_request) {
      const link = document.createElement("a");
      link.href = data.pull_request; link.target = "_blank"; link.rel = "noopener";
      link.textContent = " Open Pull Request"; status.appendChild(link);
    }
    event.target.reset(); $("dependencies-list").replaceChildren(); $("files-list").replaceChildren();
    addDependency(); addFile("README.md"); addFile("src/main.py"); syncPublishMode();
  }).catch((error) => { status.textContent = error.message || "Could not submit component."; })
    .finally(() => { button.disabled = false; button.textContent = "Submit for Review"; });
}
$("q").oninput = render;
$("component-name").addEventListener("input", renderDependencyOptions);
$("publish-mode").addEventListener("change", syncPublishMode);
$("submit-component").onclick = () => { location.hash = "/submit"; route(); };
$("add-dependency").onclick = () => addDependency();
$("add-file").onclick = () => addFile();
$("submit-form").addEventListener("submit", submitComponent);
window.onhashchange = route;
addFile("README.md", "# My Component\n\nDescribe your component here.");
addFile("src/main.py", "def main():\n    pass\n");
addDependency();
fetch(C.REGISTRY_URL || "registry.json").then((r) => { if (!r.ok) throw new Error(); return r.json(); })
  .then((d) => { all = Array.isArray(d.components) ? d.components : []; renderDependencyOptions(); render(); route(); })
  .catch(() => { $("grid").textContent = "Could not load registry.json. Serve over HTTP."; });
renderAuth();

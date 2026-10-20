const C = window.AIREGISTRY || {};
const $ = (id) => document.getElementById(id);
const h = (tag, props = {}, ...children) => {
  const node = document.createElement(tag);
  Object.assign(node, props);
  node.append(...children);
  return node;
};

let all = [];

// A registry entry holds every release in `versions`; merge the latest one so the UI can read
// m.version, m.files, m.source, ... directly. Flat (legacy) entries pass through unchanged.
function normalizeComponent(entry) {
  if (!Array.isArray(entry.versions) || !entry.versions.length) return entry;
  const latest = entry.versions.find((v) => v.version === entry.latest_version) || entry.versions[0];
  return { ...latest, ...entry, ...latest, versions: entry.versions, latest_version: latest.version };
}

function splitDependency(value) {
  const optional = / \(optional\)$/.test(value);
  const [name, version = ""] = value.replace(/ \(optional\)$/, "").split("@");
  return { name, version, optional };
}
let cat = "";
let authUser = null;

function escCommand(text) {
  return String(text).replace(/([\\`$])/g, "\\$1");
}

function card(m) {
  const deps = (m.dependencies || []).length;
  return h(
    "a",
    { className: "component-card", href: "#/" + m.name },
    h("div", { className: "card-top" },
      h("span", { className: "category-label" }, m.category || "component"),
      h("span", { className: "version-label" }, "v" + m.version)
    ),
    h("h3", {}, m.name),
    h("p", {}, m.description),
    h("div", { className: "card-bottom" },
      h("div", { className: "tag-list" }, ...(m.tags || []).slice(0, 4).map((t) => h("span", { className: "tag" }, t))),
      h("span", { className: "dependency-count" }, deps ? `${deps} dep${deps === 1 ? "" : "s"}` : "No deps")
    )
  );
}

function render() {
  const query = $("q").value.toLowerCase().split(/\s+/).filter(Boolean);
  const list = all.filter((m) => {
    if (cat && m.category !== cat) return false;
    const haystack = [m.name, m.description, m.category, m.runtime, ...(m.tags || []), ...(m.dependencies || [])].join(" ").toLowerCase();
    return query.every((term) => haystack.includes(term));
  });

  $("grid").replaceChildren(
    ...(list.length ? list.map(card) : [
      h("div", { className: "empty-state" },
        h("strong", {}, "No components found"),
        h("p", {}, "Try another search term or clear the category filter.")
      )
    ])
  );

  $("result-count").textContent = `${list.length} shown`;

  const categories = ["", ...new Set(all.map((m) => m.category).filter(Boolean))].sort();
  $("cats").replaceChildren(...categories.map((value) => h(
    "button",
    { className: value === cat ? "filter active" : "filter", type: "button", onclick: () => { cat = value; render(); } },
    value || "All"
  )));
}

function renderStats() {
  $("stat-components").textContent = all.length;
  $("stat-categories").textContent = new Set(all.map((m) => m.category)).size;
}

function detail(m) {
  const deps = m.dependencies || [];
  const files = m.files || [];
  const sourceUrl = `https://github.com/MUdevelops/AIRegistry/tree/main/${m.source}`;
  const command = `ai add ${m.name}@${m.version}`;
  const releases = (m.versions || []).map((v) => v.version);

  $("detail").replaceChildren(
    h("div", { className: "detail-shell" },
      h("a", { className: "back-link", href: "#/" }, "← Back to catalog"),
      h("div", { className: "detail-hero" },
        h("div", { className: "eyebrow" }, (m.category || "component").toUpperCase()),
        h("h1", {}, m.name, h("small", {}, "v" + m.version)),
        h("p", { className: "detail-description" }, m.description),
        h("div", { className: "detail-actions" },
          h("button", { className: "button button-primary", type: "button", onclick: () => copyText(command) }, "Copy install command"),
          h("a", { className: "button button-secondary", href: sourceUrl, target: "_blank", rel: "noopener" }, "View source ↗")
        )
      ),
      h("div", { className: "detail-grid" },
        h("section", { className: "detail-panel" },
          h("div", { className: "panel-label" }, "INSTALL"),
          h("pre", { className: "install-code" }, `$ ${command}`),
          h("p", { className: "detail-note" }, "The CLI installs the component source locally; declared dependencies are metadata and are not installed automatically.")
        ),
        h("section", { className: "detail-panel" },
          h("div", { className: "panel-label" }, "METADATA"),
          h("dl", {},
            metadataRow("Category", m.category),
            metadataRow("Runtime", m.runtime),
            metadataRow("License", m.license),
            metadataRow("Tags", (m.tags || []).join(", ") || "none"),
            metadataRow("Source", m.source)
          )
        )
      ),
      releases.length > 1 ? h("section", { className: "detail-panel detail-wide" },
        h("div", { className: "panel-label" }, `RELEASES · ${releases.length}`),
        h("div", { className: "file-list" }, ...(m.versions || []).map((v) => h("code", { title: v.release_notes || "" }, `${v.version === m.version ? "★ " : ""}${v.version}`)))
      ) : "",
      m.release_notes ? h("section", { className: "detail-panel detail-wide" },
        h("div", { className: "panel-label" }, `RELEASE NOTES · ${m.version}`),
        h("p", { className: "detail-note" }, m.release_notes)
      ) : "",
      h("section", { className: "detail-panel detail-wide" },
        h("div", { className: "panel-label" }, `FILES · ${files.length}`),
        h("div", { className: "file-list" }, ...files.map((file) => h("code", {}, file)))
      ),
      h("section", { className: "detail-panel detail-wide" },
        h("div", { className: "panel-label" }, `DEPENDENCIES · ${deps.length}`),
        deps.length
          ? h("div", { className: "dependency-pills" }, ...deps.map((dep) => h("span", {}, dep)))
          : h("p", { className: "detail-note" }, "No registry dependencies declared.")
      )
    )
  );
}

function metadataRow(label, value) {
  return h("div", { className: "metadata-row" }, h("dt", {}, label), h("dd", {}, value || "—"));
}

function route() {
  const path = location.hash.slice(1);
  if (path === "/submit") {
    $("home").hidden = true;
    $("detail").hidden = true;
    $("submit").hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }

  const name = location.hash.startsWith("#/") ? location.hash.slice(2) : "";
  const match = all.find((m) => m.name === name);
  $("home").hidden = !!match;
  $("detail").hidden = !match;
  $("submit").hidden = true;
  if (match) {
    detail(match);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

async function renderAuth() {
  const box = $("auth");
  box.replaceChildren();
  authUser = null;
  if (!C.AUTH_URL) return;
  const base = C.AUTH_URL.replace(/\/$/, "");

  try {
    const response = await fetch(base + "/me", { credentials: "same-origin", cache: "no-store", headers: { Accept: "application/json" } });
    const data = await response.json();
    if (data.authenticated && data.login) {
      authUser = data.login;
      box.append(
        h("span", { className: "auth-user" }, "● " + data.login),
        h("a", { className: "auth-link", href: base + "/logout" }, "Sign out")
      );
      return;
    }
  } catch (_) {}

  box.append(h("a", { className: "auth-link", href: base + "/login" }, "Sign in with GitHub"));
}

function csvTags(value) {
  return value.split(",").map((x) => x.trim().toLowerCase()).filter(Boolean);
}

function renderDependencyOptions() {
  let list = $("registry-dependencies");
  if (!list) {
    list = document.createElement("datalist");
    list.id = "registry-dependencies";
    document.body.appendChild(list);
  }
  const current = $("component-name")?.value.trim().toLowerCase() || "";
  list.replaceChildren(...all.filter((m) => m.name !== current).sort((a, b) => a.name.localeCompare(b.name)).map((m) => h("option", { value: m.name })));
}

function addDependency(value = "") {
  const row = h("div", { className: "dependency-row" });
  const input = h("input", { className: "dependency-input", placeholder: "Select or type a component", value });
  input.setAttribute("list", "registry-dependencies");
  const optional = h("label", { className: "optional-check" }, h("input", { type: "checkbox" }), "Optional");
  const remove = h("button", { type: "button", className: "remove-btn" }, "Remove");
  remove.onclick = () => row.remove();
  row.append(input, optional, remove);
  $("dependencies-list").appendChild(row);
}

function collectDependencies() {
  return [...document.querySelectorAll(".dependency-row")].map((row) => {
    const input = row.querySelector(".dependency-input");
    const checkbox = row.querySelector('input[type="checkbox"]');
    const name = input.value.trim().toLowerCase();
    if (!name) return "";
    return checkbox.checked ? `${name} (optional)` : name;
  }).filter(Boolean);
}

function addFile(path = "", content = "") {
  const row = h("div", { className: "file-row" });
  const top = h("div", { className: "file-row-top" });
  const pathInput = h("input", { className: "file-path", placeholder: "src/main.py", value: path });
  const remove = h("button", { type: "button", className: "remove-btn" }, "Remove");
  const textarea = h("textarea", { className: "file-content", placeholder: "File content…", rows: 10 });
  textarea.value = content;
  remove.onclick = () => row.remove();
  top.append(pathInput, remove);
  row.append(top, textarea);
  $("files-list").appendChild(row);
}

function collectFiles() {
  return [...document.querySelectorAll(".file-row")].map((row) => ({
    path: row.querySelector(".file-path").value.trim(),
    content: row.querySelector(".file-content").value
  })).filter((file) => file.path);
}

async function submitComponent(event) {
  event.preventDefault();
  const status = $("submit-status");
  const button = event.submitter;
  status.replaceChildren();

  if (!authUser) {
    status.textContent = "Please sign in with GitHub first.";
    window.location.href = (C.AUTH_URL || "/auth").replace(/\/$/, "") + "/login";
    return;
  }

  const files = collectFiles();
  const dependencies = collectDependencies();
  const currentName = $("component-name").value.trim().toLowerCase();
  const parsed = dependencies.map(splitDependency);
  const dependencyNames = parsed.map((d) => d.name);

  if (new Set(dependencyNames).size !== dependencyNames.length) {
    status.textContent = "Duplicate dependencies are not allowed.";
    return;
  }
  for (const dep of parsed) {
    if (dep.name === currentName) {
      status.textContent = "A component cannot depend on itself.";
      return;
    }
    const target = all.find((m) => m.name === dep.name);
    if (!target) {
      status.textContent = `Dependency '${dep.name}' was not found in the registry.`;
      return;
    }
    if (dep.version && !(target.versions || [target]).some((v) => v.version === dep.version)) {
      status.textContent = `Dependency '${dep.name}' has no release ${dep.version}.`;
      return;
    }
  }
  // Pin every dependency to an exact release (plain names resolve to the latest one).
  const pinnedDependencies = parsed.map((dep) => {
    const target = all.find((m) => m.name === dep.name);
    return `${dep.name}@${dep.version || target.version}${dep.optional ? " (optional)" : ""}`;
  });

  if (!files.some((f) => f.path === "README.md")) {
    status.textContent = "README.md is required.";
    return;
  }
  if (!files.some((f) => f.path.startsWith("src/"))) {
    status.textContent = "At least one src/ file is required.";
    return;
  }

  button.disabled = true;
  button.textContent = "Submitting…";

  const payload = {
    name: $("component-name").value.trim(),
    version: $("component-version").value.trim(),
    description: $("component-description").value.trim(),
    category: $("component-category").value.trim().toLowerCase(),
    runtime: $("component-runtime").value.trim(),
    license: $("component-license").value.trim(),
    tags: csvTags($("component-tags").value),
    release_notes: $("component-release-notes").value.trim(),
    dependencies: pinnedDependencies,
    files
  };

  try {
    const response = await fetch("/api/publisher/submit", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || data.error || "Submission failed.");

    status.append(h("span", { className: "success-message" }, "Submitted successfully. Pull Request created."));
    if (data.pull_request) {
      status.append(" ", h("a", { href: data.pull_request, target: "_blank", rel: "noopener" }, "Open Pull Request ↗"));
    }
    event.target.reset();
    $("dependencies-list").replaceChildren();
    $("files-list").replaceChildren();
    addDependency();
    addFile("README.md", "# My Component\n\nDescribe your component here.");
    addFile("src/main.py", "def main():\n    pass\n");
    renderDependencyOptions();
  } catch (error) {
    status.textContent = error.message || "Could not submit component.";
  } finally {
    button.disabled = false;
    button.textContent = "Submit for review";
  }
}

async function copyText(value) {
  try {
    await navigator.clipboard.writeText(value);
    const active = document.activeElement;
    const original = active?.textContent;
    if (active && active.classList.contains("button")) {
      active.textContent = "Copied ✓";
      setTimeout(() => { active.textContent = original; }, 1400);
    }
  } catch (_) {}
}

function loadHealth() {
  $("stat-health").textContent = "Checking";
  fetch("/api/health", { cache: "no-store", headers: { Accept: "application/json" } })
    .then((r) => r.json().then((data) => ({ ok: r.ok && data.ok })))
    .then(({ ok }) => { $("stat-health").textContent = ok ? "Online" : "Degraded"; })
    .catch(() => { $("stat-health").textContent = "Offline"; });
}

$("q").oninput = render;
$("component-name").addEventListener("input", renderDependencyOptions);
$("submit-component")?.addEventListener("click", () => { location.hash = "/submit"; route(); });
$("add-dependency").onclick = () => addDependency();
$("add-file").onclick = () => addFile();
$("submit-form").addEventListener("submit", submitComponent);
$("copy-command").onclick = () => copyText("pip install airegistry-cli\nai search rag\nai info keyword-rag\nai add keyword-rag");
window.onhashchange = route;

addFile("README.md", "# My Component\n\nDescribe your component here.");
addFile("src/main.py", "def main():\n    pass\n");
addDependency();

fetch(C.REGISTRY_URL || "registry.json", { cache: "no-store" })
  .then((r) => { if (!r.ok) throw new Error("registry"); return r.json(); })
  .then((d) => {
    all = Array.isArray(d.components) ? d.components.map(normalizeComponent) : [];
    renderStats();
    renderDependencyOptions();
    render();
    route();
  })
  .catch(() => {
    $("grid").replaceChildren(h("div", { className: "empty-state error-state" }, h("strong", {}, "Registry unavailable"), h("p", {}, "The catalog index could not be loaded. Please refresh or check the service status.")));
    $("result-count").textContent = "Unavailable";
  });

renderAuth();
loadHealth();

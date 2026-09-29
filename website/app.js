const C = window.AIREGISTRY || {};
const $ = (id) => document.getElementById(id);
// DOM builder using textContent only: registry data is untrusted.
const h = (t, p = {}, ...k) => { const e = document.createElement(t); Object.assign(e, p); e.append(...k); return e; };
let all = [], cat = "";

function card(m) {
  return h("a", { className: "card", href: "#/" + m.name },
    h("h3", {}, m.name, h("small", {}, " v" + m.version)),
    h("p", {}, m.description),
    h("div", {}, ...m.tags.map((t) => h("span", { className: "tag" }, t))));
}

function render() {
  const q = $("q").value.toLowerCase().split(/\s+/).filter(Boolean);
  const list = all.filter((m) => (!cat || m.category === cat) &&
    q.every((t) => [m.name, m.description, m.category, ...m.tags].join(" ").toLowerCase().includes(t)));
  $("grid").replaceChildren(...(list.length ? list.map(card) : [h("p", {}, "No matches.")]));
  const cats = ["", ...new Set(all.map((m) => m.category))].sort();
  $("cats").replaceChildren(...cats.map((c) =>
    h("button", { className: c === cat ? "on" : "", onclick: () => { cat = c; render(); } }, c || "all")));
}

function detail(m) {
  const rows = [["Category", m.category], ["Runtime", m.runtime], ["License", m.license],
    ["Tags", m.tags.join(", ")], ["Dependencies", (m.dependencies || []).join(", ") || "none"],
    ["Files", m.files.join(", ")], ["Source", m.source]];
  $("detail").replaceChildren(h("a", { href: "#/" }, "< all components"),
    h("h1", {}, m.name, h("small", {}, " v" + m.version)), h("p", {}, m.description),
    h("pre", {}, "$ ai add " + m.name),
    h("dl", {}, ...rows.flatMap(([a, b]) => [h("dt", {}, a), h("dd", {}, b)])));
}

function route() {
  const m = all.find((x) => x.name === location.hash.slice(2));
  $("home").hidden = !!m; $("detail").hidden = !m;
  if (m) detail(m);
}

if (C.AUTH_URL) $("auth").append(h("a", { href: C.AUTH_URL.replace(/\/$/, "") + "/login" }, "Sign in with GitHub"));
$("q").oninput = render;
window.onhashchange = route;
fetch(C.REGISTRY_URL || "registry.json")
  .then((r) => { if (!r.ok) throw 0; return r.json(); })
  .then((d) => { all = d.components; render(); route(); })
  .catch(() => { $("grid").textContent = "Could not load registry.json. Serve over http: python -m http.server -d website"; });

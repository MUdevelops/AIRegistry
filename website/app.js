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

function card(m) {
  return h(
    "a",
    {
      className: "card",
      href: "#/" + m.name
    },
    h(
      "h3",
      {},
      m.name,
      h("small", {}, " v" + m.version)
    ),
    h("p", {}, m.description),
    h(
      "div",
      {},
      ...(m.tags || []).map((t) =>
        h("span", { className: "tag" }, t)
      )
    )
  );
}

function render() {
  const q = $("q").value
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean);

  const list = all.filter(
    (m) =>
      (!cat || m.category === cat) &&
      q.every((t) =>
        [
          m.name,
          m.description,
          m.category,
          ...(m.tags || [])
        ]
          .join(" ")
          .toLowerCase()
          .includes(t)
      )
  );

  $("grid").replaceChildren(
    ...(list.length
      ? list.map(card)
      : [h("p", {}, "No matches.")]
    )
  );

  const cats = [
    "",
    ...new Set(all.map((m) => m.category))
  ].sort();

  $("cats").replaceChildren(
    ...cats.map((c) =>
      h(
        "button",
        {
          className: c === cat ? "on" : "",
          onclick: () => {
            cat = c;
            render();
          }
        },
        c || "all"
      )
    )
  );
}

function detail(m) {
  const rows = [
    ["Category", m.category],
    ["Runtime", m.runtime],
    ["License", m.license],
    ["Tags", (m.tags || []).join(", ") || "none"],
    [
      "Dependencies",
      (m.dependencies || []).join(", ") || "none"
    ],
    [
      "Files",
      (m.files || []).join(", ")
    ],
    ["Source", m.source]
  ];

  $("detail").replaceChildren(
    h(
      "a",
      { href: "#/" },
      "← all components"
    ),
    h(
      "h1",
      {},
      m.name,
      h("small", {}, " v" + m.version)
    ),
    h("p", {}, m.description),
    h("pre", {}, "$ ai add " + m.name),
    h(
      "dl",
      {},
      ...rows.flatMap(([a, b]) => [
        h("dt", {}, a),
        h("dd", {}, b)
      ])
    )
  );
}

function route() {
  const path = location.hash.slice(1);

  if (path === "/submit") {
    $("home").hidden = true;
    $("detail").hidden = true;
    $("submit").hidden = false;
    return;
  }

  const m = all.find(
    (x) => x.name === location.hash.slice(2)
  );

  $("home").hidden = !!m;
  $("detail").hidden = !m;
  $("submit").hidden = true;

  if (m) {
    detail(m);
  }
}

async function renderAuth() {
  const box = $("auth");

  if (!box) return;

  box.replaceChildren();
  authUser = null;

  if (!C.AUTH_URL) return;

  const base = C.AUTH_URL.replace(/\/$/, "");

  try {
    const response = await fetch(base + "/me", {
      credentials: "same-origin",
      cache: "no-store",
      headers: {
        Accept: "application/json"
      }
    });

    const data = await response.json();

    if (data.authenticated && data.login) {
      authUser = data.login;

      box.append(
        h(
          "span",
          {
            className: "auth-user"
          },
          "✓ " + data.login + " "
        ),
        h(
          "a",
          {
            className: "auth-link",
            href: base + "/logout"
          },
          "Sign out"
        )
      );

      return;
    }
  } catch (_) {}

  box.append(
    h(
      "a",
      {
        className: "auth-link",
        href: base + "/login"
      },
      "Sign in with GitHub"
    )
  );
}

function csvTags(value) {
  return value
    .split(",")
    .map((x) => x.trim().toLowerCase())
    .filter(Boolean);
}


/* ---------------- Dependencies ---------------- */

function addDependency(value = "") {
  const row = h(
    "div",
    {
      className: "dependency-row"
    }
  );

  const input = h(
    "input",
    {
      className: "dependency-input",
      placeholder: "component-name",
      value
    }
  );

  const optional = h(
    "label",
    {
      className: "optional-check"
    },
    h("input", {
      type: "checkbox"
    }),
    "Optional"
  );

  const remove = h(
    "button",
    {
      type: "button",
      className: "remove-btn"
    },
    "Remove"
  );

  remove.onclick = () => row.remove();

  row.append(
    input,
    optional,
    remove
  );

  $("dependencies-list").appendChild(row);
}

function collectDependencies() {
  return [
    ...document.querySelectorAll(
      ".dependency-row"
    )
  ]
    .map((row) => {
      const input =
        row.querySelector(".dependency-input");

      const checkbox =
        row.querySelector(
          'input[type="checkbox"]'
        );

      const name = input.value
        .trim()
        .toLowerCase();

      if (!name) return "";

      return checkbox.checked
        ? `${name} (optional)`
        : name;
    })
    .filter(Boolean);
}


/* ---------------- Files ---------------- */

function addFile(path = "", content = "") {
  const row = h(
    "div",
    {
      className: "file-row"
    }
  );

  const top = h(
    "div",
    {
      className: "file-row-top"
    }
  );

  const pathInput = h(
    "input",
    {
      className: "file-path",
      placeholder: "src/main.py",
      value: path
    }
  );

  const remove = h(
    "button",
    {
      type: "button",
      className: "remove-btn"
    },
    "Remove"
  );

  remove.onclick = () => row.remove();

  const textarea = h(
    "textarea",
    {
      className: "file-content",
      placeholder: "File content...",
      rows: 12
    }
  );

  textarea.value = content;

  top.append(
    pathInput,
    remove
  );

  row.append(
    top,
    textarea
  );

  $("files-list").appendChild(row);
}

function collectFiles() {
  return [
    ...document.querySelectorAll(
      ".file-row"
    )
  ]
    .map((row) => ({
      path: row
        .querySelector(".file-path")
        .value
        .trim(),

      content: row
        .querySelector(".file-content")
        .value
    }))
    .filter((file) => file.path);
}


/* ---------------- Submit ---------------- */

async function submitComponent(event) {
  event.preventDefault();

  const status = $("submit-status");
  const button = event.submitter;

  status.textContent = "";

  if (!authUser) {
    status.textContent =
      "Please sign in with GitHub first.";

    window.location.href =
      (C.AUTH_URL || "/auth")
        .replace(/\/$/, "") +
      "/login";

    return;
  }

  const files = collectFiles();

  const readme = files.find(
    (file) => file.path === "README.md"
  );

  const source = files.some(
    (file) =>
      file.path.startsWith("src/")
  );

  if (!readme) {
    status.textContent =
      "README.md is required.";

    return;
  }

  if (!source) {
    status.textContent =
      "At least one src/ file is required.";

    return;
  }

  button.disabled = true;
  button.textContent = "Submitting...";

  const payload = {
    name: $("component-name")
      .value
      .trim(),

    version: $("component-version")
      .value
      .trim(),

    description: $("component-description")
      .value
      .trim(),

    category: $("component-category")
      .value
      .trim()
      .toLowerCase(),

    runtime: $("component-runtime")
      .value
      .trim(),

    license: $("component-license")
      .value
      .trim(),

    tags: csvTags(
      $("component-tags").value
    ),

    dependencies:
      collectDependencies(),

    files
  };

  try {
    const response = await fetch(
      "/api/publisher/submit",
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type":
            "application/json",
          Accept:
            "application/json"
        },
        body: JSON.stringify(payload)
      }
    );

    const data =
      await response.json();

    if (!response.ok) {
      throw new Error(
        data.message ||
        data.error ||
        "Submission failed."
      );
    }

    status.textContent =
      "Submitted successfully. Pull Request created.";

    event.target.reset();

    $("dependencies-list")
      .replaceChildren();

    $("files-list")
      .replaceChildren();

    addDependency();
    addFile("README.md");
    addFile("src/main.py");

    if (data.pull_request) {
      const link =
        document.createElement("a");

      link.href =
        data.pull_request;

      link.target = "_blank";
      link.rel = "noopener";
      link.textContent =
        " Open Pull Request";

      status.appendChild(link);
    }
  } catch (error) {
    status.textContent =
      error.message ||
      "Could not submit component.";
  } finally {
    button.disabled = false;
    button.textContent =
      "Submit for Review";
  }
}


/* ---------------- Events ---------------- */

$("q").oninput = render;

$("submit-component").onclick = () => {
  location.hash = "/submit";
  route();
};

$("add-dependency").onclick = () => {
  addDependency();
};

$("add-file").onclick = () => {
  addFile();
};

$("submit-form").addEventListener(
  "submit",
  submitComponent
);

window.onhashchange = route;


/* ---------------- Initial files ---------------- */

addFile(
  "README.md",
  "# My Component\n\nDescribe your component here."
);

addFile(
  "src/main.py",
  "def main():\n    pass\n"
);

addDependency();


/* ---------------- Registry ---------------- */

fetch(
  C.REGISTRY_URL || "registry.json"
)
  .then((r) => {
    if (!r.ok) {
      throw new Error("registry");
    }

    return r.json();
  })
  .then((d) => {
    all = Array.isArray(d.components)
      ? d.components
      : [];

    render();
    route();
  })
  .catch(() => {
    $("grid").textContent =
      "Could not load registry.json. Serve over HTTP.";
  });

renderAuth();
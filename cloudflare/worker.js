// OPTIONAL GitHub OAuth adapter (Cloudflare Worker). Not needed by the core app.
// Secrets (wrangler secret put): GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, SESSION_SECRET. Var: SITE_URL.
// Serve it on the SAME site as the pages (e.g. route example.com/auth/*) so the cookie is first-party.
const enc = new TextEncoder();
const b64 = (b) => btoa(String.fromCharCode(...new Uint8Array(b))).replace(/[+/=]/g, (c) => ({ "+": "-", "/": "_", "=": "" })[c]);
async function sign(v, secret) {
  const k = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return b64(await crypto.subtle.sign("HMAC", k, enc.encode(v)));
}
const getC = (req, n) => (req.headers.get("Cookie") || "").split(/;\s*/).map((c) => c.split("=")).find((c) => c[0] === n)?.[1];
const setC = (n, v, age) => `${n}=${v}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${age}`;

export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    const path = u.pathname.replace(/^\/auth/, "");
    if (path === "/login") {
      const state = crypto.randomUUID();
      const to = new URL("https://github.com/login/oauth/authorize");
      to.search = new URLSearchParams({ client_id: env.GITHUB_CLIENT_ID, state, scope: "read:user" });
      return new Response(null, { status: 302, headers: { Location: to.href, "Set-Cookie": setC("st", state, 600) } });
    }
    if (path === "/callback") {
      const state = u.searchParams.get("state"), code = u.searchParams.get("code");
      if (!state || !code || state !== getC(req, "st")) return new Response("bad state", { status: 400 });
      const t = await (await fetch("https://github.com/login/oauth/access_token", {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ client_id: env.GITHUB_CLIENT_ID, client_secret: env.GITHUB_CLIENT_SECRET, code }),
      })).json();
      if (!t.access_token) return new Response("oauth failed", { status: 400 });
      const me = await (await fetch("https://api.github.com/user", {
        headers: { Authorization: `Bearer ${t.access_token}`, "User-Agent": "airegistry" },
      })).json();
      if (!me.login) return new Response("oauth failed", { status: 400 });
      const v = encodeURIComponent(me.login);
      return new Response(null, { status: 302, headers: { Location: env.SITE_URL, "Set-Cookie": setC("s", `${v}.${await sign(v, env.SESSION_SECRET)}`, 604800) } });
    }
    if (path === "/me") {
      const [v, sig] = (getC(req, "s") || "").split(".");
      if (!v || sig !== (await sign(v, env.SESSION_SECRET))) return new Response("{}", { status: 401 });
      return Response.json({ login: decodeURIComponent(v) });
    }
    return new Response("not found", { status: 404 });
  },
};

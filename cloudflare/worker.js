const enc = new TextEncoder();
const DECODER = new TextDecoder();

function b64url(bytes) {
  return btoa(String.fromCharCode(...new Uint8Array(bytes)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function b64urlDecode(value) {
  const padded = value.replace(/-/g, "+").replace(/_/g, "/")
    + "=".repeat((4 - (value.length % 4)) % 4);

  const raw = atob(padded);
  return Uint8Array.from(raw, c => c.charCodeAt(0));
}

async function hmacKey(secret) {
  return crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"]
  );
}

async function sign(value, secret) {
  const key = await hmacKey(secret);
  return b64url(
    await crypto.subtle.sign(
      "HMAC",
      key,
      enc.encode(value)
    )
  );
}

async function verify(value, signature, secret) {
  try {
    const key = await hmacKey(secret);
    return await crypto.subtle.verify(
      "HMAC",
      key,
      b64urlDecode(signature),
      enc.encode(value)
    );
  } catch {
    return false;
  }
}

async function pkceChallenge(verifier) {
  const digest = await crypto.subtle.digest(
    "SHA-256",
    enc.encode(verifier)
  );
  return b64url(digest);
}

function randomVerifier() {
  return b64url(crypto.getRandomValues(new Uint8Array(32)));
}

function getCookie(request, name) {
  const raw = request.headers.get("Cookie") || "";

  for (const part of raw.split(/;\s*/)) {
    const i = part.indexOf("=");

    if (i === -1) continue;

    const key = part.slice(0, i);
    const value = part.slice(i + 1);

    if (key === name) return value;
  }

  return "";
}

function cookie(name, value, maxAge) {
  return [
    `${name}=${value}`,
    "Path=/",
    "HttpOnly",
    "Secure",
    "SameSite=Lax",
    `Max-Age=${maxAge}`
  ].join("; ");
}

function clearCookie(name) {
  return `${name}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`;
}

function securityHeaders(headers = {}) {
  const h = new Headers(headers);

  h.set("X-Content-Type-Options", "nosniff");
  h.set("X-Frame-Options", "DENY");
  h.set("Referrer-Policy", "strict-origin-when-cross-origin");
  h.set("Permissions-Policy", "camera=(), microphone=(), geolocation=()");
  h.set(
    "Content-Security-Policy",
    "default-src 'self'; script-src 'self'; style-src 'self'; " +
    "connect-src 'self'; img-src 'self' data:; object-src 'none'; " +
    "base-uri 'none'; frame-ancestors 'none'"
  );

  return h;
}

function response(body, status = 200, headers = {}) {
  return new Response(body, {
    status,
    headers: securityHeaders(headers)
  });
}

function redirect(url, cookies = []) {
  const headers = securityHeaders({
    Location: url,
    "Cache-Control": "no-store"
  });

  for (const value of cookies) {
    headers.append("Set-Cookie", value);
  }

  return new Response(null, {
    status: 302,
    headers
  });
}

function authConfigured(env) {
  return Boolean(
    env.GITHUB_CLIENT_ID &&
    env.GITHUB_CLIENT_SECRET &&
    env.SESSION_SECRET &&
    env.SITE_URL &&
    env.GITHUB_REDIRECT_URI
  );
}

async function handleAuth(request, env) {
  const url = new URL(request.url);
  const path = url.pathname;

  if (!authConfigured(env)) {
    return response("Authentication is not configured.", 503, {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store"
    });
  }

  if (path === "/auth/login") {
    const state = crypto.randomUUID();
    const verifier = randomVerifier();
    const challenge = await pkceChallenge(verifier);

    const github = new URL(
      "https://github.com/login/oauth/authorize"
    );

    github.search = new URLSearchParams({
      client_id: env.GITHUB_CLIENT_ID,
      redirect_uri: env.GITHUB_REDIRECT_URI,
      state,
      code_challenge: challenge,
      code_challenge_method: "S256",
      scope: "read:user"
    });

    return redirect(github.href, [
      cookie("st", state, 600),
      cookie("pk", verifier, 600)
    ]);
  }

  if (path === "/auth/callback") {
    const state = url.searchParams.get("state");
    const code = url.searchParams.get("code");

    const storedState = getCookie(request, "st");
    const verifier = getCookie(request, "pk");

    if (
      !state ||
      !code ||
      !storedState ||
      !verifier ||
      state !== storedState
    ) {
      return response("Invalid OAuth state.", 400, {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-store"
      });
    }

    const tokenResponse = await fetch(
      "https://github.com/login/oauth/access_token",
      {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          client_id: env.GITHUB_CLIENT_ID,
          client_secret: env.GITHUB_CLIENT_SECRET,
          code,
          redirect_uri: env.GITHUB_REDIRECT_URI,
          code_verifier: verifier
        })
      }
    );

    if (!tokenResponse.ok) {
      return response("GitHub OAuth token exchange failed.", 502);
    }

    const token = await tokenResponse.json();

    if (!token.access_token) {
      return response("GitHub OAuth token missing.", 502);
    }

    const userResponse = await fetch(
      "https://api.github.com/user",
      {
        headers: {
          Authorization: `Bearer ${token.access_token}`,
          "User-Agent": "AIRegistry"
        }
      }
    );

    if (!userResponse.ok) {
      return response("GitHub user lookup failed.", 502);
    }

    const user = await userResponse.json();

    if (!user.login) {
      return response("GitHub identity unavailable.", 502);
    }

    const identity = encodeURIComponent(user.login);
    const expires = Math.floor(Date.now() / 1000) + 604800;
    const payload = `${identity}.${expires}`;
    const signature = await sign(payload, env.SESSION_SECRET);

    const session = `${payload}.${signature}`;

    return redirect(env.SITE_URL, [
      clearCookie("st"),
      clearCookie("pk"),
      cookie("s", session, 604800)
    ]);
  }

  if (path === "/auth/me") {
    const session = getCookie(request, "s");

    if (!session) {
      return response(
        JSON.stringify({ authenticated: false }),
        200,
        {
          "Content-Type": "application/json",
          "Cache-Control": "no-store"
        }
      );
    }

    const parts = session.split(".");

    if (parts.length !== 3) {
      return response(
        JSON.stringify({ authenticated: false }),
        200,
        {
          "Content-Type": "application/json",
          "Cache-Control": "no-store"
        }
      );
    }

    const identity = parts[0];
    const expires = Number(parts[1]);
    const signature = parts[2];

    if (
      !identity ||
      !Number.isSafeInteger(expires) ||
      expires <= Math.floor(Date.now() / 1000)
    ) {
      return response(
        JSON.stringify({ authenticated: false }),
        200,
        {
          "Content-Type": "application/json",
          "Cache-Control": "no-store"
        }
      );
    }

    const payload = `${identity}.${expires}`;

    const valid = await verify(
      payload,
      signature,
      env.SESSION_SECRET
    );

    if (!valid) {
      return response(
        JSON.stringify({ authenticated: false }),
        200,
        {
          "Content-Type": "application/json",
          "Cache-Control": "no-store"
        }
      );
    }

    return response(
      JSON.stringify({
        authenticated: true,
        login: decodeURIComponent(identity),
        expires
      }),
      200,
      {
        "Content-Type": "application/json",
        "Cache-Control": "no-store"
      }
    );
  }

  if (path === "/auth/logout") {
    return redirect(env.SITE_URL, [
      clearCookie("s")
    ]);
  }

  return response("Authentication endpoint not found.", 404, {
    "Content-Type": "text/plain; charset=utf-8",
    "Cache-Control": "no-store"
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname.startsWith("/auth/")) {
      return handleAuth(request, env);
    }

    return env.ASSETS.fetch(request);
  }
};
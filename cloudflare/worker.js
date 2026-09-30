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

function bytesToBase64Url(bytes) {
  return btoa(String.fromCharCode(...new Uint8Array(bytes)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function base64ToBytes(value) {
  const padded =
    value.replace(/-/g, "+").replace(/_/g, "/") +
    "=".repeat((4 - (value.length % 4)) % 4);

  const raw = atob(padded);

  return Uint8Array.from(raw, (c) => c.charCodeAt(0));
}

function derLength(length) {
  if (length < 128) return Uint8Array.of(length);

  const bytes = [];

  while (length > 0) {
    bytes.unshift(length & 255);
    length >>>= 8;
  }

  return Uint8Array.of(0x80 | bytes.length, ...bytes);
}

function derSequence(...parts) {
  const total = parts.reduce((n, p) => n + p.length, 0);
  const out = new Uint8Array(
    1 + derLength(total).length + total
  );

  let o = 0;

  out[o++] = 0x30;

  const len = derLength(total);
  out.set(len, o);
  o += len.length;

  for (const part of parts) {
    out.set(part, o);
    o += part.length;
  }

  return out;
}

function derIntegerZero() {
  return Uint8Array.of(0x02, 0x01, 0x00);
}

function derOidRsaEncryption() {
  return Uint8Array.of(
    0x30, 0x0d,
    0x06, 0x09,
    0x2a, 0x86, 0x48, 0x86, 0xf7, 0x0d, 0x01, 0x01, 0x01,
    0x05, 0x00
  );
}

function derOctetString(bytes) {
  const len = derLength(bytes.length);

  const out = new Uint8Array(
    1 + len.length + bytes.length
  );

  out[0] = 0x04;
  out.set(len, 1);
  out.set(bytes, 1 + len.length);

  return out;
}

function rsaPkcs1ToPkcs8(pkcs1) {
  return derSequence(
    derIntegerZero(),
    derOidRsaEncryption(),
    derOctetString(pkcs1)
  );
}

function pemToDer(pem) {
  const clean = pem
    .replace(/\\n/g, "\n")
    .replace(/-----BEGIN [^-]+-----/g, "")
    .replace(/-----END [^-]+-----/g, "")
    .replace(/\s+/g, "");

  return base64ToBytes(clean);
}

async function importGitHubPrivateKey(pem) {
  const der = pemToDer(pem);

  const isPkcs1 =
    pem.includes("BEGIN RSA PRIVATE KEY");

  const pkcs8 = isPkcs1
    ? rsaPkcs1ToPkcs8(der)
    : der;

  return crypto.subtle.importKey(
    "pkcs8",
    pkcs8,
    {
      name: "RSASSA-PKCS1-v1_5",
      hash: "SHA-256"
    },
    false,
    ["sign"]
  );
}

async function createGitHubAppJwt(env) {
  if (
    !env.GITHUB_APP_ID ||
    !env.GITHUB_APP_PRIVATE_KEY
  ) {
    throw new Error("GitHub App credentials are missing.");
  }

  const now = Math.floor(Date.now() / 1000);

  const header = bytesToBase64Url(
    new TextEncoder().encode(
      JSON.stringify({
        alg: "RS256",
        typ: "JWT"
      })
    )
  );

  const payload = bytesToBase64Url(
    new TextEncoder().encode(
      JSON.stringify({
        iat: now - 60,
        exp: now + 540,
        iss: String(env.GITHUB_APP_ID)
      })
    )
  );

  const message = `${header}.${payload}`;

  const key = await importGitHubPrivateKey(
    env.GITHUB_APP_PRIVATE_KEY
  );

  const signature = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5",
    key,
    new TextEncoder().encode(message)
  );

  return `${message}.${bytesToBase64Url(signature)}`;
}

async function githubApi(path, options = {}) {
  const headers = new Headers(options.headers || {});

  headers.set(
    "Accept",
    "application/vnd.github+json"
  );

  headers.set(
    "X-GitHub-Api-Version",
    "2026-03-10"
  );

  headers.set(
    "User-Agent",
    "AIRegistry"
  );

  return fetch(
    `https://api.github.com${path}`,
    {
      ...options,
      headers
    }
  );
}

async function getInstallationToken(env) {
  const jwt = await createGitHubAppJwt(env);

  const response = await githubApi(
    `/app/installations/${encodeURIComponent(
      env.GITHUB_APP_INSTALLATION_ID
    )}/access_tokens`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${jwt}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        repositories: [env.GITHUB_REPO_NAME],
        permissions: {
          contents: "write",
          pull_requests: "write"
        }
      })
    }
  );

  if (!response.ok) {
    const text = await response.text();

    throw new Error(
      `GitHub installation token failed (${response.status}): ${text.slice(0, 300)}`
    );
  }

  const data = await response.json();

  if (!data.token) {
    throw new Error(
      "GitHub installation token was not returned."
    );
  }

  return data.token;
}

async function getAuthenticatedAiRegistryUser(
  request,
  env
) {
  const session = getCookie(request, "s");

  if (!session) return null;

  const parts = session.split(".");

  if (parts.length !== 3) return null;

  const identity = parts[0];
  const expires = Number(parts[1]);
  const signature = parts[2];

  if (
    !identity ||
    !Number.isSafeInteger(expires) ||
    expires <= Math.floor(Date.now() / 1000)
  ) {
    return null;
  }

  const valid = await verify(
    `${identity}.${expires}`,
    signature,
    env.SESSION_SECRET
  );

  if (!valid) return null;

  return {
    login: decodeURIComponent(identity),
    expires
  };
}

async function handlePublisherStatus(request, env) {
  const user =
    await getAuthenticatedAiRegistryUser(
      request,
      env
    );

  if (!user) {
    return response(
      JSON.stringify({
        error: "authentication_required"
      }),
      401,
      {
        "Content-Type": "application/json",
        "Cache-Control": "no-store"
      }
    );
  }

  if (
    !env.GITHUB_APP_ID ||
    !env.GITHUB_APP_INSTALLATION_ID ||
    !env.GITHUB_APP_PRIVATE_KEY ||
    !env.GITHUB_REPO_OWNER ||
    !env.GITHUB_REPO_NAME
  ) {
    return response(
      JSON.stringify({
        error: "publisher_not_configured"
      }),
      503,
      {
        "Content-Type": "application/json",
        "Cache-Control": "no-store"
      }
    );
  }

  try {
    const token =
      await getInstallationToken(env);

    const repo = await githubApi(
      `/repos/${encodeURIComponent(
        env.GITHUB_REPO_OWNER
      )}/${encodeURIComponent(
        env.GITHUB_REPO_NAME
      )}`,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    );

    if (!repo.ok) {
      return response(
        JSON.stringify({
          error: "repository_access_failed",
          status: repo.status
        }),
        502,
        {
          "Content-Type": "application/json",
          "Cache-Control": "no-store"
        }
      );
    }

    const data = await repo.json();

    return response(
      JSON.stringify({
        ok: true,
        user: user.login,
        repository: `${env.GITHUB_REPO_OWNER}/${env.GITHUB_REPO_NAME}`,
        app_access: true,
        default_branch: data.default_branch
      }),
      200,
      {
        "Content-Type": "application/json",
        "Cache-Control": "no-store"
      }
    );
  } catch (error) {
    return response(
      JSON.stringify({
        error: "publisher_check_failed",
        message: String(error.message || error)
          .slice(0, 300)
      }),
      502,
      {
        "Content-Type": "application/json",
        "Cache-Control": "no-store"
      }
    );
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname.startsWith("/auth/")) {
  	return handleAuth(request, env);
	}

    if (url.pathname === "/api/publisher/status") {
  	return handlePublisherStatus(request, env);
	}

    return env.ASSETS.fetch(request);
  }
};
const enc = new TextEncoder();

const b64 = (bytes) =>
  btoa(String.fromCharCode(...new Uint8Array(bytes)))
    .replace(/[+/=]/g, (c) => ({ "+": "-", "/": "_", "=": "" })[c]);

async function sign(value, secret) {
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );

  return b64(await crypto.subtle.sign("HMAC", key, enc.encode(value)));
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

function redirect(url, cookies = []) {
  const headers = new Headers({ Location: url });

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
    return new Response("Authentication is not configured.", {
      status: 503,
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }

  if (path === "/auth/login") {
    const state = crypto.randomUUID();

    const github = new URL(
      "https://github.com/login/oauth/authorize"
    );

    github.search = new URLSearchParams({
      client_id: env.GITHUB_CLIENT_ID,
      redirect_uri: env.GITHUB_REDIRECT_URI,
      state,
      scope: "read:user"
    });

    return redirect(github.href, [
      cookie("st", state, 600)
    ]);
  }

  if (path === "/auth/callback") {
    const state = url.searchParams.get("state");
    const code = url.searchParams.get("code");

    const storedState = getCookie(request, "st");

    if (!state || !code || !storedState || state !== storedState) {
      return new Response("Invalid OAuth state.", {
        status: 400
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
          redirect_uri: env.GITHUB_REDIRECT_URI
        })
      }
    );

    if (!tokenResponse.ok) {
      return new Response("GitHub OAuth token exchange failed.", {
        status: 502
      });
    }

    const token = await tokenResponse.json();

    if (!token.access_token) {
      return new Response("GitHub OAuth token missing.", {
        status: 502
      });
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
      return new Response("GitHub user lookup failed.", {
        status: 502
      });
    }

    const user = await userResponse.json();

    if (!user.login) {
      return new Response("GitHub identity unavailable.", {
        status: 502
      });
    }

    const identity = encodeURIComponent(user.login);
    const signature = await sign(
      identity,
      env.SESSION_SECRET
    );

    const session = `${identity}.${signature}`;

    return redirect(env.SITE_URL, [
      clearCookie("st"),
      cookie("s", session, 604800)
    ]);
  }

  if (path === "/auth/me") {
    const session = getCookie(request, "s");

    if (!session) {
      return new Response(
        JSON.stringify({ authenticated: false }),
        {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Cache-Control": "no-store"
          }
        }
      );
    }

    const dot = session.lastIndexOf(".");

    if (dot <= 0) {
      return new Response(
        JSON.stringify({ authenticated: false }),
        {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Cache-Control": "no-store"
          }
        }
      );
    }

    const identity = session.slice(0, dot);
    const signature = session.slice(dot + 1);

    const expected = await sign(
      identity,
      env.SESSION_SECRET
    );

    if (signature !== expected) {
      return new Response(
        JSON.stringify({ authenticated: false }),
        {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Cache-Control": "no-store"
          }
        }
      );
    }

    return new Response(
      JSON.stringify({
        authenticated: true,
        login: decodeURIComponent(identity)
      }),
      {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Cache-Control": "no-store"
        }
      }
    );
  }

  if (path === "/auth/logout") {
    return redirect(env.SITE_URL, [
      clearCookie("s")
    ]);
  }

  return new Response("Authentication endpoint not found.", {
    status: 404
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
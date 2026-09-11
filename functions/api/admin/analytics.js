function verifyAdminAuth(request) {
  const authHeader = request.headers.get("Authorization");
  if (authHeader && authHeader.startsWith("Basic ")) {
    try {
      const decoded = atob(authHeader.substring(6));
      const [user, pass] = decoded.split(":");
      if (user === "user" && pass === "hacker") {
        return true;
      }
    } catch (e) {
      // Invalid base64
    }
  }

  // Fallback to query params
  const url = new URL(request.url);
  const u = url.searchParams.get("u");
  const p = url.searchParams.get("p");
  if (u === "user" && p === "hacker") {
    return true;
  }

  return false;
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}

export async function onRequestGet(context) {
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
  };

  if (!verifyAdminAuth(context.request)) {
    return new Response(JSON.stringify({ error: "Unauthorized. Admin credentials required." }), {
      status: 401,
      headers: {
        ...corsHeaders,
        "WWW-Authenticate": 'Basic realm="Bubbsy Admin Area"',
      },
    });
  }

  try {
    let clicks = [];
    let totalClicks = 0;
    let uniqueSessions = 0;
    let topTargets = [];

    if (context.env && context.env.DB) {
      await context.env.DB.prepare(`
        CREATE TABLE IF NOT EXISTS clicks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          session_id TEXT NOT NULL,
          element_tag TEXT,
          element_id TEXT,
          element_classes TEXT,
          element_text TEXT,
          target_href TEXT,
          page_path TEXT,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
          ip TEXT,
          country TEXT,
          user_agent TEXT
        )
      `).run();

      const totalRes = await context.env.DB.prepare("SELECT COUNT(*) as count FROM clicks").first();
      totalClicks = totalRes ? totalRes.count : 0;

      const sessionsRes = await context.env.DB.prepare("SELECT COUNT(DISTINCT session_id) as count FROM clicks").first();
      uniqueSessions = sessionsRes ? sessionsRes.count : 0;

      const topRes = await context.env.DB.prepare(`
        SELECT 
          COALESCE(NULLIF(target_href, ''), element_text, element_id) as target,
          COUNT(*) as count
        FROM clicks
        WHERE target IS NOT NULL AND target != ''
        GROUP BY target
        ORDER BY count DESC
        LIMIT 6
      `).all();
      topTargets = topRes ? (topRes.results || []) : [];

      const clicksRes = await context.env.DB.prepare(`
        SELECT id, session_id, element_tag, element_id, element_classes, element_text, target_href, page_path, timestamp, ip, country, user_agent
        FROM clicks
        ORDER BY id DESC
        LIMIT 250
      `).all();
      clicks = clicksRes ? (clicksRes.results || []) : [];
    }

    return new Response(
      JSON.stringify({
        authorized: true,
        summary: {
          total_clicks: totalClicks,
          unique_sessions: uniqueSessions,
          top_targets: topTargets,
        },
        clicks,
      }),
      { status: 200, headers: corsHeaders }
    );
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: corsHeaders,
    });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

export async function onRequestPost(context) {
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
  };

  try {
    const payload = await context.request.json();
    const req = context.request;
    const ip = req.headers.get("cf-connecting-ip") || req.headers.get("x-forwarded-for") || "127.0.0.1";
    const country = req.headers.get("cf-ipcountry") || "AU";
    const userAgent = (req.headers.get("user-agent") || "").slice(0, 250);

    const sessionId = payload.session_id || "anonymous";
    const elementTag = payload.element_tag || "";
    const elementId = payload.element_id || "";
    const elementClasses = payload.element_classes || "";
    const elementText = (payload.element_text || "").slice(0, 200);
    const targetHref = payload.target_href || "";
    const pagePath = payload.page_path || "/";
    const timestamp = payload.timestamp || new Date().toISOString();

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

      await context.env.DB.prepare(`
        INSERT INTO clicks (
          session_id, element_tag, element_id, element_classes, element_text, target_href, page_path, timestamp, ip, country, user_agent
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        sessionId,
        elementTag,
        elementId,
        elementClasses,
        elementText,
        targetHref,
        pagePath,
        timestamp,
        ip,
        country,
        userAgent
      ).run();
    }

    return new Response(JSON.stringify({ success: true, timestamp }), {
      status: 200,
      headers: corsHeaders,
    });
  } catch (err) {
    return new Response(JSON.stringify({ success: false, error: err.message }), {
      status: 400,
      headers: corsHeaders,
    });
  }
}

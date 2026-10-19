/**
 * GET /api/admin/analytics: click analytics for the site owner.
 * Access: the ADMIN_PASSWORD secret (see lib/cf-accounts.js). Off when the secret is unset.
 */
import { requireAdmin } from "../../../lib/cf-accounts.js";

export async function onRequestGet(context) {
  const corsHeaders = {
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
  };

  const denied = await requireAdmin(context.request, context.env || {});
  if (denied) return denied;

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

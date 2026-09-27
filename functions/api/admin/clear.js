/**
 * POST /api/admin/clear: delete all click analytics. Site owner only (ADMIN_PASSWORD secret).
 */
import { requireAdmin } from "../../../lib/cf-accounts.js";

export async function onRequestPost(context) {
  const corsHeaders = {
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
  };

  const denied = await requireAdmin(context.request, context.env || {});
  if (denied) return denied;

  try {
    if (context.env && context.env.DB) {
      await context.env.DB.prepare("DELETE FROM clicks").run();
    }
    return new Response(JSON.stringify({ success: true, message: "Analytics logs cleared" }), {
      status: 200,
      headers: corsHeaders,
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: corsHeaders,
    });
  }
}

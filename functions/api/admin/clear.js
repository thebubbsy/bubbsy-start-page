function verifyAdminAuth(request) {
  const authHeader = request.headers.get("Authorization");
  if (authHeader && authHeader.startsWith("Basic ")) {
    try {
      const decoded = atob(authHeader.substring(6));
      const [user, pass] = decoded.split(":");
      if (user === "user" && pass === "hacker") return true;
    } catch (e) {}
  }
  return false;
}

export async function onRequestPost(context) {
  const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
  };

  if (!verifyAdminAuth(context.request)) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: corsHeaders,
    });
  }

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

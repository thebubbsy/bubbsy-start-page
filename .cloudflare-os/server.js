import { DurableObject } from "cloudflare:workers";

export class BubbsyDashboardGadget extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.ctx = ctx;
  }

  async fetch(request) {
    return new Response("Bubbsy Start Page Cloudflare-OS Workspace Ready", { status: 200 });
  }
}

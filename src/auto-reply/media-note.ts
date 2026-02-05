import type { MsgContext } from "./templating.js";

function formatMediaAttachedLine(params: {
  path: string;
  url?: string;
  type?: string;
  index?: number;
  total?: number;
}): string {
  const prefix =
    typeof params.index === "number" && typeof params.total === "number"
      ? `[media attached ${params.index}/${params.total}: `
      : "[media attached: ";
  const typePart = params.type?.trim() ? ` (${params.type.trim()})` : "";
  const urlRaw = params.url?.trim();
  const urlPart = urlRaw ? ` | ${urlRaw}` : "";
  return `${prefix}${params.path}${typePart}${urlPart}]`;
}

export function buildInboundMediaNote(ctx: MsgContext): string | undefined {
  // Attachment indices follow MediaPaths/MediaUrls ordering as supplied by the channel.
  const suppressed = new Set<number>();
  if (Array.isArray(ctx.MediaUnderstanding)) {
    for (const output of ctx.MediaUnderstanding) {
      suppressed.add(output.attachmentIndex);
    }
  }
  if (Array.isArray(ctx.MediaUnderstandingDecisions)) {
    for (const decision of ctx.MediaUnderstandingDecisions) {
      if (decision.outcome !== "success") {
        continue;
      }
      for (const attachment of decision.attachments) {
        if (attachment.chosen?.outcome === "success") {
          suppressed.add(attachment.attachmentIndex);
        }
      }
    }
  }
  const pathsFromArray = Array.isArray(ctx.MediaPaths) ? ctx.MediaPaths : undefined;
  const paths =
    pathsFromArray && pathsFromArray.length > 0
      ? pathsFromArray
      : ctx.MediaPath?.trim()
        ? [ctx.MediaPath.trim()]
        : [];
  // eslint-disable-next-line no-console
  console.log(`[IMG-DIAG] Step 3: buildInboundMediaNote — MediaPath=${ctx.MediaPath ?? "undefined"}, paths=[${paths.join(",")}], suppressed=[${[...suppressed].join(",")}], MediaUnderstanding=${Array.isArray(ctx.MediaUnderstanding) ? ctx.MediaUnderstanding.length : 0} outputs, decisions=${Array.isArray(ctx.MediaUnderstandingDecisions) ? ctx.MediaUnderstandingDecisions.map(d => `${d.capability}:${d.outcome}`).join(",") : "none"}`);
  if (paths.length === 0) {
    // eslint-disable-next-line no-console
    console.log(`[IMG-DIAG] Step 3: No paths found — mediaNote will be UNDEFINED (no image path in prompt!)`);
    return undefined;
  }

  const urls =
    Array.isArray(ctx.MediaUrls) && ctx.MediaUrls.length === paths.length
      ? ctx.MediaUrls
      : undefined;
  const types =
    Array.isArray(ctx.MediaTypes) && ctx.MediaTypes.length === paths.length
      ? ctx.MediaTypes
      : undefined;

  const entries = paths
    .map((entry, index) => ({
      path: entry ?? "",
      type: types?.[index] ?? ctx.MediaType,
      url: urls?.[index] ?? ctx.MediaUrl,
      index,
    }))
    .filter((entry) => !suppressed.has(entry.index));
  if (entries.length === 0) {
    // eslint-disable-next-line no-console
    console.log(`[IMG-DIAG] Step 3: All entries suppressed (already handled by media understanding) — mediaNote=undefined`);
    return undefined;
  }
  if (entries.length === 1) {
    const note = formatMediaAttachedLine({
      path: entries[0]?.path ?? "",
      type: entries[0]?.type,
      url: entries[0]?.url,
    });
    // eslint-disable-next-line no-console
    console.log(`[IMG-DIAG] Step 3: mediaNote="${note}"`);
    return note;
  }

  const count = entries.length;
  const lines: string[] = [`[media attached: ${count} files]`];
  for (const [idx, entry] of entries.entries()) {
    lines.push(
      formatMediaAttachedLine({
        path: entry.path,
        index: idx + 1,
        total: count,
        type: entry.type,
        url: entry.url,
      }),
    );
  }
  const note = lines.join("\n");
  // eslint-disable-next-line no-console
  console.log(`[IMG-DIAG] Step 3: mediaNote (multi)="${note.slice(0, 200)}"`);
  return note;
}

/**
 * Model/provider configuration for the VoltAgent agent.
 *
 * The LLM provider is NOT hard-coded. `resolveModel` picks a real provider from
 * environment variables when configured, and otherwise falls back to a
 * deterministic, offline model so the demo, tests, and Docker E2E run with no
 * paid API. MCC-Core governance is entirely independent of which model is used —
 * the model only chooses what to *propose*.
 *
 * Environment:
 *   MCC_VOLTAGENT_MODEL_PROVIDER   e.g. "openai" (omit/"deterministic" -> offline)
 *   MCC_VOLTAGENT_MODEL            model id, e.g. "gpt-4o-mini"
 *   OPENAI_API_KEY                 required for the openai provider
 */

import type { LanguageModelV3CallOptions, LanguageModelV3GenerateResult } from "@ai-sdk/provider";
import { MockLanguageModelV3 } from "ai/test";
import { GOVERNED_TOOL_NAME } from "./tools/governed-notification.js";

interface ParsedRequest {
  recipient: string;
  message: string;
  priority: "low" | "normal" | "high" | "urgent";
  channel: "email" | "sms" | "pager";
}

/** Deterministically parse a natural-language request into notification args. */
export function parseNotificationRequest(text: string): ParsedRequest {
  const t = text.trim();
  const recipientMatch = t.match(/\b([A-Za-z][\w-]*-\d+|customer[\w-]*)\b/);
  const recipient = recipientMatch?.[1] ?? "customer-000";
  const afterThat = t.split(/\bthat\b/i);
  const message = (afterThat.length > 1 ? afterThat.slice(1).join("that").trim() : t) || t;

  let priority: ParsedRequest["priority"] = "normal";
  if (/\burgent|critical|asap|immediately\b/i.test(t)) priority = "urgent";
  else if (/\bhigh[- ]?priority|high\b/i.test(t)) priority = "high";
  else if (/\blow[- ]?priority|low\b/i.test(t)) priority = "low";

  let channel: ParsedRequest["channel"] = "email";
  if (/\bpager|page\b/i.test(t)) channel = "pager";
  else if (/\bsms|text message\b/i.test(t)) channel = "sms";

  return { recipient, message, priority, channel };
}

// -- prompt helpers (Vercel AI SDK v6 LanguageModelV3 prompt shape) ---------- //

function extractUserText(prompt: unknown): string {
  if (!Array.isArray(prompt)) return "";
  const parts: string[] = [];
  for (const msg of prompt as Array<{ role?: string; content?: unknown }>) {
    if (msg.role !== "user") continue;
    if (typeof msg.content === "string") {
      parts.push(msg.content);
    } else if (Array.isArray(msg.content)) {
      for (const p of msg.content as Array<{ type?: string; text?: string }>) {
        if (p.type === "text" && typeof p.text === "string") parts.push(p.text);
      }
    }
  }
  return parts.join("\n");
}

function hasToolResult(prompt: unknown): boolean {
  if (!Array.isArray(prompt)) return false;
  return (prompt as Array<{ role?: string }>).some((m) => m.role === "tool");
}

/**
 * A deterministic model: it emits exactly one governed-notification tool call
 * derived from the user's request, then (once a tool result is present) a short
 * final summary. No network, no key, fully reproducible.
 */
export function createDeterministicModel(): MockLanguageModelV3 {
  const usage: LanguageModelV3GenerateResult["usage"] = {
    inputTokens: { total: 1, noCache: undefined, cacheRead: undefined, cacheWrite: undefined },
    outputTokens: { total: 1, text: 1, reasoning: undefined },
  };
  const finish = (
    unified: "stop" | "tool-calls",
  ): LanguageModelV3GenerateResult["finishReason"] => ({
    unified,
    raw: undefined,
  });

  const doGenerate = async (
    options: LanguageModelV3CallOptions,
  ): Promise<LanguageModelV3GenerateResult> => {
    if (hasToolResult(options.prompt)) {
      return {
        content: [
          {
            type: "text",
            text: "The notification has been submitted to MCC-Core for governance; see the governed result.",
          },
        ],
        finishReason: finish("stop"),
        usage,
        warnings: [],
      };
    }
    const args = parseNotificationRequest(extractUserText(options.prompt));
    return {
      content: [
        {
          type: "tool-call",
          toolCallId: `call-${Math.random().toString(36).slice(2, 10)}`,
          toolName: GOVERNED_TOOL_NAME,
          input: JSON.stringify(args),
        },
      ],
      finishReason: finish("tool-calls"),
      usage,
      warnings: [],
    };
  };
  return new MockLanguageModelV3({ doGenerate });
}

/**
 * Resolve the model for the agent. Uses a configured real provider when present,
 * otherwise the deterministic offline model. Never throws for a missing provider
 * — it degrades to deterministic so governance is always exercisable.
 */
export async function resolveModel(
  env: NodeJS.ProcessEnv = process.env,
): Promise<{ model: unknown; provider: string }> {
  const provider = (env.MCC_VOLTAGENT_MODEL_PROVIDER ?? "deterministic").trim().toLowerCase();

  if (provider === "openai") {
    const apiKey = env.OPENAI_API_KEY;
    if (!apiKey) {
      throw new Error("MCC_VOLTAGENT_MODEL_PROVIDER=openai but OPENAI_API_KEY is not set");
    }
    const modelId = env.MCC_VOLTAGENT_MODEL ?? "gpt-4o-mini";
    // Dynamic import so the (optional) provider is not required for the default
    // deterministic path, tests, or CI.
    const { createOpenAI } = await import("@ai-sdk/openai");
    const openai = createOpenAI({ apiKey });
    return { model: openai(modelId), provider: `openai:${modelId}` };
  }

  return { model: createDeterministicModel(), provider: "deterministic" };
}

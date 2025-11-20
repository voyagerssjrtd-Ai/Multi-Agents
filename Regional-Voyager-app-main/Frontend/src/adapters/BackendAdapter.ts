// src/adapters/BackendAdapter.ts
import { ChatBackend, Message } from "../types/chat";

const API_URL = "http://localhost:8000/chat";

export const BackendAdapter: ChatBackend = {
  sendMessage: async (content: string): Promise<Message> => {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: content })
    });

    const data = await response.json();
    let formatted: string;

    // 1️⃣ If backend returns array (DB rows)
    if (Array.isArray(data.response)) {
      formatted = "### Results\n\n" + data.response
        .map((row: any) =>
          Object.entries(row)
            .map(([k, v]) => `**${k}:** ${v}`)
            .join(" | ")
        )
        .join("\n");
    }

    // 2️⃣ If response already string → use directly
    else if (typeof data.response === "string") {
      formatted = data.response;
    }

    // 3️⃣ Otherwise convert cleanly
    else {
      formatted = "```json\n" + JSON.stringify(data.response, null, 2) + "\n```";
    }

    return {
      id: Date.now().toString(),
      role: "assistant",
      content: formatted,
      createdAt: new Date().toISOString(),
    };
  }
};

// src/components/MarkdownMessage.tsx
import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import DOMPurify from "dompurify";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

export default function MarkdownMessage({ content }: { content: string }) {
  if (!content) return null;

  // 🔥 COMPLETE PROTECTION AGAINST SVG CRASH
  const sanitized = DOMPurify.sanitize(content, {
    USE_PROFILES: { html: true },
    FORBID_TAGS: ["svg", "path", "script", "iframe"],
    FORBID_ATTR: ["d"], // this prevents <path d="undefined">
  });

  return (
    <div className="prose prose-sm max-w-none text-gray-800">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ inline, className, children, ...rest }: any) {
            const match = /language-(\w+)/.exec(className || "");
            return !inline && match ? (
              <SyntaxHighlighter
                style={oneDark}
                language={match[1]}
                PreTag="div"
                className="rounded-lg p-2 text-sm"
                {...rest}
              >
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            ) : (
              <code className="bg-gray-200 px-1 py-0.5 rounded text-sm" {...rest}>
                {children}
              </code>
            );
          },
        }}
      >
        {sanitized}
      </ReactMarkdown>
    </div>
  );
}

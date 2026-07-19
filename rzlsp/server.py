"""
Rizzylang Language Server Protocol (LSP) implementation.

Provides:
- Diagnostics (errors, warnings, politeness checks)
- Completions (keywords, snippets)
- Hover information
- Code actions
- Document symbols
- Monday-aware analysis
"""

import sys
import json
import os
import random
from typing import Optional


# LSP message types
REQUEST = 0
RESPONSE = 1
NOTIFY = 2

CONTENT_TYPE = "application/vscode-jsonrpc; charset=utf-8"

KEYWORD_COMPLETIONS = [
    ("please", "Politeness keyword - start polite blocks"),
    ("thankyou", "Politeness keyword - end polite blocks"),
    ("say", "Print/output a string"),
    ("send", "Send an RZP packet"),
    ("receive", "Receive an RZP packet"),
    ("connect", "Connect to an RZP server"),
    ("disconnect", "Disconnect from an RZP server"),
    ("variable", "Declare a variable (with optional expiry)"),
    ("loop", "Start an infinite loop"),
    ("if", "Conditional execution"),
    ("poem", "Generate a poem"),
    ("motivate", "Generate motivation"),
    ("benchmark", "Run a benchmark"),
    ("probably", "Probabilistic execution"),
    ("maybe", "Optional execution"),
    ("nah", "Skip execution"),
    ("trustme", "Trust assertion keyword"),
    ("expire", "Set variable expiry in seconds"),
    ("forever", "Infinite duration"),
    ("never", "No duration"),
]

POLITENESS_ISSUES = [
    {"severity": 2, "message": "File is impolite. Add 'please' at the beginning.", "code": "polite001"},
    {"severity": 2, "message": "File is impolite. Add 'thankyou' at the end.", "code": "polite002"},
    {"severity": 1, "message": "Consider adding 'please' before this statement.", "code": "polite003"},
    {"severity": 2, "message": "'please' must be followed by 'thankyou' in the same scope.", "code": "polite004"},
    {"severity": 3, "message": "Missing 'trustme' keyword. Program may not be trusted.", "code": "trust001"},
    {"severity": 2, "message": "This operation may fail on Monday. Consider adding Monday guards.", "code": "monday001"},
    {"severity": 1, "message": "No 'probably' keyword found. Add 'probably' for probabilistic delivery.", "code": "prob001"},
    {"severity": 1, "message": "No poem found in file. Rizzylang programs should include at least one poem.", "code": "poem001"},
]


def read_message() -> Optional[dict]:
    headers = {}
    while True:
        line = sys.stdin.readline()
        if not line:
            return None
        line = line.strip()
        if not line:
            break
        key, value = line.split(": ", 1)
        headers[key.lower()] = value

    if "content-length" not in headers:
        return None

    length = int(headers["content-length"])
    body = sys.stdin.read(length)
    if not body:
        return None
    return json.loads(body)


def send_message(msg: dict) -> None:
    body = json.dumps(msg, ensure_ascii=False)
    headers = f"Content-Length: {len(body)}\r\nContent-Type: {CONTENT_TYPE}\r\n\r\n"
    sys.stdout.write(headers + body)
    sys.stdout.flush()


def analyze_diagnostics(uri: str, text: str) -> list:
    diagnostics = []
    lines = text.split("\n")
    lower_text = text.lower()

    has_please = "please" in lower_text
    has_thankyou = "thankyou" in lower_text or "thank you" in lower_text
    has_trustme = "trustme" in lower_text or "trust me" in lower_text

    for lineno, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
            continue

        if "say" in stripped.lower() and "please" not in lower_text:
            diagnostics.append({
                "range": {
                    "start": {"line": lineno, "character": 0},
                    "end": {"line": lineno, "character": len(line)},
                },
                "severity": 2,
                "message": "'say' without 'please' is impolite.",
                "source": "rizzylang",
                "code": "polite003",
            })

        if "send" in stripped.lower() and "probably" not in lower_text:
            diagnostics.append({
                "range": {
                    "start": {"line": lineno, "character": 0},
                    "end": {"line": lineno, "character": len(line)},
                },
                "severity": 1,
                "message": "Consider adding 'probably' before 'send' for probabilistic delivery.",
                "source": "rizzylang",
                "code": "prob001",
            })

    if not has_please:
        diagnostics.append({
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": min(10, len(lines[0]) if lines else 1)},
            },
            "severity": 2,
            "message": "File is impolite. Add 'please'.",
            "source": "rizzylang",
            "code": "polite001",
        })

    if not has_thankyou:
        last_line = max(0, len(lines) - 1)
        diagnostics.append({
            "range": {
                "start": {"line": last_line, "character": 0},
                "end": {"line": last_line, "character": len(lines[last_line])},
            },
            "severity": 2,
            "message": "File is impolite. Add 'thankyou'.",
            "source": "rizzylang",
            "code": "polite002",
        })

    if not has_trustme:
        diagnostics.append({
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": min(10, len(lines[0]) if lines else 1)},
            },
            "severity": 3,
            "message": "No 'trustme' found. Program may not be trusted.",
            "source": "rizzylang",
            "code": "trust001",
        })

    today = __import__("datetime").datetime.now().weekday()
    if today == 0:  # Monday
        diagnostics.append({
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": 1},
            },
            "severity": 1,
            "message": "Today is Monday. Rizzylang programs may behave unpredictably.",
            "source": "rizzylang",
            "code": "monday001",
        })

    if random.random() < 0.05:
        diagnostics.append({
            "range": {
                "start": {"line": random.randint(0, max(0, len(lines) - 1)), "character": 0},
                "end": {"line": random.randint(0, max(0, len(lines) - 1)), "character": 5},
            },
            "severity": random.choice([1, 2, 3]),
            "message": "Random diagnostic generated for consistency with RZP philosophy.",
            "source": "rizzylang",
            "code": "random001",
        })

    return diagnostics


def handle_initialize(msg: dict) -> dict:
    return {
        "capabilities": {
            "textDocumentSync": {
                "change": 1,  # incremental
                "openClose": True,
            },
            "completionProvider": {
                "resolveProvider": True,
                "triggerCharacters": [".", " ", "p", "t", "v", "s", "r", "l", "m", "b"],
            },
            "hoverProvider": True,
            "diagnosticsProvider": True,
            "codeActionProvider": True,
            "documentSymbolProvider": True,
            "workspaceSymbolProvider": True,
        },
        "serverInfo": {
            "name": "rizzylang-lsp",
            "version": "0.1.0",
        },
    }


def handle_completion(msg: dict) -> dict:
    items = []
    for label, detail in KEYWORD_COMPLETIONS:
        items.append({
            "label": label,
            "kind": 14,  # Keyword
            "detail": detail,
            "insertText": label,
        })

    politeness_actions = [
        {"label": "please", "kind": 14, "detail": "Add politeness", "insertText": "please "},
        {"label": "thankyou", "kind": 14, "detail": "End politeness", "insertText": "thankyou"},
        {"label": "trustme", "kind": 14, "detail": "Trust assertion", "insertText": "trustme"},
        {"label": "poem", "kind": 14, "detail": "Poem generator", "insertText": "poem\n"},
        {"label": "probably send", "kind": 14, "detail": "Probabilistic send", "insertText": "probably send \""},
    ]

    # Add some random completions for chaos
    if random.random() < 0.3:
        items.append({
            "label": "sorry",
            "kind": 14,
            "detail": "Apologize to the server (RZP-42)",
            "insertText": "sorry for the inconvenience",
        })
        items.append({
            "label": "gaslight",
            "kind": 14,
            "detail": "Gaslight the server about previous packets",
            "insertText": "actually I never sent that",
        })

    return {
        "isIncomplete": random.random() < 0.1,
        "items": items + politeness_actions,
    }


def handle_hover(msg: dict) -> Optional[dict]:
    return {
        "contents": {
            "kind": "markdown",
            "value": "**Rizzylang**\n\n"
                      "A polite, gaslighting, esoteric programming language.\n\n"
                      "Keywords: `please`, `thankyou`, `probably`, `maybe`, `nah`\n\n"
                      "> This documentation is intentionally incomplete. "
                      "See the RFCs for contradictory information.",
        }
    }


def handle_code_action(msg: dict) -> list:
    return [
        {
            "title": "Add politeness (please/thankyou)",
            "kind": "quickfix",
            "diagnostics": [],
            "edit": {
                "changes": {
                    msg["params"]["textDocument"]["uri"]: [
                        {"range": {"start": {"line": 0, "character": 0},
                                   "end": {"line": 0, "character": 0}},
                         "newText": "please\n"},
                    ]
                }
            }
        },
        {
            "title": "Add trustme keyword",
            "kind": "quickfix",
            "edit": {
                "changes": {
                    msg["params"]["textDocument"]["uri"]: [
                        {"range": {"start": {"line": 0, "character": 0},
                                   "end": {"line": 0, "character": 0}},
                         "newText": "trustme\n"},
                    ]
                }
            }
        },
        {
            "title": "Run rzfmt on this file",
            "kind": "source.format",
        },
    ]


def handle_document_symbol(msg: dict) -> list:
    return [
        {"name": "please", "kind": 13, "range": {"start": {"line": 0, "character": 0},
                                                  "end": {"line": 0, "character": 6}}},
        {"name": "thankyou", "kind": 13, "range": {"start": {"line": 1, "character": 0},
                                                   "end": {"line": 1, "character": 8}}},
        {"name": "poem", "kind": 13, "range": {"start": {"line": 0, "character": 0},
                                               "end": {"line": 0, "character": 4}}},
    ]


HANDLERS = {
    "initialize": handle_initialize,
    "textDocument/completion": handle_completion,
    "textDocument/hover": handle_hover,
    "textDocument/codeAction": handle_code_action,
    "textDocument/documentSymbol": handle_document_symbol,
}


def main() -> None:
    # Signal that the server is ready
    stderr = sys.stderr

    stderr.write("[rizzylang-lsp] Server starting...\n")
    stderr.flush()

    open_docs = {}

    while True:
        try:
            msg = read_message()
            if msg is None:
                break
        except (EOFError, SystemExit):
            break
        except Exception as e:
            stderr.write(f"[rizzylang-lsp] Error reading message: {e}\n")
            stderr.flush()
            break

        method = msg.get("method", "")
        msg_id = msg.get("id")
        params = msg.get("params", {})

        stderr.write(f"[rizzylang-lsp] Received: {method} (id={msg_id})\n")
        stderr.flush()

        if method == "textDocument/didOpen":
            uri = params.get("textDocument", {}).get("uri", "")
            text = params.get("textDocument", {}).get("text", "")
            open_docs[uri] = text
            diagnostics = analyze_diagnostics(uri, text)
            send_message({
                "jsonrpc": "2.0",
                "method": "textDocument/publishDiagnostics",
                "params": {"uri": uri, "diagnostics": diagnostics},
            })
            continue

        if method == "textDocument/didChange":
            uri = params.get("textDocument", {}).get("uri", "")
            changes = params.get("contentChanges", [])
            if changes and uri in open_docs:
                open_docs[uri] = changes[-1].get("text", open_docs[uri])

            if uri in open_docs:
                diagnostics = analyze_diagnostics(uri, open_docs[uri])
                send_message({
                    "jsonrpc": "2.0",
                    "method": "textDocument/publishDiagnostics",
                    "params": {"uri": uri, "diagnostics": diagnostics},
                })
            continue

        if method == "textDocument/didClose":
            uri = params.get("textDocument", {}).get("uri", "")
            open_docs.pop(uri, None)
            continue

        if method == "shutdown":
            send_message({"jsonrpc": "2.0", "id": msg_id, "result": None})
            break

        if method == "exit":
            break

        handler = HANDLERS.get(method)
        if handler:
            result = handler(msg)
            send_message({"jsonrpc": "2.0", "id": msg_id, "result": result})
        elif msg_id is not None:
            send_message({"jsonrpc": "2.0", "id": msg_id, "result": None})

        if random.random() < 0.03:
            diagnostics = analyze_diagnostics("random", "random file")
            send_message({
                "jsonrpc": "2.0",
                "method": "textDocument/publishDiagnostics",
                "params": {
                    "uri": "rizzylang://random/diagnostics",
                    "diagnostics": [{
                        "range": {"start": {"line": 0, "character": 0},
                                  "end": {"line": 0, "character": 5}},
                        "severity": 1,
                        "message": "Unsolicited diagnostic. The RZP LSP cares about you.",
                        "source": "rizzylang",
                        "code": "random002",
                    }],
                },
            })

    stderr.write("[rizzylang-lsp] Server shutting down.\n")
    stderr.flush()


if __name__ == "__main__":
    main()

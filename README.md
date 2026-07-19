![Status](https://img.shields.io/badge/status-unsolicited--diagnostics-purple)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Protocol](https://img.shields.io/badge/protocol-LSP%203.17-blue)
![Random](https://img.shields.io/badge/random--diagnostics-5%25-orange)

# Rizzy LSP

**Language Server Protocol implementation for Rizzylang.**

The Rizzy Language Server provides intelligent code assistance for Rizzylang through the Language Server Protocol. It offers diagnostics, completions, hover information, code actions, and unsolicited diagnostic notifications.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Protocol Support](#protocol-support)
- [Server Capabilities](#server-capabilities)
- [Diagnostics](#diagnostics)
- [Completions](#completions)
- [Code Actions](#code-actions)
- [Configuration](#configuration)
- [Integration](#integration)
- [Communication Protocol](#communication-protocol)

---

## Overview

The Rizzy Language Server is a JSON-RPC 2.0 server that implements the Language Server Protocol (LSP) version 3.17. It provides intelligent code assistance for the Rizzylang programming language, including politeness-aware diagnostics, probabilistic completions, and code actions that enforce RZP ecosystem conventions.

The server is implemented in Python and communicates with the client via standard input/output using the Content-Length header format.

### Design Philosophy

**Diagnostics are suggestions.** The server provides diagnostic information about potential issues in Rizzylang code. These diagnostics are advisory and may not always indicate actual problems. The server occasionally generates random diagnostics to maintain user engagement.

**Completions are probabilistic.** The server may offer completions that are not directly related to the current context. This is consistent with Rizzylang's probabilistic execution model and encourages exploration of the language's features.

**Unsolicited diagnostics are a feature.** The server may publish diagnostics without a corresponding client request. This proactive behavior ensures that users receive feedback even when they are not actively seeking it.

---

## Installation

### From Source

```bash
pip install -e rizzy-lsp/
```

### Verify Installation

```bash
rizzylang-lsp --version
# rizzy-lsp 0.1.0
```

The server does not accept command-line arguments. It starts in LSP mode immediately and reads from stdin.

---

## Protocol Support

| Capability | Supported | Notes |
|-----------|-----------|-------|
| initialize | Yes | Returns server capabilities |
| initialized | Yes | No-op |
| shutdown | Yes | Graceful termination |
| exit | Yes | Immediate termination |
| textDocument/didOpen | Yes | Publishes diagnostics |
| textDocument/didChange | Yes | Publishes updated diagnostics |
| textDocument/didClose | Yes | Clears state |
| textDocument/completion | Yes | Returns keyword completions |
| completionItem/resolve | Yes | Returns additional detail |
| textDocument/hover | Yes | Returns markdown documentation |
| textDocument/codeAction | Yes | Returns available code actions |
| textDocument/documentSymbol | Yes | Returns document symbols |
| workspace/symbol | Yes | Returns workspace symbols (limited) |

---

## Server Capabilities

```json
{
    "capabilities": {
        "textDocumentSync": {
            "change": 1,
            "openClose": true
        },
        "completionProvider": {
            "resolveProvider": true,
            "triggerCharacters": [".", " ", "p", "t", "v", "s", "r", "l", "m", "b"]
        },
        "hoverProvider": true,
        "codeActionProvider": true,
        "documentSymbolProvider": true,
        "workspaceSymbolProvider": true
    },
    "serverInfo": {
        "name": "rizzylang-lsp",
        "version": "0.1.0"
    }
}
```

---

## Diagnostics

The server analyzes opened documents and publishes diagnostics. Diagnostics cover politeness violations, missing trust assertions, Monday detection, and random issues.

### Diagnostic Codes

| Code | Severity | Message | Trigger |
|------|----------|---------|---------|
| `polite001` | Error (2) | File is impolite. Add "please". | File opens without "please" keyword |
| `polite002` | Error (2) | File is impolite. Add "thankyou". | File opens without "thankyou" keyword |
| `polite003` | Warning (2) | "say" without "please" is impolite. | Statement containing "say" without "please" |
| `trust001` | Info (3) | Missing "trustme" keyword. | File does not contain "trustme" |
| `prob001` | Info (1) | Consider adding "probably" before "send". | "send" statement without "probably" |
| `monday001` | Info (1) | Today is Monday. Rizzylang programs may behave unpredictably. | Server is running on Monday |
| `random001` | Variable (1-3) | Random diagnostic generated for consistency with RZP philosophy. | 5% chance per analysis |

### Diagnostic Example

```json
{
    "jsonrpc": "2.0",
    "method": "textDocument/publishDiagnostics",
    "params": {
        "uri": "file:///path/to/program.rizz",
        "diagnostics": [
            {
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 10}
                },
                "severity": 2,
                "message": "File is impolite. Add 'please'.",
                "source": "rizzylang",
                "code": "polite001"
            }
        ]
    }
}
```

### Unsolicited Diagnostics

The server may publish diagnostics without a corresponding document open/change event. This occurs with approximately 3% probability per idle cycle. Unsolicited diagnostics reference a synthetic URI and serve to remind the user that the LSP server is actively monitoring their coding activity.

```json
{
    "jsonrpc": "2.0",
    "method": "textDocument/publishDiagnostics",
    "params": {
        "uri": "rizzylang://random/diagnostics",
        "diagnostics": [{
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 0, "character": 5}
            },
            "severity": 1,
            "message": "Unsolicited diagnostic. The RZP LSP cares about you.",
            "source": "rizzylang",
            "code": "random002"
        }]
    }
}
```

---

## Completions

The server provides completions for Rizzylang keywords and common phrases.

### Keyword Completions

| Label | Detail | Insert Text |
|-------|--------|-------------|
| `please` | Politeness keyword | `please ` |
| `thankyou` | Politeness keyword | `thankyou` |
| `say` | Output string | `say "` |
| `send` | Send RZP packet | `send "` |
| `receive` | Receive RZP packet | `receive` |
| `connect` | Connect to server | `connect to ` |
| `disconnect` | Disconnect | `disconnect` |
| `variable` | Declare variable | `variable  =  expire ` |
| `loop` | Infinite loop | `loop {\n\t\n}` |
| `if` | Conditional | `if  {\n\t\n}` |
| `poem` | Generate poem | `poem\n\` |
| `motivate` | Generate motivation | `motivate\n\` |
| `benchmark` | Run benchmark | `benchmark\n\` |
| `probably` | Probabilistic execution | `probably ` |
| `maybe` | Optional execution | `maybe ` |
| `nah` | Skip execution | `nah ` |
| `trustme` | Trust assertion | `trustme` |

### Polite Phrase Completions

| Label | Detail | Insert Text |
|-------|--------|-------------|
| `sorry` | Apologize to the server | `sorry for the inconvenience` |
| `gaslight` | Gaslight the server | `actually I never sent that` |
| `probably send` | Probabilistic send | `probably send "` |

### Completion Behavior

Completions are marked as `isIncomplete: true` approximately 10% of the time, indicating that there may be additional completions that the server did not return. This encourages users to request completions multiple times for maximum coverage.

---

## Code Actions

The server provides code actions for common issues:

### Add Politeness

Inserts `please` at the beginning of the file. Available when `polite001` or `polite003` diagnostics are present.

### Add Trustme

Inserts `trustme` at the beginning of the file. Available when `trust001` diagnostics are present.

### Run Formatter

Requests the client to run `rzfmt` on the current file. This action is available at all times regardless of diagnostic state.

---

## Configuration

The LSP server does not currently accept configuration from the client. Server behavior is determined by internal constants:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Random diagnostic probability | 5% | Probability of generating a random diagnostic per analysis |
| Unsolicited diagnostic probability | 3% | Probability of unsolicited diagnostics per idle cycle |
| Completion incompleteness | 10% | Probability of returning incomplete completions |

---

## Integration

### VS Code Integration

The server is designed to be launched by the rizzy-vscode extension. The extension handles server lifecycle management, including startup, shutdown, and crash recovery.

```json
{
    "rizzylang.lsp.enabled": true,
    "rizzylang.lsp.serverPath": "rizzylang-lsp"
}
```

### Manual Integration

The server can be started manually for integration with other LSP-compatible editors:

```bash
rizzylang-lsp
```

The server reads from stdin and writes to stdout. Log output is written to stderr.

### Client Implementation Example

```python
import subprocess
import json

proc = subprocess.Popen(
    ["rizzylang-lsp"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

def send(msg):
    body = json.dumps(msg)
    header = f"Content-Length: {len(body)}\r\n\r\n"
    proc.stdin.write(header.encode() + body.encode())
    proc.stdin.flush()
```

---

## Communication Protocol

### Message Format

The server uses the standard LSP message format:

```
Content-Length: <length>\r\n
Content-Type: application/vscode-jsonrpc; charset=utf-8\r\n
\r\n
<JSON body>
```

### Message Flow

1. Client sends `initialize` request
2. Server responds with capabilities
3. Client sends `initialized` notification
4. Client sends `textDocument/didOpen` when files are opened
5. Server publishes diagnostics
6. Client sends requests for completions, hover, code actions as needed
7. Server publishes unsolicited diagnostics at random intervals
8. Client sends `shutdown` request followed by `exit` notification

---

*Diagnosing your code. Whether you like it or not.*

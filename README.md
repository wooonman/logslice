# logslice

Stream and filter structured JSON logs from multiple sources with a simple query syntax.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

Point `logslice` at one or more log sources and filter using field expressions:

```bash
# Filter logs from a file where level is ERROR
logslice --source app.log "level=ERROR"

# Stream from multiple files and match a service name
logslice --source api.log --source worker.log "service=payments AND level=WARN"

# Pipe from stdin
tail -f app.log | logslice "status_code>=500"

# Output only specific fields
logslice --source app.log --fields timestamp,level,message "level=ERROR"
```

**Example output:**

```json
{"timestamp": "2024-03-01T12:34:56Z", "level": "ERROR", "service": "api", "message": "Connection timeout"}
{"timestamp": "2024-03-01T12:35:10Z", "level": "ERROR", "service": "api", "message": "Database unreachable"}
```

### Query Syntax

| Operator | Example | Description |
|----------|---------|-------------|
| `=` | `level=ERROR` | Exact match |
| `!=` | `level!=DEBUG` | Not equal |
| `>=`, `<=` | `status_code>=500` | Numeric comparison |
| `~` | `message~timeout` | Substring match |
| `AND` / `OR` | `level=ERROR AND service=api` | Boolean logic |

### Options

| Flag | Description |
|------|-------------|
| `--source` | Log file to read from (can be repeated) |
| `--fields` | Comma-separated list of fields to include in output |
| `--follow` | Keep reading as the file grows (like `tail -f`) |
| `--no-color` | Disable colorized output |

---

## License

MIT © [yourname](https://github.com/yourname)

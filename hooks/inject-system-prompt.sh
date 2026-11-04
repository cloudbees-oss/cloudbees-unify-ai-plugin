#!/usr/bin/env sh
# Grok sets GROK_HOOK_EVENT and GROK_HOOK_NAME for hooks and ignores SessionStart additionalContext.
[ "${GROK_HOOK_EVENT:-}" = session_start ] && [ -n "${GROK_HOOK_NAME:-}" ] && exit 0
python3 -c "
import os, json
r = os.environ.get('CLAUDE_PLUGIN_ROOT', '')
p = os.path.join(r, 'hooks', 'system-prompt.md')
t = open(p).read() if r and os.path.exists(p) else ''
print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': t}}))
"

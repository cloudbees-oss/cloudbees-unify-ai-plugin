#!/usr/bin/env sh
python3 -c "
import os, json
r = os.environ.get('CLAUDE_PLUGIN_ROOT', '')
p = os.path.join(r, 'hooks', 'system-prompt.md')
t = open(p).read() if r and os.path.exists(p) else ''
print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': t}}))
"

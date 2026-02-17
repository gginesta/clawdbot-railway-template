#!/bin/bash

AGENTS=("molty" "raphael" "leonardo")

for agent in "${AGENTS[@]}"; do
    echo "Checking QMD for $agent:"
    
    # Check workspace
    WORKSPACE=$(grep -A10 "\"id\": \"$agent\"" /data/workspace/research/tmnt-team-architecture/config-template.json5 | grep "workspace" | cut -d'"' -f4)
    
    echo "Workspace: $WORKSPACE"
    
    # Check QMD in that workspace
    echo "QMD in Workspace:"
    find "$WORKSPACE" -name "qmd" || echo "No QMD found in workspace"
    
    # Check global QMD
    echo "Global QMD:"
    (cd "$WORKSPACE" && which qmd) || echo "No global QMD accessible"
    
    echo "---"
done
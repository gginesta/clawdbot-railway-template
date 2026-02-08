#!/bin/bash

# Source credentials
source /data/workspace/credentials/notion.env

# Create Skill Evaluation Checklist Page
echo "Creating Skill Evaluation Checklist Page..."

CHECKLIST_RESPONSE=$(curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Notion-Version: 2022-06-28" \
  -d '{
    "parent": {
      "type": "page_id", 
      "page_id": "2fa39dd69afd80be89dae91e20d30a38"
    },
    "icon": {
      "type": "emoji",
      "emoji": "🔒"
    },
    "properties": {
      "title": [
        {
          "type": "text",
          "text": {
            "content": "Skill Evaluation Checklist"
          }
        }
      ]
    },
    "children": [
      {
        "type": "callout",
        "callout": {
          "icon": {
            "type": "emoji",
            "emoji": "⚠️"
          },
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Every skill MUST pass this checklist before installation. No exceptions. Security failures = automatic rejection."
              }
            }
          ]
        }
      },
      {
        "type": "heading_2",
        "heading_2": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Security Evaluation (MANDATORY — All Must Pass)"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Code Audit",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text", 
              "text": {
                "content": " — Read EVERY script in scripts/. Check for: outbound network calls to unknown hosts, credential access beyond declared scope, file system writes outside workspace, eval() or exec() of dynamic strings, obfuscated code"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Credential Scope",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — Does the skill need API keys/tokens? Which ones? Are they the MINIMUM required? Does it access credentials it shouldn'\''t?"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Network Access",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — Does it make outbound HTTP calls? To where? Are all endpoints documented and expected? Any data exfiltration risk?"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "File System Access",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — What does it read/write? Does it stay within /data/workspace? Any access to /data/.openclaw or system files?"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Dependency Chain",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — External dependencies (npm, pip, binaries)? Each dependency is an attack surface. Prefer zero-dependency skills."
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Data Handling",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — Does it process sensitive data (emails, credentials, personal info)? Does it log or transmit sensitive data? Is data handled in memory only or written to disk?"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Prompt Injection Surface",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — Does the skill process external/untrusted content? Could injected instructions in that content hijack the agent? Are there safeguards?"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Update Mechanism",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — How is the skill updated? Can it auto-update (risk)? Is it pinned to a version?"
              }
            }
          ]
        }
      },
      {
        "type": "heading_2",
        "heading_2": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Functional Evaluation"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Purpose Fit",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — Does this solve a real need for our squad? Which agents benefit?"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Token Cost",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — How large is SKILL.md? Remember: context window is shared. Prefer <2KB SKILL.md"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Reliability",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — Does it work on Railway containers (no GPU, limited RAM)? Tested end-to-end?"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Overlap Check",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — Do we already have a skill that does this? Check /data/shared/skills/ and installed skills"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Maintenance Burden",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " — Who maintains it? Will it break when APIs change? Is the author active?"
              }
            }
          ]
        }
      },
      {
        "type": "heading_2",
        "heading_2": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Distribution Decision"
              }
            }
          ]
        }
      },
      {
        "type": "table",
        "table": {
          "table_width": 3,
          "has_column_header": true,
          "children": [
            {
              "type": "table_row",
              "table_row": {
                "cells": [
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "Tier"
                      }
                    }
                  ],
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "Criteria"
                      }
                    }
                  ],
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "Distribution"
                      }
                    }
                  ]
                ]
              }
            },
            {
              "type": "table_row",
              "table_row": {
                "cells": [
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "Core"
                      }
                    }
                  ],
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "All agents need it, security passed, low token cost"
                      }
                    }
                  ],
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "/data/shared/skills/ (Syncthing)"
                      }
                    }
                  ]
                ]
              }
            },
            {
              "type": "table_row",
              "table_row": {
                "cells": [
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "Role"
                      }
                    }
                  ],
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "Specific agents need it, security passed"
                      }
                    }
                  ],
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "Webhook to target agent"
                      }
                    }
                  ]
                ]
              }
            },
            {
              "type": "table_row",
              "table_row": {
                "cells": [
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "Custom"
                      }
                    }
                  ],
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "One agent, experimental, or conditional security"
                      }
                    }
                  ],
                  [
                    {
                      "type": "text",
                      "text": {
                        "content": "Local workspace only"
                      }
                    }
                  ]
                ]
              }
            }
          ]
        }
      },
      {
        "type": "heading_2",
        "heading_2": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Approval Flow"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Evaluator",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " runs checklist (usually Molty)"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Security score",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " assigned: ✅ Passed / ⚠️ Conditional (document conditions) / ❌ Failed (rejected)"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Test",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " on one agent in isolation first"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Register",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " in Skill Registry database with all metadata"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Distribute",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " per tier rules"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Notify",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " receiving agents via webhook with install instructions"
              }
            }
          ]
        }
      },
      {
        "type": "numbered_list_item",
        "numbered_list_item": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Verify",
                "annotations": {
                  "bold": true
                }
              }
            },
            {
              "type": "text",
              "text": {
                "content": " installation confirmed by each agent"
              }
            }
          ]
        }
      },
      {
        "type": "divider",
        "divider": {}
      },
      {
        "type": "paragraph",
        "paragraph": {
          "rich_text": [
            {
              "type": "text",
              "text": {
                "content": "Last updated: 2026-02-08 by Molty 🦎"
              }
            }
          ]
        }
      }
    ]
  }')

echo "Checklist Response: $CHECKLIST_RESPONSE"
CHECKLIST_PAGE_ID=$(echo "$CHECKLIST_RESPONSE" | jq -r '.id')
echo "Checklist Page ID: $CHECKLIST_PAGE_ID"
echo "Checklist Page URL: https://www.notion.so/$CHECKLIST_PAGE_ID"

echo "Skill Evaluation Checklist creation complete!"
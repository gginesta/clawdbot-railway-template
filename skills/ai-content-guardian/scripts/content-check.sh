#!/bin/bash
# Make executable: chmod +x content-check.sh

# AI Content Guardian - Slop Pattern Detector
# Usage: content-check.sh "text to analyze"

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"text to analyze\""
    echo "Flags potential AI slop patterns in social media content"
    exit 1
fi

TEXT="$1"
ISSUES=0

echo "🔍 AI Content Guardian - Slop Detection"
echo "========================================"

# Check for em dashes
if echo "$TEXT" | grep -q "—"; then
    echo "❌ EM DASHES detected — classic Claude artifact"
    ISSUES=$((ISSUES + 1))
fi

# Check for filler openers
FILLER_PATTERNS=(
    "Great point"
    "This is huge" 
    "Love this"
    "Thanks for sharing"
    "Absolutely"
    "I'd be happy to"
    "Hope this helps"
    "Let me know if"
)

for pattern in "${FILLER_PATTERNS[@]}"; do
    if echo "$TEXT" | grep -qi "$pattern"; then
        echo "❌ FILLER OPENER: '$pattern' - sounds generic"
        ISSUES=$((ISSUES + 1))
    fi
done

# Check for LinkedIn influencer language
LINKEDIN_PATTERNS=(
    "game changer"
    "game-changer"
    "actionable insights"
    "key takeaways"
    "thought leadership"
    "circle back"
    "deep dive"
    "low-hanging fruit"
    "synergy"
    "leverage"
)

for pattern in "${LINKEDIN_PATTERNS[@]}"; do
    if echo "$TEXT" | grep -qi "$pattern"; then
        echo "❌ LINKEDIN SPEAK: '$pattern' - too corporate"
        ISSUES=$((ISSUES + 1))
    fi
done

# Check for excessive emoji usage
EMOJI_COUNT=$(echo "$TEXT" | grep -o "🙌\|👏\|💯\|🔥\|✨\|💪" | wc -l)
if [ "$EMOJI_COUNT" -gt 2 ]; then
    echo "❌ EMOJI OVERLOAD: $EMOJI_COUNT excitement emojis detected"
    ISSUES=$((ISSUES + 1))
fi

# Check for bullet point structure
if echo "$TEXT" | grep -q "^[•·\*\-]"; then
    echo "❌ BULLET ESSAYS: Detected list structure - too formal for replies"
    ISSUES=$((ISSUES + 1))
fi

# Check for overly long responses (likely essays)
WORD_COUNT=$(echo "$TEXT" | wc -w)
if [ "$WORD_COUNT" -gt 50 ]; then
    echo "⚠️  LONG RESPONSE: $WORD_COUNT words - consider shorter for social replies"
    ISSUES=$((ISSUES + 1))
fi

# Check for relentlessly positive tone (basic check)
POSITIVE_WORDS=$(echo "$TEXT" | grep -oi "\(amazing\|awesome\|incredible\|fantastic\|perfect\|brilliant\|outstanding\|excellent\)" | wc -l)
if [ "$POSITIVE_WORDS" -gt 2 ]; then
    echo "❌ TOO POSITIVE: $POSITIVE_WORDS superlatives - humans have bad days too"
    ISSUES=$((ISSUES + 1))
fi

# Check for generic phrases
GENERIC_PATTERNS=(
    "couldn't agree more"
    "so true"
    "exactly this"
    "well said"
    "spot on"
    "nailed it"
)

for pattern in "${GENERIC_PATTERNS[@]}"; do
    if echo "$TEXT" | grep -qi "$pattern"; then
        echo "❌ GENERIC PHRASE: '$pattern' - could apply to any post"
        ISSUES=$((ISSUES + 1))
    fi
done

# Check sentence structure variety
SENTENCE_COUNT=$(echo "$TEXT" | grep -o '[.!?]' | wc -l)
if [ "$SENTENCE_COUNT" -gt 2 ]; then
    # Simple check: if all sentences are similar length, flag it
    AVG_LENGTH=$(echo "$TEXT" | sed 's/[.!?]/\n/g' | awk '{sum+=length($0); count++} END {if(count>0) print int(sum/count)}')
    if [ "$AVG_LENGTH" -gt 40 ]; then
        echo "⚠️  UNIFORM SENTENCES: All sentences similar length - add variety"
        ISSUES=$((ISSUES + 1))
    fi
fi

echo "========================================"

if [ "$ISSUES" -eq 0 ]; then
    echo "✅ LOOKS HUMAN: No obvious AI slop patterns detected"
    echo "💡 Still ask: 'Would I text this to a friend?'"
else
    echo "🚨 $ISSUES ISSUE(S) FOUND"
    echo "💡 Rewrite to sound more natural and specific"
fi

echo ""
echo "Self-check questions:"
echo "1. Does this only work for THIS specific post?"
echo "2. Am I adding new info or specific opinion?"
echo "3. Would I send this in a group chat?"

exit $ISSUES
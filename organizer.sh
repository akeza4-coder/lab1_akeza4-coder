#!/usr/bin/env bash
# organizer.sh — Archives grades.csv with a timestamp, resets the workspace, and logs the action.

TARGET="grades.csv"
ARCHIVE_DIR="archive"
LOG_FILE="organizer.log"

# ── 1. Ensure the archive directory exists ────────────────────────────────────
if [ ! -d "$ARCHIVE_DIR" ]; then
    mkdir -p "$ARCHIVE_DIR"
    echo "Created directory: $ARCHIVE_DIR"
fi

# ── 2. Check that grades.csv actually exists before archiving ─────────────────
if [ ! -f "$TARGET" ]; then
    echo "Warning: '$TARGET' not found. Nothing to archive."
    echo "A fresh '$TARGET' will be created."
    touch "$TARGET"
    exit 0
fi

# ── 3. Generate a timestamp (YYYYMMDD-HHMMSS) ─────────────────────────────────
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# ── 4. Build the archived filename ───────────────────────────────────────────
ARCHIVED_NAME="grades_${TIMESTAMP}.csv"

# ── 5. Move and rename the file into the archive directory ───────────────────
mv "$TARGET" "${ARCHIVE_DIR}/${ARCHIVED_NAME}"
echo "Archived: $TARGET  →  ${ARCHIVE_DIR}/${ARCHIVED_NAME}"

# ── 6. Create a fresh, empty grades.csv for the next batch ───────────────────
touch "$TARGET"
echo "Reset: A new empty '$TARGET' has been created."

# ── 7. Append a log entry to organizer.log ───────────────────────────────────
{
    echo "---"
    echo "Timestamp     : $TIMESTAMP"
    echo "Original file : $TARGET"
    echo "Archived as   : ${ARCHIVE_DIR}/${ARCHIVED_NAME}"
} >> "$LOG_FILE"

echo "Logged action to: $LOG_FILE"
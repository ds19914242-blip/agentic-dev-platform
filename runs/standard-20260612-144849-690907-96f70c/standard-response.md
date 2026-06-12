# Standard Implementation Response

Done. The change is minimal and label-only:

- **Collect-run line** relabeled `последний:` → `последний сбор:` ("last collected"), so it's textually distinct from a manual check.
- **Comment added** documenting the distinction and reserving `Проверено …` ("Проверено" = checked) for the manual-check indicator, so whoever adds that badge uses the distinct label.

No change to `lastStatus`/`lastItemCount` data flow or collect-run semantics. Note: the manual-check badge itself doesn't exist in this file yet (the "Проверить" button currently only fires a toast), so this task establishes the label convention for it without introducing the badge.

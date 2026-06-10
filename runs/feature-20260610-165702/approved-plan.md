# Approved Plan

I've reviewed the only in-scope file. Here is the implementation plan.

## Plan: Translate `app/reports/page.tsx` UI text to Russian

**Scope:** Only `app/reports/page.tsx`. No other files touched. Only user-visible string literals change — no logic, JSX structure, `value=` attributes, class names, or data values change.

### String replacements

| Line | Current (EN) | Russian |
|------|-------------|---------|
| 39 | `toast("Report deleted", ...)` | `"Отчёт удалён"` |
| 41 | `toast("Failed to delete", ...)` | `"Не удалось удалить"` |
| 55 | `<h1>Reports</h1>` | `Отчёты` |
| 57 | `Saved analyses — open without re-running Claude.` | `Сохранённые анализы — открывайте без повторного запуска Claude.` |
| 60 | (already Russian helper text) | **leave unchanged** |
| 68 | `placeholder="Search by file…"` | `"Поиск по файлу…"` |
| 76 | `<option>All modes</option>` (value stays `all`) | `Все режимы` |
| 77 | `<option>Fast</option>` (value stays `fast`) | `Быстрый` |
| 78 | `<option>Balanced</option>` (value stays `balanced`) | `Сбалансированный` |
| 79 | `<option>Deep</option>` (value stays `deep`) | `Глубокий` |
| 92 | `"No reports yet."` / `"Nothing matches your filters."` | `"Отчётов пока нет."` / `"Ничего не найдено по вашим фильтрам."` |
| 95 | `Run analysis` | `Запустить анализ` |
| 121 | `<p className="label">Selected</p>` | `Выбрано` |
| 125 | `<p className="label">Trends</p>` | `Тренды` |
| 130 | `Open` | `Открыть` |
| 142 | `Delete` | `Удалить` |
| 152 | `title="Delete report?"` | `"Удалить отчёт?"` |
| 153 | `message="The report, upload, and history record will be removed. This cannot be undone."` | `"Отчёт, загруженный файл и запись истории будут удалены. Это действие необратимо."` |

### Deliberately left unchanged
- **Line 60** — already Russian.
- **Line 106 `{r.mode}`** — renders the raw data value (`fast`/`balanced`/`deep`), not a UI label. Translating it would require a label-mapping object and risks visual mismatch; leaving the data verbatim is the smallest safe choice.
- **Lines 132/135 `PDF` / `MD`** — format acronyms, not translatable text.
- **Line 114** — date already formatted with `"ru-RU"` locale.
- All `value=` attributes on `<option>` (`all`/`fast`/`balanced`/`deep`) — these drive filter logic and must stay as-is.

### One judgment call to confirm
The mode badge on **line 106** shows the literal English-ish mode keyword. My plan leaves it as data. If you'd prefer the badge localized too, I'd add a small `MODE_LABEL` map (`fast → Быстрый`, etc.) and render `MODE_LABEL[r.mode]` — slightly larger change. Default: leave it.

### Verification
- Confirm no `value=` / className / import / hook changed.
- Type-check is unaffected (only string literal contents change).

The change is mechanical, contained to one file, and trivially reversible.


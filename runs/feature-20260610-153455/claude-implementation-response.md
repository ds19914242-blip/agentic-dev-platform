# Claude Implementation Response

Done. Type-check passed with no errors.

**Changed files:**
- `app/sources/page.tsx` — added one helper `<p>` element under the existing subtitle in the header `<div>`, using `text-xs text-slate-400` muted styling: "Здесь можно добавлять RSS-источники и проверять их доступность."

**Risks:** None of consequence. This is a purely presentational, additive change — no logic, state, or data flow touched. The sibling "+ Новый источник" button and the `flex items-center justify-between` header layout are unaffected, and the change is trivially reversible.

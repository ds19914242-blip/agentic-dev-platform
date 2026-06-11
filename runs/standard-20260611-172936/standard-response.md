# Standard Implementation Response

TSC passed (no output). Type check is clean.

I've added a build info toggle to the footer in `components/Footer.tsx`.

**Changes:**
- Added `"use client"` and a local `useState` (`showBuildInfo`) — state is purely local UI state.
- Added a small toggle button ("Сведения о сборке" / "Скрыть сведения") at the end of the footer row.
- When hidden (default), the existing footer renders exactly as before — same content, now wrapped in a flex row inside the footer.
- When shown, a second line appears displaying the app name and current year (`RSS Agent Lab · © 2026`).

No API, auth, database, route, or config changes. `tsc --noEmit` passes clean. (The project has no `lint` script.)

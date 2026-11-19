# V3 release verification

Date: 2026-09-25. Status: PASS.

- Final student worksheet: 8 pages; reference: 4 pages. All 12 latest rendered pages visually inspected. No clipped text, broken tables, detached prompts, near-empty overflow pages, missing Chinese glyphs, or decorative title borders.
- Unmodified skill worksheet lint: 0 errors, 0 warnings. Design check: 0 errors, 0 warnings. Coverage maps all Lesson 2 objectives and five homework items.
- Independent simulated student pilot: 129/129 fields answered, 0 blocking issues. Launch estimate 48 minutes versus 45; homework 92 minutes versus 90, both within the skill's 20% tolerance. This is simulated feasibility evidence, not a real student trial.
- Two residual timing frictions: Experiment 2 plus the method column needs about 33 minutes rather than 25; the 92-minute total assumes the working course Python environment, the optional helper and direct insertion of generated numeric tables. Building every Excel calculation from scratch will take longer. Students may redistribute time across modules.
- Numerical helper executed. Its category recoding, contingency table, standardization, missingness, zero-value sensitivity and complete-case outputs agree with independent raw-data calculations. Source dataset copy is byte-for-byte unchanged (SHA256 in verified-results.json).
- All five public source URLs returned HTTP 200. Source metadata, codebook discrepancies and StandardScaler ddof convention checked. Course slide ranges inspected directly from the existing PPTX.
- All local student file paths resolve. Worksheet and reference contain no replacement glyphs. Pilot copy refreshed against the final worksheet layout.

## Intentional departures from default package workflow

The user approved replacing Packet A–D releases, repeated tracking, evidence cards and exit tickets with Learn / Experiment / Explain. All inputs are available from the start; stage codes in analysis-design.json exist only for QA mapping. This is a worksheet revision with a short reference, not a regenerated full teaching package. V2 and shared skills were not edited.

## Rendering environment

The packaged documents renderer was attempted and failed because LibreOffice was unavailable. No bundled dependency loader was exposed in this Windows session. Available Python document libraries were used, with an isolated hidden Microsoft Word instance to export read-only DOCXs and PyMuPDF to render page images. Source documents were never saved through Word. Rendering outputs and all answers remain teacher-only under review/.

# Raw Google inputs audit

Download [raw_inputs_audit.zip](raw_inputs_audit.zip), extract, and open analysis_clean/raw_inputs_audit/raw_inputs_report.html. Includes read-only audit code, field coverage, availability flags and file inventory. No raw review text or reviewer identities are included.

The inputs folder contains 52 metadata gzip files (1.113 GB) and 52 review gzip files (52.702 GB): all 50 states, DC, and other. All 4,989,684 metadata rows were scanned, and all 8,669 primary-ME/Mediterranean businesses matched, including the 5,983 current core-label businesses.

Fields absent from Meta_data_combined.csv include price tier (73.5% of current core businesses), description (56.9%), hours (97.3%), operating status (71.5%), lifetime rating/review count (100%), and related-business IDs (93.6%). MISC is already in combined metadata but unused in the current models; it contains service, offerings, atmosphere and clientele attributes.

Raw reviews add the full national text source, reviewer user_id, owner responses/timestamps and photo URL lists compared with the saved text panel. Only the first 1,000 review rows per file were inspected for schema, not a complete corpus count or historical coverage audit. The strongest next opportunity is scanning all available pre-election text with the frozen dictionary; current tags rely on a limited food-screened saved corpus. Expansion size remains unknown. Outcome ratings/counts already use the larger combined outcome source.

Metadata lacks a historical as-of date and includes COVID-era attributes. Snapshot prices, hours, lifetime ratings/counts or closure status cannot automatically be used as predetermined 2016 controls. No explicit opening date or chain identifier was found. Raw date validation is needed, including a 1990 timestamp observed in the bounded review inspection.

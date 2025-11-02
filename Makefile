# Helpers locals (opcionals)
.PHONY: i18n-check i18n-icu i18n-pseudo

i18n-check:
	python scripts/i18n_check_keys.py i18n/en-US.json i18n/ca.json

i18n-icu:
	python scripts/i18n_validate_icu.py i18n/en-US.json i18n/ca.json

i18n-pseudo:
	python scripts/pseudo_localize.py i18n/en-US.json i18n/en-US__pseudo.json

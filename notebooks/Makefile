PIP := pip

ipython                := ipython
ipython_notebook       := notebook

den := $(ipython) $(ipython_notebook)

nohup := nohup

kill       := pkill
kill_flags := -f

help:
	@$(MAKE) --print-data-base --question no-such-target | \
	grep -v -e '^no-such-target' -e '^Makefile'	     | \
	awk '/^[^.%][-A-Za-z0-9_]*:/ \
	     { print substr($$1, 1, length($$1)-1) }'        | \
	sort					             | \
	pr -2 -t

init:
	$(PIP) install --editable ..[notebook]

run:
	$(nohup) $(den) &

stop:
	$(kill) $(kill_flags) $(den)

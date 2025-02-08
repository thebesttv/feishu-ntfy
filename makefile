.PHONY: clean

ntfy: main.sh main.py
	cat main.sh main.py >$@
	chmod +x $@

clean:
	rm -f ntfy

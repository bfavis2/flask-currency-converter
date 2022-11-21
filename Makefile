ZIPFILE := takehome-backend-$(shell date "+%Y-%m-%d").zip
zip:
	zip $(ZIPFILE) * -x README.md Makefile

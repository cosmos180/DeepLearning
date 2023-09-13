default_target: help
.PHONY : help build clean

# Help Target
help:
	@echo "The following are some of the valid targets for this Makefile:"
	@echo "... all (the default if no target is provided)"
	@echo "... clean"
	@echo "... depend"
	@echo "... edit_cache"
	@echo "... rebuild_cache"
	@echo "... jason"
	@echo "... main"
	@echo "... main.o"
	@echo "... main.i"
	@echo "... main.s"

clean:
	@echo "... clean"
	pwd
	rm -r build/*

build:
	@echo "[build]:"
	./sh/build.sh


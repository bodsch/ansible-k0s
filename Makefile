#
export TOX_SCENARIO  ?= default
export TOX_ANSIBLE   ?= ansible_8.5

.PHONY: converge destroy verify test lint gh-clean

default: converge

converge:
	@hooks/converge

destroy:
	@hooks/destroy

verify:
	@hooks/verify

test:
	@hooks/test

lint:
	@hooks/lint

gh-clean:
	@hooks/gh-clean

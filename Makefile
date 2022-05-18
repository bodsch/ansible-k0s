#
export TOX_SCENARIO  ?= default
export TOX_PYTHON    ?= py310
export TOX_ANSIBLE   ?= ansible510

.PHONY: converge destroy verify lint

default: converge

converge:
	@hooks/converge

destroy:
	@hooks/destroy

verify:
	@hooks/verify

lint:
	@hooks/lint

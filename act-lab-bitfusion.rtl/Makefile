##################################################
# COCOTB
COCOTB=$(HOME)/workspace/libs/cocotb
SIM_BUILD ?= sim_build
export SIM_BUILD
SIM_OUTPUT ?= sim_output
export SIM_OUTPUT

PYTHONPATH:=$(PYTHONPATH):./cocotb/

# xml compile vars
EXTRA_LIBS := -lvpi
EXTRA_LIBDIRS := -L$(ICARUS_BIN_DIR)/../lib

# We want to include the Python files from Cocotb in the dependencies
CUSTOM_SIM_DEPS += $(shell find $(COCOTB)/cocotb/ -name "*.py")

IVERILOG_BIN:= /usr/local/bin/iverilog
VVP_BIN:= /usr/local/bin/vvp
LIB_DIR:= $(HOME)/workspace/libs/cocotb/build/libs/x86_64
BUILD_VPI=1

LIB_LOAD := LD_LIBRARY_PATH=$(LIB_DIR):$(LD_LIBRARY_PATH)

include $(COCOTB)/version
export VERSION
##################################################

##################################################
# DnnWeaver
HW_SRC_DIR := .
HW_FILELIST := file.list
HW_TESTLIST := test.list
HW_SRC_FILES := $(shell cat $(HW_FILELIST) | egrep -v '\#' | grep -v "tb" | grep -v "include")
VERILOG_SOURCES := $(HW_SRC_FILES:%=$(HW_SRC_DIR)/%)

# Generate the test.xml files
TEST_SUITE := $(shell cat $(HW_TESTLIST) | egrep -v '\#')
# TEST_XML := $(foreach test, $(TEST_SUITE), $(SIM_OUTPUT)/$(test).xml)

EXTRA_ARGS := -I $(HW_SRC_DIR)/include -g2012

TOPLEVEL ?=
MODULE ?=
##################################################

all: compile run_test

$(SIM_BUILD):
	@mkdir -p $@

$(SIM_OUTPUT):
	@mkdir -p $@

##################################################
# Compilation phase
##################################################
$(SIM_BUILD)/%.vvp: $(SIM_BUILD) $(VERILOG_SOURCES) $(CUSTOM_COMPILE_DEPS) $(HW_FILELIST)
	@echo "Compiling " $@
	@$(IVERILOG_BIN) -o $@ \
		-s $(patsubst $(SIM_BUILD)/%.vvp,%, $@) \
		-D COCOTB_SIM=1 \
		-D COCOTB_TOPLEVEL_$(patsubst $(SIM_BUILD)/%.vvp,%, $@) \
		$(COMPILE_ARGS) \
		$(EXTRA_ARGS) \
		$(VERILOG_SOURCES)

compile: $(patsubst %,$(SIM_BUILD)/%.vvp, $(TEST_SUITE))
	@echo $<

##################################################

##################################################
# Run Tests
##################################################
run_test: $(patsubst %,$(SIM_OUTPUT)/%.xml, $(TEST_SUITE))

.PHONY:FORCE
FORCE:

$(SIM_OUTPUT)/%.xml: $(SIM_BUILD)/%.vvp $(CUSTOM_SIM_DEPS) $(COCOTB_LIBS) $(COCOTB_VPI_LIB) $(SIM_OUTPUT) FORCE
	@echo "Testing " $@
	@PYTHONPATH=$(LIB_DIR):$(COCOTB):$(PWD):$(PYTHONPATH) $(LIB_LOAD) \
						 MODULE=$(patsubst $(SIM_OUTPUT)/%.xml,cocotb_%, $@) \
						 TESTCASE=$(TESTCASE) \
						 TOPLEVEL=$(patsubst $(SIM_OUTPUT)/%.xml,%,$@) \
						 TOPLEVEL_LANG=$(TOPLEVEL_LANG) \
						 $(VVP_BIN) -M $(LIB_DIR) -m gpivpi \
						 $< \
						 $(SIM_ARGS) \
						 $(EXTRA_ARGS) \
						 $(PLUSARGS)
	mv results.xml $@
	mv *.vcd $(SIM_OUTPUT)
##################################################

.PHONY: clean
clean:
	rm -rf $(SIM_OUTPUT) $(SIM_BUILD)

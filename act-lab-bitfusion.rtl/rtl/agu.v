//
// Address generation unit
//
// Hardik Sharma
// (hsharma@gatech.edu)

module agu #(
  parameter integer ADDR_WIDTH            = 32,
  parameter integer NUM_ADDR              = 16,
  parameter integer ADDR_SEL_WIDTH        = $clog2(NUM_ADDR)
) (
  input  wire                               clk,
  input  wire                               reset,

  input  wire                               start,
  input  wire                               ready,
  output wire                               done,

  input  wire                               write_enable,
  input  wire [ ADDR_SEL_WIDTH  -1 : 0 ]    write_sel,
  input  wire [ ADDR_WIDTH      -1 : 0 ]    write_offset,

  output wire [ ADDR_WIDTH      -1 : 0 ]    addr_out
);

`ifdef COCOTB_TOPLEVEL_agu
initial begin
  $dumpfile("agu.vcd");
  $dumpvars(0, agu);
end
`endif

endmodule

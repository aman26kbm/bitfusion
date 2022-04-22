//
// Fixed Point Multiplier
// Implements: out = in_0 * in_1 // Combinational Logic Only
//
// Hardik Sharma
// (hsharma@gatech.edu)

module umult #(
  parameter integer IN_0_WIDTH        = 8,
  parameter integer IN_1_WIDTH        = 8,
  parameter integer OUT_WIDTH         = IN_0_WIDTH == 1 ? IN_1_WIDTH : IN_1_WIDTH == 1 ? IN_0_WIDTH : IN_0_WIDTH + IN_1_WIDTH
) (
  input  wire [ IN_0_WIDTH -1 : 0]     in_0,
  input  wire [ IN_1_WIDTH -1 : 0]     in_1,
  output wire [ OUT_WIDTH  -1 : 0]     out
);

  assign out = in_0 * in_1;

endmodule;
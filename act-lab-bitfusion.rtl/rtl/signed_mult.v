//
// Signed multiplier
// Implements: out = in_0 * in_1 // Combinational Logic Only
//
// Hardik Sharma
// (hsharma@gatech.edu)

module signed_mult #(
  parameter integer IN_0_WIDTH        = 8,
  parameter integer IN_1_WIDTH        = 8,
  parameter integer OUT_WIDTH         = IN_0_WIDTH + IN_1_WIDTH
) (
  input  wire signed [ IN_0_WIDTH -1 : 0]     in_0,
  input  wire signed [ IN_1_WIDTH -1 : 0]     in_1,
  output wire signed [ OUT_WIDTH  -1 : 0]     out
);

  assign out = in_0 * in_1;

endmodule

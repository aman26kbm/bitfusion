//
// Signed Max Comparator
// Implements: out = a > b ? a : b
//
// Hardik Sharma
// (hsharma@gatech.edu)

module signed_max_comparator #(
  parameter integer IN_WIDTH              = 8,
  parameter integer OUT_WIDTH             = 8
) (
  input  wire signed [ IN_WIDTH   -1 : 0 ] a,
  input  wire signed [ IN_WIDTH   -1 : 0 ] b,
  output wire signed [ OUT_WIDTH  -1 : 0 ] out
);

assign out = a > b ? a : b;

endmodule

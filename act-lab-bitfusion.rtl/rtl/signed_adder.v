//
// Signed Adder
// Implements: out = a + b
//
// Hardik Sharma
// (hsharma@gatech.edu)

module signed_adder #(
  parameter integer IN1_WIDTH             = 8,
  parameter integer IN2_WIDTH             = 8,
  parameter integer OUT_WIDTH             = 8
) (
  input  wire signed [ IN1_WIDTH  -1 : 0 ] a,
  input  wire signed [ IN2_WIDTH  -1 : 0 ] b,
  output wire signed [ OUT_WIDTH  -1 : 0 ] out
);

assign out = a + b;

endmodule

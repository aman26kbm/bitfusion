//
// Half Adder
// Implements: Sum = Xor (in_0, in_1)
//             Carry = And (in_0, in_1)
//
// Hardik Sharma
// (hsharma@gatech.edu)

module half_adder (
  input wire in_0,
  input wire in_1,
  output wire sum,
  output wire carry
);


  assign sum = in_0 ^ in_1;
  assign carry = in_0 & in_1;

  // assign {carry, sum} = in_0 + in_1;

endmodule

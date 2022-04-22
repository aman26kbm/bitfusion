//
// Full Adder
//
// Hardik Sharma
// (hsharma@gatech.edu)

module full_adder (
  input  wire in_0,
  input  wire in_1,
  input  wire in_2,
  output wire sum,
  output wire carry
);

  assign {carry, sum} = in_0 + in_1 + in_2;
  
  // wire s1, s2;
  // wire c1, c2;

  // half_adder ha1 (in_0, in_1, s1, c1);
  // half_adder ha2 (in_2, s1, s2, c2);

  // assign sum = s2;
  // assign carry = c1 | c2;

endmodule

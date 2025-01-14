//
// Register
//
// Hardik Sharma
// (hsharma@gatech.edu)

module register_async #(
  parameter integer WIDTH                 = 8
) (
  input  wire                             clk,
  input  wire                             reset,
  input  wire                             enable,
  input  wire        [ WIDTH -1 : 0 ]     in,
  output wire        [ WIDTH -1 : 0 ]     out
);

  reg [ WIDTH -1 : 0 ] out_reg;

  always @(posedge clk or posedge reset)
  begin
    if (reset)
      out_reg <= 'b0;
    else if (enable)
      out_reg <= in;
  end

  assign out = out_reg;

endmodule

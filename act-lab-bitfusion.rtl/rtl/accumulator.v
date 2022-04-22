//
// Accumulator
// Implements: out = out + in (sel == 1)
//             out = in (sel == 0)
//
// Hardik Sharma
// (hsharma@gatech.edu)

module accumulator #(
  parameter integer IN_WIDTH              = 8,
  parameter integer OUT_WIDTH             = 8
) (
  input  wire                             clk,
  input  wire                             reset,
  input  wire                             clear,
  input  wire signed [ IN_WIDTH  -1 : 0 ] in,
  output wire signed [ OUT_WIDTH -1 : 0 ] out
);

wire signed [OUT_WIDTH-1:0] next_out = clear ? in : in + out;

register_async #(
  .WIDTH        ( OUT_WIDTH   )
) acc_reg_inst (
  .clk          ( clk         ),
  .reset        ( reset       ),
  .enable       ( 1'b1        ),
  .in           ( next_out    ),
  .out          ( out         )
);

endmodule

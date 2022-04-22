//
// Low Precision Temporal Multiply-Accumulate
//
// Hardik Sharma
// (hsharma@gatech.edu)

module signed_temporal_mult #(
  parameter integer A_WIDTH                   = 2, // Width of the first input 'a'
  parameter integer B_WIDTH                   = 4, // Width of the second input 'b'
  parameter integer ACC_WIDTH                 = 40, // Width of the Accumulator
  parameter integer MAX_PRECISION             = 16, // Max output precision supported (16 for 8x8 mult, 8 for 4x4 mult)
  // Internal use
  parameter integer MULT_OUT_WIDTH            = A_WIDTH + B_WIDTH + 2,
  parameter integer MIN_WIDTH                 = (A_WIDTH > B_WIDTH ? B_WIDTH : A_WIDTH),
  parameter integer SHIFTER_WIDTH             = $clog2(MAX_PRECISION + MAX_PRECISION -A_WIDTH-B_WIDTH + 1) - $clog2(MIN_WIDTH)
) (
  input                                       clk,
  input                                       reset,
  input                                       a_sign_mode,
  input                                       b_sign_mode,
  input  wire signed [ A_WIDTH       -1:0]    a,
  input  wire signed [ B_WIDTH       -1:0]    b,
  input  wire        [ SHIFTER_WIDTH -1:0]    shift,
  input  wire                                 sel,
  output wire signed [ ACC_WIDTH     -1:0]    out
);

//=========================================
// Wires and Regs
//=========================================
  wire signed [ MULT_OUT_WIDTH  -1 : 0 ] mult_out;
  wire signed [ ACC_WIDTH       -1 : 0 ] acc_in;
  reg  signed [ ACC_WIDTH       -1 : 0 ] acc_reg;

  wire signed [ A_WIDTH            : 0 ] a_extended;
  wire signed [ B_WIDTH            : 0 ] b_extended;

//=========================================
// Step 1: Extend a and b
// sign_mode == 0: data is unsigned
// sign_mode == 1: data is signed
//=========================================
  assign a_extended = {a_sign_mode && a[A_WIDTH-1], a};
  assign b_extended = {b_sign_mode && b[B_WIDTH-1], b};

//=========================================
// Step 2: Multiply a_extended and b_extended
//=========================================
signed_mult #(
  .IN_0_WIDTH     ( A_WIDTH + 1   ),
  .IN_1_WIDTH     ( B_WIDTH + 1   )
) signed_mult_inst (
  .in_0           ( a_extended    ),
  .in_1           ( b_extended    ),
  .out            ( mult_out      )
);

//=========================================
// Step 3: Shift the mult_out according to shift
//=========================================
shifter #(
  .IN_WIDTH       ( MULT_OUT_WIDTH  ),
  .OUT_WIDTH      ( ACC_WIDTH       ),
  .SHIFT_WIDTH    ( SHIFTER_WIDTH   ),
  .SHIFT_AMOUNT   ( MIN_WIDTH       )
) shifter_inst (
  .in             ( mult_out        ),
  .shift          ( shift           ),
  .out            ( acc_in          )
);

//=========================================
// Step 4: Accumulate the results
//=========================================

accumulator #(
  .IN_WIDTH     ( ACC_WIDTH   ),
  .OUT_WIDTH    ( ACC_WIDTH   )
) acc_inst (
  .clk          ( clk         ),
  .reset        ( reset       ),
  .clear        ( sel         ),
  .in           ( acc_in      ),
  .out          ( acc_reg     )
);
  assign out = acc_reg;

//=========================================
// Debugging: COCOTB VCD
//=========================================
`ifdef COCOTB_TOPLEVEL_lp_mult
initial begin
  $dumpfile("lp_mult.vcd");
  $dumpvars(0, lp_mult);
end
`endif

endmodule

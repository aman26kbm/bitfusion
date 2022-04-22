//
// Low Precision Multiply-Accumulate
//
// Hardik Sharma
// (hsharma@gatech.edu)

module lp_mult #(
  parameter integer IN_0_WIDTH      = 1,
  parameter integer IN_1_WIDTH      = 1,
  parameter integer ACC_WIDTH       = 16,
  parameter integer MULT_OUT_WIDTH  = IN_0_WIDTH + IN_1_WIDTH,
  parameter integer MIN_WIDTH       = (IN_0_WIDTH > IN_1_WIDTH ? IN_1_WIDTH : IN_0_WIDTH),
  //parameter integer MAX_WIDTH       = (IN_0_WIDTH > IN_1_WIDTH ? IN_0_WIDTH : IN_1_WIDTH),
  parameter integer SHIFTER_WIDTH   = $clog2(ACC_WIDTH-MULT_OUT_WIDTH) - $clog2(MIN_WIDTH)
) (
  input                                       clk,
  input                                       reset,
  input  wire signed [ IN_0_WIDTH    -1:0]    in_0,
  input  wire signed [ IN_0_WIDTH    -1:0]    in_1,
  input  wire        [ SHIFTER_WIDTH -1:0]    shift,
  input  wire                                 sel,
  output wire signed [ ACC_WIDTH     -1:0]    out
);

//=========================================
// Step 1: Multiply in_0 and in_1
//=========================================
  wire signed [ MULT_OUT_WIDTH -1 : 0 ] mult_out;
  assign mult_out = in_0 * in_1;

//=========================================
// Step 2: Shift the mult_out according to shift
//=========================================
  wire signed [ ACC_WIDTH -1 : 0 ] acc_in;
  assign acc_in = mult_out <<< (shift * MIN_WIDTH);

//=========================================
// Step 3: Accumulate the results
//=========================================
  reg signed [ ACC_WIDTH -1 : 0 ] acc_reg;
  always @(posedge clk)
  begin
    if (reset)
      acc_reg <= 0;
    else begin
      if (sel)
        acc_reg <= acc_in;
      else
        acc_reg <= acc_in + acc_reg;
    end
  end

  assign out = acc_reg;

endmodule

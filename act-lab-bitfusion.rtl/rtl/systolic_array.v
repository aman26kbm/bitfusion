//
// 2-D systolic array using Variable Precision Signed Spatial Multipliers
// Implements: out = in_0 * in_1 // Combinational Logic Only
//
// Hardik Sharma
// (hsharma@gatech.edu)

module systolic_array #(
  parameter integer ARRAY_N               = 2,
  parameter integer ARRAY_M               = 2,
  parameter integer PMAX                  = 8,
  parameter integer PMIN                  = 4,
  // Internal
  parameter integer ACT_WIDTH             = ARRAY_N * PMAX * (PMAX/PMIN),
  parameter integer WGT_WIDTH             = ARRAY_M * ARRAY_N * PMAX * (PMAX/PMIN),
  parameter integer ACCUMULATOR_WIDTH     = 4 * PMAX,
  parameter integer OUT_WIDTH             = ARRAY_M * ACCUMULATOR_WIDTH,
  parameter integer MODE_WIDTH            = $clog2(PMAX/PMIN) * 2
) (
  input  wire                               clk,
  input  wire                               reset,
  input  wire                               out_valid,
  input  wire                               acc_clear,
  input  wire        [ ACT_WIDTH  -1 : 0 ]  activation_in,
  input  wire        [ WGT_WIDTH  -1 : 0 ]  weight_in,
  input  wire        [ MODE_WIDTH -1 : 0 ]  mode,
  output wire        [ OUT_WIDTH  -1 : 0 ]  activation_out,
  output wire                               activation_valid
);

//=========================================
// Localparams
//=========================================
  localparam integer MULT_IN_WIDTH = PMAX * PMAX / PMIN;
  localparam integer MULT_OUT_WIDTH = 2 * PMAX;
  localparam integer ADDER_OUT_WIDTH = 2 * PMAX + $clog2(ARRAY_N);
  localparam integer SYSTOLIC_OUT_WIDTH = ADDER_OUT_WIDTH * ARRAY_M;
//=========================================
// Wires and Regs
//=========================================
  wire        [ OUT_WIDTH          -1 : 0 ]  accumulator_out;
  wire        [ SYSTOLIC_OUT_WIDTH -1 : 0 ]  systolic_out;

  wire        [ ARRAY_M            -1 : 0 ]  systolic_out_valid;
  wire        [ ARRAY_M            -1 : 0 ]  _systolic_out_valid;

  wire        [ ARRAY_M            -1 : 0 ]  systolic_acc_clear;
  wire        [ ARRAY_M            -1 : 0 ]  _systolic_acc_clear;
//=========================================
// Systolic Array - Begin
//=========================================
  genvar n, m;
  generate
  for (m=0; m<ARRAY_M; m=m+1)
  begin: LOOP_INPUT_FORWARD
    for (n=0; n<ARRAY_N; n=n+1)
    begin: LOOP_OUTPUT_FORWARD

      wire        [ MULT_IN_WIDTH   -1 : 0 ] a;         // Input Operand a
      wire        [ MULT_IN_WIDTH   -1 : 0 ] b;         // Input Operand b
      wire signed [ MULT_OUT_WIDTH  -1 : 0 ] mult_out;  // Output of signed spatial multiplier
      wire signed [ ADDER_OUT_WIDTH -1 : 0 ] mac_out;   // Output  of mac
      wire        [ ADDER_OUT_WIDTH -1 : 0 ] adder_out; // Output  of mac

      //==============================================================
      // Operands for the Spatial Multiplier
      // Operands are delayed by a cycles when forwarding
      if (m == 0)
      begin
        assign a = activation_in[n*MULT_IN_WIDTH+:MULT_IN_WIDTH];
      end
      else
      begin
        wire  [ MULT_IN_WIDTH -1 : 0 ] fwd_a;
        
        assign fwd_a = LOOP_INPUT_FORWARD[m-1].LOOP_OUTPUT_FORWARD[n].a;

        register_async #(MULT_IN_WIDTH) fwd_a_reg (clk, reset, 1'b1, fwd_a, a);
      end

      assign b = weight_in[(n + m*ARRAY_N)*MULT_IN_WIDTH+:MULT_IN_WIDTH];
      //==============================================================

      signed_spatial_mult #(
       .PRECISION           ( PMAX              ),  // Precision at current level
       .L_PRECISION         ( PMIN              ),  // Lowest precision
       .TOP_MODULE          ( 1                 )   // top or not
      ) mult_inst (
        .clk                ( clk               ),  // input
        .reset              ( reset             ),  // input
        .prev_level_mode    ( 2'b0              ),  // input
        .mode               ( mode              ),  // input
        .a                  ( a                 ),  // input
        .b                  ( b                 ),  // input
        .out                ( mult_out          )   // output
      );

      // Adder to accumulate partial sums
      if (n > 0)
      begin: ADD_MULT_OUT
        wire signed [ ADDER_OUT_WIDTH -1 : 0 ] prev_mac_out;
        assign prev_mac_out = LOOP_INPUT_FORWARD[m].LOOP_OUTPUT_FORWARD[n-1].adder_out;
        signed_adder #(
          .IN1_WIDTH        ( MULT_OUT_WIDTH    ),
          .IN2_WIDTH        ( ADDER_OUT_WIDTH   ),
          .OUT_WIDTH        ( ADDER_OUT_WIDTH   )
        ) adder_inst (
          .a                ( mult_out          ),
          .b                ( prev_mac_out      ),
          .out              ( mac_out           )
        );
      end
      else
      begin
        assign mac_out = mult_out;
      end

      wire enable;
      assign enable = 1'b1;
      register_async #(
        .WIDTH              ( ADDER_OUT_WIDTH   )
      ) reg_inst (
        .clk                ( clk               ),  // input
        .reset              ( reset             ),  // input
        .enable             ( enable            ),  // input
        .in                 ( mac_out           ),  // input
        .out                ( adder_out         )   // output
      );

      if (n == ARRAY_N - 1)
      begin
        assign systolic_out[m*ADDER_OUT_WIDTH+:ADDER_OUT_WIDTH] = adder_out;
      end

    end
  end
  endgenerate
//=========================================
// Systolic Array - End
//=========================================


//=========================================
// Clear and Valid signal Delay
// 2 cycle delay for clear and 1 cycle for valid
//=========================================
  register_async #(1) out_valid_delay1 (clk, reset, 1'b1, out_valid, _systolic_out_valid[0]);
  register_async #(1) out_valid_delay2 (clk, reset, 1'b1, _systolic_out_valid[0], systolic_out_valid[0]);

  register_async #(1) acc_clear_delay1 (clk, reset, 1'b1, acc_clear, _systolic_acc_clear[0]);
  assign systolic_acc_clear[0] = _systolic_acc_clear[0];

  genvar i;
  generate
  for (i=1; i<ARRAY_M; i=i+1)
  begin: CLEAR_AND_VALID
    register_async #(1) out_valid_delay2 (clk, reset, 1'b1, systolic_out_valid[i-1], systolic_out_valid[i]);
    register_async #(1) acc_clear_delay1 (clk, reset, 1'b1, systolic_acc_clear[i-1], systolic_acc_clear[i]);
  end
  endgenerate

//=========================================

//=========================================
// Output assignments
//=========================================
  assign activation_out = accumulator_out;
  assign activation_valid = |systolic_out_valid; //Liangzhen
//=========================================

//=========================================
// Accumulator
//=========================================
  generate
  for (i=0; i<ARRAY_M; i=i+1)
  begin: ACCUMULATOR

    wire acc_clr;
    wire [ADDER_OUT_WIDTH-1:0] acc_in;
    wire [ACCUMULATOR_WIDTH-1:0] acc_out;
    wire acc_out_valid;

    assign acc_clr = systolic_acc_clear[i];
    assign acc_in = systolic_out[i * ADDER_OUT_WIDTH +: ADDER_OUT_WIDTH];
    assign accumulator_out[ACCUMULATOR_WIDTH*i+:ACCUMULATOR_WIDTH] = acc_out;
    assign acc_out_valid = systolic_out_valid[i];

    accumulator #(
      .IN_WIDTH           ( ADDER_OUT_WIDTH     ),
      .OUT_WIDTH          ( ACCUMULATOR_WIDTH   )
    ) acc_inst (
      .clk                ( clk                 ),
      .reset              ( reset               ),
      .clear              ( acc_clr             ),
      .in                 ( acc_in              ),
      .out                ( acc_out             )
    );
  end
  endgenerate
//=========================================

`ifdef COCOTB_TOPLEVEL_systolic_array
initial begin
  $dumpfile("systolic_array.vcd");
  $dumpvars(0, systolic_array);
end
`endif

endmodule

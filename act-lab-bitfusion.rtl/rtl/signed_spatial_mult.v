//
// Spatial: Low Precision Multiply-Accumulate
//
// Mode 0: 2K x 2K
// Mode 1: 2K x 1K
// Mode 2: 1K x 2K
// Mode 3: 1K x 1K
//
// Hardik Sharma
// (hsharma@gatech.edu)

module signed_spatial_mult #(
  parameter integer PRECISION                     = 8,                                   // Precision at current level
  parameter integer L_PRECISION                   = 2,                                    // Lowest precision
  parameter integer TOP_MODULE                    = 1,                                    // 1: top or 0: not
  parameter integer A_SIGN_EXTEND                 = 0,                                    // 1: extend or 0: not
  parameter integer B_SIGN_EXTEND                 = 0,                                    // 1: extend or 0: not
  parameter integer IN_WIDTH                      = (PRECISION/L_PRECISION) * PRECISION,  // Input width at current level
  parameter integer A_WIDTH                       = IN_WIDTH,                             // A's width at current level
  parameter integer B_WIDTH                       = IN_WIDTH,                             // B's width at current level
  parameter integer OUT_WIDTH                     = PRECISION * 2 + A_SIGN_EXTEND + B_SIGN_EXTEND,                        // Output width at current level
  parameter integer NUM_LEVELS                    = $clog2(PRECISION/L_PRECISION),        // Number of levels in the spatial multiplier. 8:4:2:1 mult has 3 levels
  parameter integer MODE_WIDTH                    = 2 * NUM_LEVELS,                       // Mode width. Every level needs 2 bits
  parameter integer HALF_PRECISION                = PRECISION / 2                         // Half of current level's precision
) (
  input                                           clk,
  input                                           reset,
  input  wire        [ 2              -1 : 0 ]    prev_level_mode,
  input  wire        [ MODE_WIDTH     -1 : 0 ]    mode,
  input  wire        [ A_WIDTH        -1 : 0 ]    a,
  input  wire        [ B_WIDTH        -1 : 0 ]    b,
  output wire        [ OUT_WIDTH      -1 : 0 ]    out
);


genvar ii, jj, kk;
generate

    // Sign mode
    // Required when A_SIGN_EXTEND == 1 or B_SIGN_EXTEND == 1
    // This means that the sign for the MSB bits of an input depend on the higher level mode, instead of the current level mode
    wire [2-1:0] higher_level_mode;
    if (TOP_MODULE == 1)
      assign higher_level_mode = 2'b0;
    else
      assign higher_level_mode = prev_level_mode;


    localparam integer A_SIGNED_WIDTH = A_WIDTH + A_SIGN_EXTEND;
    localparam integer B_SIGNED_WIDTH = B_WIDTH + B_SIGN_EXTEND;

    wire signed [ A_SIGNED_WIDTH -1 : 0 ] a_signed;
    wire signed [ B_SIGNED_WIDTH -1 : 0 ] b_signed;
    wire signed [ OUT_WIDTH      -1 : 0 ] out_signed;

    wire a_mode, b_mode;
    assign {a_mode, b_mode} = prev_level_mode;
    assign a_signed = {a_mode && a[IN_WIDTH-1], a};
    assign b_signed = {b_mode && b[IN_WIDTH-1], b};

//=========================================
// Generate FULL/HALF precision multilpier
//=========================================
  if (PRECISION == L_PRECISION)
  begin: FULL_PRECISION // Full Precision

    assign out_signed = a_signed * b_signed;
    assign out = out_signed;
  end

  else
  begin: LP_MULT_INST

    wire [1:0] curr_level_mode = mode[MODE_WIDTH-1:MODE_WIDTH-2];

//=========================================
// Step 1: Operand Select
//
// -------------
// | a_3 | a_2 |
// -------------
// | a_1 | a_0 |
// -------------
// Transpose required at Top Level for B
// -------------
// | b_3 | b_2 |
// -------------
// | b_1 | b_0 |
// -------------
//
//=========================================

    localparam integer LP_MULT_IN_W = IN_WIDTH / 4;

    wire [ LP_MULT_IN_W - 1 : 0 ] a_0;
    wire [ LP_MULT_IN_W - 1 : 0 ] a_1;
    wire [ LP_MULT_IN_W - 1 : 0 ] a_2;
    wire [ LP_MULT_IN_W - 1 : 0 ] a_3;

    wire [ LP_MULT_IN_W - 1 : 0 ] b_0;
    wire [ LP_MULT_IN_W - 1 : 0 ] b_1;
    wire [ LP_MULT_IN_W - 1 : 0 ] b_2;
    wire [ LP_MULT_IN_W - 1 : 0 ] b_3;

    localparam integer II_MAX = PRECISION/(L_PRECISION*2);
    localparam integer JJ_MAX = PRECISION/(L_PRECISION*2); 

    if (TOP_MODULE == 1)
    begin: B_TRANSPOSE
      for (ii=0; ii<II_MAX; ii=ii+1)
      begin: LOOP_II
        for (jj=0; jj<JJ_MAX; jj=jj+1)
        begin: LOOP_JJ
          for (kk=0; kk<L_PRECISION; kk=kk+1)
          begin: LOOP_KK
            assign b_0[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((ii + 0     )+(jj + 0     )*JJ_MAX*2)];
            assign b_1[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((ii + 0     )+(jj + II_MAX)*JJ_MAX*2)];
            assign b_2[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((ii + JJ_MAX)+(jj + 0     )*JJ_MAX*2)];
            assign b_3[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((ii + JJ_MAX)+(jj + II_MAX)*JJ_MAX*2)];
          end
        end
      end
    end else
    begin
      for (ii=0; ii<II_MAX; ii=ii+1)
      begin: LOOP_II
        for (jj=0; jj<JJ_MAX; jj=jj+1)
        begin: LOOP_JJ
          for (kk=0; kk<L_PRECISION; kk=kk+1)
          begin: LOOP_KK
            assign b_0[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((jj + 0     )+(ii + 0     )*JJ_MAX*2)];
            assign b_1[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((jj + JJ_MAX)+(ii + 0     )*JJ_MAX*2)];
            assign b_2[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((jj + 0     )+(ii + II_MAX)*JJ_MAX*2)];
            assign b_3[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((jj + JJ_MAX)+(ii + II_MAX)*JJ_MAX*2)];
          end
        end
      end
    end

    for (ii=0; ii<II_MAX; ii=ii+1)
    begin: LOOP_II
      for (jj=0; jj<JJ_MAX; jj=jj+1)
      begin: LOOP_JJ
        for (kk=0; kk<L_PRECISION; kk=kk+1)
        begin: LOOP_KK
          assign a_0[kk+L_PRECISION*(jj+ii*JJ_MAX)] = a[kk+L_PRECISION*((jj + 0     )+(ii + 0     )*JJ_MAX*2)];
          assign a_1[kk+L_PRECISION*(jj+ii*JJ_MAX)] = a[kk+L_PRECISION*((jj + JJ_MAX)+(ii + 0     )*JJ_MAX*2)];
          assign a_2[kk+L_PRECISION*(jj+ii*JJ_MAX)] = a[kk+L_PRECISION*((jj + 0     )+(ii + II_MAX)*JJ_MAX*2)];
          assign a_3[kk+L_PRECISION*(jj+ii*JJ_MAX)] = a[kk+L_PRECISION*((jj + JJ_MAX)+(ii + II_MAX)*JJ_MAX*2)];
        end
      end
    end

//=========================================
// Half Precision Multipliers
//=========================================

    // Partial Products
    wire signed [ PRECISION + 1             + 1             -1 : 0 ] pp_0;
    wire signed [ PRECISION + A_SIGN_EXTEND + 1             -1 : 0 ] pp_1;
    wire signed [ PRECISION + 1             + B_SIGN_EXTEND -1 : 0 ] pp_2;
    wire signed [ PRECISION + A_SIGN_EXTEND + B_SIGN_EXTEND -1 : 0 ] pp_3;

    wire [MODE_WIDTH-3:0] lower_level_mode;
    if (PRECISION == L_PRECISION*2)
    begin: LAST_LEVEL
      assign lower_level_mode = 'b0;
    end
    else
    begin: NEXT_LEVEL
      assign lower_level_mode = mode[MODE_WIDTH-3:0];
    end

    wire [2-1:0] m0_sign_mode;
    wire [2-1:0] m1_sign_mode;
    wire [2-1:0] m2_sign_mode;
    wire [2-1:0] m3_sign_mode;

    assign m0_sign_mode = curr_level_mode;
    assign m1_sign_mode = {higher_level_mode[1], curr_level_mode[0]};
    assign m2_sign_mode = {curr_level_mode[1], higher_level_mode[0]};
    assign m3_sign_mode = higher_level_mode;

    signed_spatial_mult #(HALF_PRECISION, L_PRECISION, 0, 1            , 1            ) m0 (clk, reset, m0_sign_mode, lower_level_mode, a_0, b_0, pp_0);
    signed_spatial_mult #(HALF_PRECISION, L_PRECISION, 0, A_SIGN_EXTEND, 1            ) m1 (clk, reset, m1_sign_mode, lower_level_mode, a_1, b_1, pp_1);
    signed_spatial_mult #(HALF_PRECISION, L_PRECISION, 0, 1            , B_SIGN_EXTEND) m2 (clk, reset, m2_sign_mode, lower_level_mode, a_2, b_2, pp_2);
    signed_spatial_mult #(HALF_PRECISION, L_PRECISION, 0, A_SIGN_EXTEND, B_SIGN_EXTEND) m3 (clk, reset, m3_sign_mode, lower_level_mode, a_3, b_3, pp_3);
//=========================================

//=========================================
// Step 2: Shift
// Mode:
//  0: 2Kx2K
//  1: 2KxK
//  2: Kx2K
//  3: KxK
//=========================================
    wire signed [OUT_WIDTH-1:0] spp_0;
    wire signed [OUT_WIDTH-1:0] spp_1;
    wire signed [OUT_WIDTH-1:0] spp_2;
    wire signed [OUT_WIDTH-1:0] spp_3;

    reg [1:0] s_0;
    reg [1:0] s_1;
    reg [1:0] s_2;
    reg [1:0] s_3;

    // Shift amounts
    always @(*) begin
      case (curr_level_mode)
        0: begin
          s_0 = 2'd0;
          s_1 = 2'd1;
          s_2 = 2'd1;
          s_3 = 2'd2;
        end
        1: begin
          s_0 = 2'd0;
          s_1 = 2'd1;
          s_2 = 2'd0;
          s_3 = 2'd1;
        end
        2: begin
          s_0 = 2'd0;
          s_1 = 2'd0;
          s_2 = 2'd1;
          s_3 = 2'd1;
        end
        3: begin
          s_0 = 2'd0;
          s_1 = 2'd0;
          s_2 = 2'd0;
          s_3 = 2'd0;
        end
      endcase
    end

    // generate shifted partial products
    assign spp_0 = pp_0 <<< (s_0 * HALF_PRECISION);
    assign spp_1 = pp_1 <<< (s_1 * HALF_PRECISION);
    assign spp_2 = pp_2 <<< (s_2 * HALF_PRECISION);
    assign spp_3 = pp_3 <<< (s_3 * HALF_PRECISION);
//=========================================

//=========================================
// Step 3: ADD
// out = spp_0 + spp_1 + spp_2 + spp_3
//=========================================
    assign out = spp_0 + spp_1 + spp_2 + spp_3;
//=========================================
  end // Half Precision End
  endgenerate

//=========================================
// Debugging: COCOTB VCD
//=========================================
`ifdef COCOTB_TOPLEVEL_signed_spatial_mult
if (TOP_MODULE == 1)
begin
  initial begin
    $dumpfile("signed_spatial_mult.vcd");
    $dumpvars(0, signed_spatial_mult);
  end
end
`endif

endmodule

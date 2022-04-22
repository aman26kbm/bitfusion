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

module spatial_mult #(
  parameter integer PRECISION                     = 16,                                    // Precision at current level
  parameter integer L_PRECISION                   = 1,                                    // Lowest precision
  parameter integer TOP_MODULE                    = 1,                                    // top or not
  parameter integer HALF_PRECISION                = PRECISION / 2,                        // Half of current level's precision
  parameter integer IN_WIDTH                      = (PRECISION/L_PRECISION) * PRECISION,  // Input width at current level
  parameter integer OUT_WIDTH                     = PRECISION * 2,                        // Output width at current level
  parameter integer NUM_LEVELS                    = $clog2(PRECISION/L_PRECISION),        // Number of levels in the spatial multiplier. 8:4:2:1 mult has 3 levels
  parameter integer MODE_WIDTH                    = 2 * NUM_LEVELS                        // Mode width. Every level needs 2 bits
) (
  input                                           clk,
  input                                           reset,
  input  wire        [ MODE_WIDTH     -1 : 0 ]    mode,
  input  wire        [ IN_WIDTH       -1 : 0 ]    a,
  input  wire        [ IN_WIDTH       -1 : 0 ]    b,
  output wire        [ OUT_WIDTH      -1 : 0 ]    out
);

genvar ii, jj, kk;
  generate
//=========================================
// Generate FULL/HALF precision multilpier
//=========================================
  if (PRECISION == L_PRECISION) begin // Full Precision
    assign out = a * b;
  end

  else
  begin: LP_MULT_INST

//=========================================
// Step 1: Mux
// Mode:
//  0: 2Kx2K:
//  a_0, a_2 = a[0]; a_1, a_3 = a[1]
//  b_0, b_2 = b[0]; b_1, b_3 = b[1]
//  1: 2KxK : a_0
//  a_0, a_2 = a[0]; a_1, a_3 = a[1]
//  b_0 = b[0]; b_1 = b[1]; b_2 = b[2]; b_3 = b[3]
//  2: Kx2K
//  a_0 = a[0]; a_1 = a[1]; a_2 = a[2]; a_3 = a[3]
//  b_0, b_2 = b[0]; b_1, b_3 = b[1]
//  3: KxK
//  a_0 = a[0]; a_1 = a[1]; a_2 = a[2]; a_3 = a[3]
//  b_0 = b[0]; b_1 = b[1]; b_2 = b[2]; b_3 = b[3]
//=========================================

    wire [1:0] curr_level_mode = mode[MODE_WIDTH-1:MODE_WIDTH-2];
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
    begin: TOP_MODULE_SWIZZLE
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
  
            assign b_0[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((ii + 0     )+(jj + 0     )*JJ_MAX*2)];
            assign b_1[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((ii + 0     )+(jj + II_MAX)*JJ_MAX*2)];
            assign b_2[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((ii + JJ_MAX)+(jj + 0     )*JJ_MAX*2)];
            assign b_3[kk+L_PRECISION*(jj+ii*JJ_MAX)] = b[kk+L_PRECISION*((ii + JJ_MAX)+(jj + II_MAX)*JJ_MAX*2)];
          end
        end
      end
    end else
    begin
      assign {a_3, a_2, a_1, a_0} = a;
      assign {b_3, b_2, b_1, b_0} = b;
    end

    
//=========================================
// Half Precision Multipliers
//=========================================

    // Partial Products
    wire [PRECISION-1:0] pp_0;
    wire [PRECISION-1:0] pp_1;
    wire [PRECISION-1:0] pp_2;
    wire [PRECISION-1:0] pp_3;

    if (PRECISION == L_PRECISION*2) begin
      assign pp_0 = a_0 * b_0;
      assign pp_1 = a_1 * b_1;
      assign pp_2 = a_2 * b_2;
      assign pp_3 = a_3 * b_3;
    end
    else begin
      // assign pp_0 = a_0 * b_0;
      // assign pp_1 = a_1 * b_2;
      // assign pp_2 = a_2 * b_1;
      // assign pp_3 = a_3 * b_3;
      wire [MODE_WIDTH-3:0] lower_level_mode = mode[MODE_WIDTH-3:0];
      spatial_mult #(HALF_PRECISION, L_PRECISION, 0) mult_0(clk, reset, lower_level_mode, a_0, b_0, pp_0);
      spatial_mult #(HALF_PRECISION, L_PRECISION, 0) mult_1(clk, reset, lower_level_mode, a_1, b_1, pp_1);
      spatial_mult #(HALF_PRECISION, L_PRECISION, 0) mult_2(clk, reset, lower_level_mode, a_2, b_2, pp_2);
      spatial_mult #(HALF_PRECISION, L_PRECISION, 0) mult_3(clk, reset, lower_level_mode, a_3, b_3, pp_3);
    end
//=========================================

//=========================================
// Step 2: Shift
// Mode:
//  0: 2Kx2K
//  1: 2KxK
//  2: Kx2K
//  3: KxK
//=========================================
    wire [OUT_WIDTH-1:0] spp_0;
    wire [OUT_WIDTH-1:0] spp_1;
    wire [OUT_WIDTH-1:0] spp_2;
    wire [OUT_WIDTH-1:0] spp_3;
    
    reg [1:0] s_0;
    reg [1:0] s_1;
    reg [1:0] s_2;
    reg [1:0] s_3;
    
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
    assign spp_0 = pp_0 << (s_0 * HALF_PRECISION);
    assign spp_1 = pp_1 << (s_1 * HALF_PRECISION);
    assign spp_2 = pp_2 << (s_2 * HALF_PRECISION);
    assign spp_3 = pp_3 << (s_3 * HALF_PRECISION);
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
`ifdef COCOTB_TOPLEVEL_spatial_mult
if (TOP_MODULE == 1)
begin
  initial begin
    $dumpfile("spatial_mult.vcd");
    $dumpvars(0, spatial_mult);
  end
end
`endif

endmodule

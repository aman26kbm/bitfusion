//
// Spatial: Muxing logic for inputs
//
// Hardik Sharma
// (hsharma@gatech.edu)

module spatial_mult_mux #(
  parameter integer PRECISION                     = 8,                                    // Precision at current level
  parameter integer L_PRECISION                   = 2,                                    // Lowest precision
  parameter integer IN_WIDTH                      = (PRECISION/L_PRECISION) * PRECISION,  // Input width at current level
  parameter integer OUT_WIDTH                     = IN_WIDTH,                             // Output width is the same as input width
  parameter integer NUM_BANKS                     = IN_WIDTH / PRECISION,                 // Number of banks of SRAM required
  parameter integer NUM_LEVELS                    = $clog2(PRECISION/L_PRECISION),        // Number of levels in the spatial multiplier. 8:4:2:1 mult has 3 levels
  parameter integer MODE_WIDTH                    = NUM_LEVELS,                           // Mode width. Every level needs 1 bit ( Mux is for just one operand )
  parameter integer ADDR_WIDTH                    = $clog2(NUM_BANKS),                    // Address width
  parameter integer PREC_MODE_WIDTH               = $clog2(ADDR_WIDTH + 1)                // Precision Mode width
) (
  input                                           clk,
  input                                           reset,
  input  wire        [ ADDR_WIDTH     -1 : 0 ]    addr,
  input  wire        [ PREC_MODE_WIDTH-1 : 0 ]    precision_mode,
  input  wire        [ IN_WIDTH       -1 : 0 ]    data_in,
  output wire        [ OUT_WIDTH      -1 : 0 ]    data_out
);


genvar ii, oo;
// Generate statement for Muxes
generate
for (oo=0; oo<NUM_BANKS; oo=oo+1)
begin: LOOP_OUT_BANKS

  wire [ ADDR_WIDTH -1 : 0 ] sel;

  sel_gen #(
    .NUM_BANKS      ( NUM_BANKS         ),
    .BANK_ID        ( oo                )
  ) sel_inst (
    .addr           ( addr              ),
    .precision_mode ( precision_mode    ),
    .sel            ( sel               )
  );

  wire [ PRECISION - 1 : 0 ] mux_out;
  assign data_out[oo*PRECISION+:PRECISION] = mux_out;

  mux_n_1 #(
    .WIDTH          ( PRECISION         ),
    .LOG2_N         ( ADDR_WIDTH        )
  ) mux_inst (
    .sel            ( sel               ),
    .data_in        ( data_in           ),
    .data_out       ( mux_out           )
  );

end
endgenerate


endmodule

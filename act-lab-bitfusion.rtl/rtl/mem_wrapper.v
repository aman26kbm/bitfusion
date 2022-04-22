//
// Wrapper for activation memory
//
// Hardik Sharma
// (hsharma@gatech.edu)

module mem_wrapper #(
  parameter integer PMAX          = 8,                // Max Precision
  parameter integer PMIN          = 2,                // Min Precision
  parameter integer NUM_BANKS     = PMAX / PMIN,      // Num Data
  parameter integer DATA_WIDTH    = PMAX * NUM_BANKS,
  parameter integer ADDR_WIDTH    = $clog2(NUM_BANKS),
  parameter integer PMODE_WIDTH   = $clog2(NUM_BANKS), // Width of precision mode
  parameter integer MEM_DEPTH     = (1 << ADDR_WIDTH)
) (
  input  wire                                     clk,
  input  wire                                     reset,
  input  wire        [ PMODE_WIDTH    -1 : 0 ]    precision_mode,
  input  wire        [ ADDR_WIDTH     -1 : 0 ]    addr,
  input  wire        [ DATA_WIDTH     -1 : 0 ]    data_in,
  output wire        [ DATA_WIDTH     -1 : 0 ]    data_out
);

//=========================================
// Wires/Regs
//=========================================
//=========================================

  spatial_mult_mux #(
    .PRECISION                ( PMAX            ),  // Precision at current level
    .L_PRECISION              ( PMIN            ),  // Lowest precision
    .IN_WIDTH                 ( DATA_WIDTH      ),  // Input width at current level
    .NUM_BANKS                ( NUM_BANKS       ),  // Number of banks of SRAM required
    .NUM_LEVELS               ( ADDR_WIDTH      )   // Number of levels in the spatial multiplier. 8:4:2:1 mult has 3 levels
  ) mult_mux (
    .clk                      ( clk             ),
    .reset                    ( reset           ),
    .addr                     ( addr            ),
    .precision_mode           ( precision_mode  ),
    .data_in                  ( data_in         ),
    .data_out                 ( data_out        )
  );


endmodule

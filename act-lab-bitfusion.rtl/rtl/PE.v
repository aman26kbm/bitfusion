//
// PE with multiplier, shifter, and accumulator
//
// Hardik Sharma
// (hsharma@gatech.edu)

module PE #(
  parameter integer IN_0_WIDTH          = 8,
  parameter integer IN_1_WIDTH          = 8,
  parameter integer ACC_WIDTH           = 16,
  parameter integer MULT_OUT_WIDTH      = IN_0_WIDTH + IN_1_WIDTH,
  parameter integer SHIFTER_DATA_WIDTH  = MULT_OUT_WIDTH,
  parameter integer SHIFT_WIDTH         = $clog2(ACC_WIDTH)
) (
  input  wire                           clk,
  input  wire                           reset,
  input  wire                           sel,
  input  wire [ SHIFT_WIDTH-1 : 0 ]     shift,
  input  wire [ IN_0_WIDTH -1 : 0 ]     in_0,
  input  wire [ IN_1_WIDTH -1 : 0 ]     in_1,
  output wire [ ACC_WIDTH  -1 : 0 ]     out
);

// ============================================
// Wires
// ============================================
wire [ IN_0_WIDTH         -1 : 0 ]      mult_in_0;
wire [ IN_1_WIDTH         -1 : 0 ]      mult_in_1;
wire [ MULT_OUT_WIDTH     -1 : 0 ]      mult_out;

wire [ SHIFTER_DATA_WIDTH -1 : 0 ]      shifter_in;
wire [ ACC_WIDTH          -1 : 0 ]      shifter_out;

wire [ SHIFTER_DATA_WIDTH -1 : 0 ]      acc_in;
wire [ ACC_WIDTH          -1 : 0 ]      acc_out;
wire                                    acc_sel;

// ============================================
// Assignments
// ============================================
assign mult_in_0 = in_0;
assign mult_in_1 = in_1;

assign shifter_in = mult_out;

assign acc_in = shifter_out;
assign acc_sel = sel;
assign out = acc_out;


// ============================================
// Instantiations
// ============================================
mult_fxp #(
  .IN_0_WIDTH       ( IN_0_WIDTH          ),
  .IN_1_WIDTH       ( IN_1_WIDTH          )
) multiplier_unit (
  .in_0             ( mult_in_0           ),
  .in_1             ( mult_in_1           ),
  .out              ( mult_out            )
);

shifter #(
  .IN_WIDTH         ( SHIFTER_DATA_WIDTH  ),
  .OUT_WIDTH        ( ACC_WIDTH           )
) shifter_unit (
  .in               ( shifter_in          ),
  .shift            ( shift               ),
  .out              ( shifter_out         )
);

accumulator #(
  .IN_WIDTH         ( ACC_WIDTH           ),
  .OUT_WIDTH        ( ACC_WIDTH           )
) accumulator_unit (
  .clk              ( clk                 ),
  .reset            ( reset               ),
  .in               ( acc_in              ),
  .sel              ( acc_sel             ),
  .out              ( acc_out             )
);

endmodule

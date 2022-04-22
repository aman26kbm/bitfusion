//
// Register File: Single Port
//
// Hardik Sharma
// (hsharma@gatech.edu)

module register_file_sp #(
  parameter integer DATA_WIDTH             = 8,
  parameter integer ADDR_WIDTH             = 8,
  // Internal use
  parameter integer DEPTH                  = 1 << ADDR_WIDTH
) (
  input  wire                              clk,
  input  wire                              enable,  // Enable 
  input  wire                              wr,      // 1: Write, 0: Read
  input  wire        [ ADDR_WIDTH -1 : 0 ] write_addr,
  input  wire        [ DATA_WIDTH -1 : 0 ] write_data,
  input  wire        [ ADDR_WIDTH -1 : 0 ] read_addr,
  output reg         [ DATA_WIDTH -1 : 0 ] read_data
);

// Register FILE
  reg [ DATA_WIDTH -1 : 0 ] regfile [ 0 : DEPTH -1 ];

  always @(posedge clk)
  begin: RD_REG_FILE
    if (enable && !wr)
      read_data <= regfile[read_addr];
  end

  always @(posedge clk)
  begin: WR_REG_FILE
    if (enable && wr)
      regfile[write_addr] <= write_data;
  end

endmodule

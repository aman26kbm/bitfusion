//
// Generates Select logic for muxes in Spatial Multiplier
//
// Hardik Sharma
// (hsharma@gatech.edu)

module sel_gen #(
  parameter integer NUM_BANKS   = 2,
  parameter integer BANK_ID     = 1,
  parameter integer ADDR_WIDTH  = $clog2(NUM_BANKS),
  parameter integer MODE_WIDTH  = $clog2(ADDR_WIDTH + 1),
  parameter integer MAX_MODE    = ADDR_WIDTH + 1,
  parameter integer SEL_WIDTH   = ADDR_WIDTH
) (
  input  wire        [ ADDR_WIDTH     -1 : 0 ]    addr,
  input  wire        [ MODE_WIDTH     -1 : 0 ]    precision_mode,
  output wire        [ SEL_WIDTH      -1 : 0 ]    sel
);

genvar ii;
generate
if (NUM_BANKS == 2)
begin
  assign sel = BANK_ID == 0 ? addr[0] : precision_mode[0] == 1'b0 ? addr[0] : 1'b1;
end
else if (NUM_BANKS > 2)
begin
  for (ii=0; ii<MAX_MODE-1; ii=ii+1)
  begin
    wire [ADDR_WIDTH-1:0] bank_id;
    assign bank_id = BANK_ID;
    assign sel = precision_mode == ii ? {addr[ADDR_WIDTH-ii-1:0], bank_id} >> (MAX_MODE - ii - 1) : 'bz;
  end
  assign sel = precision_mode == MAX_MODE-1 ? BANK_ID : 'bz;
end
endgenerate

endmodule

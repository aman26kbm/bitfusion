//
// Loop Controller
//
// (1) RAM to hold loop instructions (max iter count)
// (2) RAM to hold loop states (current iter count)
// (3) FSM that starts when we get the start signal, stops when done
// (4) Stack for the head pointer
//
// Hardik Sharma
// (hsharma@gatech.edu)

module controller #(
  parameter integer LOOP_COUNT_W                  = 8,
  parameter integer INST_ADDR_W                   = 4,
  // Internal Parameters
  parameter integer LOOP_STATE_W                  = LOOP_COUNT_W,
  parameter integer OFFSET_W                      = INST_ADDR_W,
  parameter integer STACK_W                       = LOOP_COUNT_W + LOOP_STATE_W,
  parameter integer STACK_DEPTH                   = (1 << INST_ADDR_W)
) (
  input  wire                                     clk,
  input  wire                                     reset,

  // Start and Done handshake signals
  input  wire                                     start,
  output wire                                     done,

  // Loop instruction valid
  input  wire                                     loop_wr_v,
  // Loop instruction iteration count
  input  wire       [ LOOP_COUNT_W    -1 : 0 ]    loop_wr_max_iter,

  output wire       [ OFFSET_W        -1 : 0 ]    offset_index,
  output wire                                     offset_index_valid
);


//=============================================================
// Wires/Regs
//=============================================================
  wire exit_loop;

  reg  [ INST_ADDR_W    -1 : 0 ]    max_loop_ptr;
  reg  [ INST_ADDR_W    -1 : 0 ]    loop_wr_ptr;
  wire [ INST_ADDR_W    -1 : 0 ]    loop_rd_ptr;

  wire [ LOOP_COUNT_W   -1 : 0 ]    loop_rd_max;

  wire [ INST_ADDR_W    -1 : 0 ]    iter_wr_ptr;
  wire                              iter_wr_v;
  wire [ LOOP_COUNT_W   -1 : 0 ]    iter_wr_data;

  reg  [ INST_ADDR_W    -1 : 0 ]    iter_rd_ptr;
  wire                              iter_rd_v;
  wire [ LOOP_COUNT_W   -1 : 0 ]    iter_rd_data;

  reg  [ INST_ADDR_W    -1 : 0 ]    stall_rd_ptr;

  reg  [ 2              -1 : 0 ]    state;
  reg  [ 2              -1 : 0 ]    next_state;

  reg  [ INST_ADDR_W    -1 : 0 ]    exit_loop_count;

//=============================================================

//=============================================================
// Loop Instruction Buffer
//=============================================================

  always @(posedge clk)
  begin:WR_PTR
    if (reset)
      loop_wr_ptr <= 'b0;
    else begin
      if (loop_wr_v)
        loop_wr_ptr <= loop_wr_ptr + 1'b1;
      else if (done)
        loop_wr_ptr <= 'b0;
    end
  end

  always @(posedge clk)
  begin: MAX_LOOP_PTR
    if (loop_wr_v)
      max_loop_ptr <= loop_wr_ptr;
  end

  assign loop_rd_v = iter_rd_v;
  assign loop_rd_ptr = iter_rd_ptr;

  /*
  * This module stores the loop max iterations.
  */
  ram #(
    .ADDR_WIDTH                     ( INST_ADDR_W         ),
    .DATA_WIDTH                     ( LOOP_COUNT_W        )
  ) loop_buf (
    .clk                            ( clk                 ),
    .reset                          ( reset               ),
    .s_write_addr                   ( loop_wr_ptr         ),
    .s_write_req                    ( loop_wr_v           ),
    .s_write_data                   ( loop_wr_max_iter    ),
    .s_read_addr                    ( loop_rd_ptr         ),
    .s_read_req                     ( loop_rd_v           ),
    .s_read_data                    ( loop_rd_max         )
  );
//=============================================================

//=============================================================
// Loop Counters
//=============================================================
  /*
  * This module stores the current loop iterations.
  */

  ram #(
    .ADDR_WIDTH                     ( INST_ADDR_W         ),
    .DATA_WIDTH                     ( LOOP_COUNT_W        )
  ) iter_buf (
    .clk                            ( clk                 ),
    .reset                          ( reset               ),
    .s_write_addr                   ( iter_wr_ptr         ),
    .s_write_req                    ( iter_wr_v           ),
    .s_write_data                   ( iter_wr_data        ),
    .s_read_addr                    ( iter_rd_ptr         ),
    .s_read_req                     ( iter_rd_v           ),
    .s_read_data                    ( iter_rd_data        )
  );
//=============================================================

//=============================================================
// FSM
//=============================================================

  localparam integer IDLE   = 0;
  localparam integer BUSY   = 1;
  localparam integer ENTER  = 2;
  localparam integer RETURN = 3;

  always @(*)
  begin
    next_state = state;
    case (state)
      IDLE: begin
        if (start)
          next_state = BUSY;
      end
      BUSY: begin
        if (done)
          next_state = IDLE;
        else if (exit_loop)
          next_state = ENTER;
      end
      ENTER: begin
        if (done)
          next_state = IDLE;
        else if (!exit_loop)
          next_state = RETURN;
      end
      RETURN: begin
        if (exit_loop_count == 1)
          next_state = BUSY;
      end
    endcase
  end

  always @(posedge clk or posedge reset)
  begin
    if (reset)
      state <= 2'b0;
    else
      state <= next_state;
  end

//=============================================================

//=============================================================
  // Loop Iteration logic:
  //
  // Set iter counts to zero when initializing the max iters
  // Otherwise, increment write pointer and read pointer every
  // cycle
  //   max_loop_ptr keeps track of the last loop
  //   iter_rd signals correspond to the current iter count
  //   exit_loop whenever the current count == max count
//=============================================================
  assign done = (iter_rd_ptr == max_loop_ptr) && exit_loop;
  assign iter_rd_v = state != IDLE;

  assign iter_wr_v = state == IDLE ? loop_wr_v : state != RETURN;
  assign iter_wr_data = state == IDLE ? 'b0 :
                        exit_loop ? 'b0 : iter_rd_data + 1'b1;
  assign iter_wr_ptr = state == IDLE ? loop_wr_ptr : iter_rd_ptr;


  assign exit_loop = iter_rd_data == loop_rd_max;

  // Read address
  always @(posedge clk)
  begin: RD_PTR
    if (state != IDLE && exit_loop)
      iter_rd_ptr <= iter_rd_ptr + 1'b1;
    else
      iter_rd_ptr <= 'b0;
  end

  // Count number of loops exited
  always @(posedge clk)
  begin: ENTER_LOOP_COUNTER
    if (reset)
      exit_loop_count <= 'b0;
    else begin
      if (exit_loop)
        exit_loop_count <= exit_loop_count + 1'b1;
      else if (state == RETURN)
        exit_loop_count <= exit_loop_count - 1'b1;
      else if (start)
        exit_loop_count <= 'b0;
    end
  end

//=============================================================


//=============================================================
// OFFSET generation
//=============================================================

  assign offset_index = (state != RETURN) ? iter_rd_ptr : exit_loop_count;
  assign offset_index_valid = (state == BUSY || state == ENTER) && !exit_loop;

//=============================================================


//=============================================================
// VCD
//=============================================================
`ifdef COCOTB_TOPLEVEL_controller
initial begin
  $dumpfile("controller.vcd");
  $dumpvars(0, controller);
end
`endif
//=============================================================

endmodule

/**
 * File              : encrypt.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 17.06.2026
 * Last Modified Date: 17.06.2026
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module encrypt #(
    parameter N = 16,
    parameter M = 4,
    parameter T = 32
) (
    input clk,
    input rst,
    input start,
    input [N-1:0] round_keys[T-1:0],
    input [(N<<1)-1:0] blk_i,
    output [(N<<1)-1:0] blk_o,
    output logic end_signal
);

  assign blk_o = {x_reg_dout, y_reg_dout};

  logic x_reg_cl;
  logic x_reg_w;
  logic [N-1:0] x_reg_din;
  logic [N-1:0] x_reg_dout;

  register #(
      .DATA_WIDTH(N)
  ) x_reg (
      .clk(clk),
      .cl(x_reg_cl),
      .w(x_reg_w),
      .din(x_reg_din),
      .dout(x_reg_dout)
  );

  logic y_reg_cl;
  logic y_reg_w;
  logic [N-1:0] y_reg_din;
  logic [N-1:0] y_reg_dout;

  register #(
      .DATA_WIDTH(N)
  ) y_reg (
      .clk(clk),
      .cl(y_reg_cl),
      .w(y_reg_w),
      .din(y_reg_din),
      .dout(y_reg_dout)
  );

  logic [N-1:0] rf_impl_x_new, rf_impl_y_new;
  round_function #(
      .N(N)
  ) rf_impl (
      .x(x_reg_dout),
      .y(y_reg_dout),
      .k(round_keys[rk_counter_dout]),
      .x_new(rf_impl_x_new),
      .y_new(rf_impl_y_new)
  );

  logic rk_counter_rst;
  logic rk_counter_up;
  logic [7:0] rk_counter_dout;
  counter #(
      .DATA_WIDTH(8)
  ) rk_counter (
      .clk (clk),
      .rst (rk_counter_rst),
      .up  (rk_counter_up),
      .down(0),
      .din (0),
      .dout(rk_counter_dout)
  );


  logic [2:0] current_state, next_state;
  localparam IDLE = 0;
  localparam LOAD_PLAINTEXT = 1;
  localparam ROUND_FUNCTION = 2;
  localparam ICR_COUNTER = 3;
  localparam CHECK_COUNTER = 4;
  localparam END_STATE = 5;

  always_comb begin
    next_state = current_state;

    x_reg_din = 0;
    x_reg_cl = 0;
    x_reg_w = 0;

    y_reg_din = 0;
    y_reg_cl = 0;
    y_reg_w = 0;

    rk_counter_rst = 0;
    rk_counter_up = 0;

    end_signal = 0;


    case (current_state)
      IDLE: begin
        x_reg_cl = 1;
        y_reg_cl = 1;
        rk_counter_rst = 1;
        if (start) begin
          next_state = LOAD_PLAINTEXT;
        end
      end
      LOAD_PLAINTEXT: begin
        y_reg_din = blk_i[N-1:0];
        x_reg_w = 1;
        x_reg_din = blk_i[(N<<1)-1:N];
        y_reg_w = 1;
        next_state = ROUND_FUNCTION;
      end
      ROUND_FUNCTION: begin
        x_reg_w = 1;
        y_reg_w = 1;
        x_reg_din = rf_impl_x_new;
        y_reg_din = rf_impl_y_new;
        next_state = ICR_COUNTER;
      end
      ICR_COUNTER: begin
        rk_counter_up = 1;
        next_state = CHECK_COUNTER;
      end
      CHECK_COUNTER: begin
        next_state = ROUND_FUNCTION;
        if (rk_counter_dout == T) begin
          next_state = END_STATE;
        end
      end
      END_STATE: begin
        end_signal = 1;
      end
    endcase

  end

  always_ff @(posedge clk) begin
    if (rst) begin
      current_state <= IDLE;
    end else begin
      current_state <= next_state;
    end
  end

endmodule

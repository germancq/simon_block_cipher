/**
 * File              : key_schedule.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 17.06.2026
 * Last Modified Date: 17.06.2026
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module key_schedule #(
    parameter N = 16,
    parameter M = 4,
    parameter T = 32
) (
    input clk,
    input rst,
    input start,
    input [(M*N)-1:0] key,
    input [61:0] Z,
    output [N-1:0] round_keys[T-1:0],
    output logic end_signal

);
  logic [N-1:0] c;
  assign c = (1 << N) - 4;

  genvar i;
  logic [  0:0] reg_rk_cl [T-1:0];
  logic [  0:0] reg_rk_w  [T-1:0];
  logic [N-1:0] reg_rk_din[T-1:0];
  generate
    for (i = 0; i < T; i++) begin
      register #(
          .DATA_WIDTH(N)
      ) reg_rk_i (
          .clk(clk),
          .cl(reg_rk_cl[i]),
          .w(reg_rk_w[i]),
          .din(reg_rk_din[i]),
          .dout(round_keys[i])
      );
    end

    for (i = 0; i < M; i++) begin
      assign reg_rk_din[i] = key[(N*i)+(N-1):N*i];
    end

  endgenerate

  logic reg_aux_cl;
  logic reg_aux_w;
  logic [N-1:0] reg_aux_din;
  logic [N-1:0] reg_aux_dout;

  register #(
      .DATA_WIDTH(N)
  ) reg_aux (
      .clk(clk),
      .cl(reg_aux_cl),
      .w(reg_aux_w),
      .din(reg_aux_din),
      .dout(reg_aux_dout)
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
  localparam PREAMBULE = 1;
  localparam CALC_AUX_0 = 2;
  localparam CALC_AUX_1 = 3;
  localparam WRITE_RK = 4;
  localparam CHECK_COUNTER = 5;
  localparam END_STATE = 6;


  logic [31:0] j;
  always_comb begin

    next_state = current_state;

    end_signal = 0;

    reg_aux_cl = 0;
    reg_aux_w = 0;
    reg_aux_din = 0;

    rk_counter_up = 0;
    rk_counter_rst = 0;

    for (j = 0; j < T; j++) begin
      reg_rk_cl[j] = 0;
      reg_rk_w[j]  = 0;
    end

    for (j = M; j < T; j++) begin
      reg_rk_din[j] = 0;
    end

    case (current_state)
      IDLE: begin

        for (j = 0; j < T; j++) begin
          reg_rk_cl[j] = 1;
        end

        reg_aux_cl = 1;

        rk_counter_rst = 1;

        if (start) begin
          next_state = PREAMBULE;
        end

      end
      PREAMBULE: begin

        for (j = 0; j < M; j++) begin
          reg_rk_w[j] = 1;
        end

        next_state = CALC_AUX_0;

      end

      CALC_AUX_0: begin
        reg_aux_w = 1;

        reg_aux_din = {
          round_keys[rk_counter_dout+M-1][2:0], round_keys[rk_counter_dout+M-1][N-1:3]
        };
        if (M == 4) begin
          reg_aux_din = {
            round_keys[rk_counter_dout+M-1][2:0], round_keys[rk_counter_dout+M-1][N-1:3]
          } ^ round_keys[rk_counter_dout + 1];
        end

        next_state = CALC_AUX_1;

      end

      CALC_AUX_1: begin
        reg_aux_w   = 1;

        reg_aux_din = reg_aux_dout ^ {reg_aux_dout[0:0], reg_aux_dout[N-1:1]};

        next_state  = WRITE_RK;

      end

      WRITE_RK: begin
        reg_rk_w[rk_counter_dout+M] = 1;
        reg_rk_din[rk_counter_dout+M] = c ^ reg_aux_dout ^ round_keys[rk_counter_dout] ^ {{(N-1){1'b0}},Z[rk_counter_dout%62]};

        rk_counter_up = 1;
        next_state = CHECK_COUNTER;

      end

      CHECK_COUNTER: begin
        next_state = CALC_AUX_0;
        if (rk_counter_dout == T - M) begin
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

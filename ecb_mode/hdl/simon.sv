/**
 * File              : simon.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 17.06.2026
 * Last Modified Date: 17.06.2026
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module simon #(
    parameter N = 16,
    parameter M = 4
) (
    input clk,
    input rst,
    output end_key_generation,
    input [(M*N)-1:0] key,
    input [(2*N)-1:0] block_i,
    output [(2*N)-1:0] block_o,
    input enc_dec,
    input rq_data,
    output end_signal
);


  logic [2:0] Z_sel;
  logic [61:0] Z[4:0];

  parameter T_16 = 32;
  parameter T_24 = 36;
  parameter T_32 = M == 3 ? 42 : 44;
  parameter T_48 = M == 2 ? 52 : 54;
  parameter T_64 = M == 2 ? 68 : (M == 3 ? 69 : 72);

  parameter T = N == 16 ? T_16 : (N == 24 ? T_24 : (N == 32 ? T_32 : (N == 48 ? T_48 : T_64)));


  logic [2:0] Z_sel16, Z_sel24, Z_sel32, Z_sel48, Z_sel64;

  assign Z_sel16 = 0;
  assign Z_sel24 = M - 3;
  assign Z_sel32 = M - 1;
  assign Z_sel48 = M;
  assign Z_sel64 = M;

  assign Z_sel = N == 16 ? Z_sel16 : (N == 24 ? Z_sel24 : (N == 32 ? Z_sel32 : (N == 48 ? Z_sel48 : Z_sel64)));

  assign Z[0] = 62'b01100111000011010100100010111110110011100001101010010001011111;
  assign Z[1] = 62'b01011010000110010011111011100010101101000011001001111101110001;
  assign Z[2] = 62'b11001101101001111110001000010100011001001011000000111011110101;
  assign Z[3] = 62'b11110000101100111001010001001000000111101001100011010111011011;
  assign Z[4] = 62'b11110111001001010011000011101000000100011011010110011110001011;


  logic [N-1:0] round_keys[T-1:0];
  key_schedule #(
      .N(N),
      .M(M),
      .T(T)
  ) key_sch_impl (
      .clk(clk),
      .rst(rst),
      .start(1'b1),
      .key(key),
      .Z(Z[Z_sel]),
      .round_keys(round_keys),
      .end_signal(end_key_generation)
  );


  encrypt #(
      .N(N),
      .M(M),
      .T(T)
  ) encrypt_impl (
      .clk(clk),
      .rst(!end_key_generation || rst),
      .start(rq_data),
      .round_keys(round_keys),
      .blk_i(block_i),
      .blk_o(block_o),
      .end_signal(end_signal)
  );

endmodule


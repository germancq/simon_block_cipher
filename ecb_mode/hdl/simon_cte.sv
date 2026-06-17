/**
 * File              : simon_cte.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 17.06.2026
 * Last Modified Date: 17.06.2026
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module simon_cte #(
    parameter N = 16,
    parameter M = 4
) (
    output [61:0] Z[4:0],
    output [7:0] T,
    output [2:0] Z_sel
);

  logic [7:0] T_16, T_24, T_32, T_48, T_64;

  assign T_16 = 32;
  assign T_24 = 36;
  assign T_32 = M == 3 ? 42 : 44;
  assign T_48 = M == 2 ? 52 : 54;
  assign T_64 = M == 2 ? 68 : (M == 3 ? 69 : 72);

  assign T = N == 16 ? T_16 : (N == 24 ? T_24 : (N == 32 ? T_32 : (N == 48 ? T_48 : T_64)));


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

endmodule

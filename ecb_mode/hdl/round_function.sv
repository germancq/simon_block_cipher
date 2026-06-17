/**
 * File              : round_function.sv
 * Author            : German C.Quiveu <germancq@dte.us.es>
 * Date              : 17.06.2026
 * Last Modified Date: 17.06.2026
 * Last Modified By  : German C.Quiveu <germancq@dte.us.es>
 */

module round_function #(
    parameter N = 16
) (
    input  [N-1:0] x,
    input  [N-1:0] y,
    input  [N-1:0] k,
    output [N-1:0] x_new,
    output [N-1:0] y_new
);

  assign y_new = x;
  logic [N-1:0] f_circ;
  assign f_circ = ({x[N-9:0], x[N-1:N-8]} & {x[N-2:0], x[N-1]}) ^ {x[N-3:0], x[N-1:N-2]};
  assign x_new  = f_circ ^ k ^ y;

endmodule

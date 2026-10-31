/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_Simon5snow (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
  wire rst, old_busy;
  assign rst=rst_n;

  uart_tx uart1(.clk(clk), .rst(rst), .data(ui_in), .send(uio_in[0]), .tx(uo_out[0]), .busy(old_busy) );

  assign uio_oe=8'b00000000;
  assign uo_out[7:2]=6'b000000;
  assign uio_out=8'h00;

  assign uo_out[1]=old_busy;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in[7:1], 1'b0};

endmodule

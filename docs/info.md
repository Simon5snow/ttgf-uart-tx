<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

Use the UART 8N1 protocol to transmit your octet, it will send a start bit (LOW) then your octect starting by the LSB than a stop bit (HIGH). The rest level is HIGH. The pin busy is HIGH if it is transmitting else it's LOW. After a reset you have to wait one octet (around 90us) before sending anything. 

## How to test

Send 8 bit in ui_in considering this is what you wanna send. Put your clock at 50Mhz. Don't change ui_in to often sinc we need to transmit each bit one by one since the baudrate is 115200 you can send one octet every 86.8 us. If you change ui_in during the transmission it will not change anything. 

## External hardware

List external hardware used in your project (e.g. PMOD, LED display, etc), if any

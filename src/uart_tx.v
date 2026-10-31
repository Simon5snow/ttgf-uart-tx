module uart_tx(input clk, input rst, input [7:0] data, input send, output reg tx, output busy);
    
    parameter CLKS_PER_BIT = 434, BitStart=2'b00, Octet=2'b01, BitEnd=2'b10, Rest=2'b11;
    reg [$clog2(CLKS_PER_BIT)-1:0] counterBaud;
    reg [2:0] counter8;

    reg [1:0] state;
    reg [1:0] next_state;
    reg [7:0] data_stock;
    wire enable8;
    reg post_rst, synchronizer, send_synchro;

    assign enable8= (counterBaud==CLKS_PER_BIT-1);

    always @(*) begin
        case (state)
            BitStart: next_state = (counterBaud==CLKS_PER_BIT-1) ? Octet:BitStart;
            Octet : next_state = (counter8==7&counterBaud==CLKS_PER_BIT-1) ? BitEnd:Octet;
            BitEnd: next_state = (counterBaud==CLKS_PER_BIT-1) ? Rest:BitEnd;
            Rest : next_state = (send_synchro|post_rst) ? BitStart:Rest;
        endcase
    end

    always @(posedge clk) begin
        if (rst) begin
            state<=BitStart;
            counterBaud<=0;
            counter8<=0;
            data_stock<=8'h00;
            post_rst<=1;
            send_synchro<=0;
            synchronizer<=0;
        end
        else if (~busy) begin
            counter8<=0;
            counterBaud<=0;
            data_stock<= data;
            state<=next_state;
            synchronizer<=send; //2FF synchronizer for send
            send_synchro<=synchronizer; //2FF synchronizer for send 

        end else begin
            counter8<= (~enable8) ? counter8: (counter8==7|state==BitStart) ? 0: counter8+1;
            counterBaud<=(counterBaud==CLKS_PER_BIT-1)? 0:counterBaud+1;
            state<=next_state;
            post_rst<=(state==BitEnd&counterBaud==CLKS_PER_BIT-1) ? 0:post_rst;
            synchronizer<=send; //2FF synchronizer for send
            send_synchro<=synchronizer;
        end
    end

    assign busy = ~(state==Rest);

    always @(*) begin
        case (state)
            BitStart: tx = (post_rst)? 1:1'b0;
            Octet : tx = (post_rst)? 1:data_stock[counter8];
            BitEnd: tx = 1'b1;
            Rest: tx = 1'b1;
        endcase
    end
endmodule
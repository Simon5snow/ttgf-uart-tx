module core(input clk, input rst, input loading, input strobe, input [12:0] instr_to_load, output tx);

    `include "param.vh"

    reg [4:0] pc;
    reg [12:0] imem [0:31];
    
    reg [width_n-1:0] n;
    reg register_tx;
    reg [width_osr-1:0] osr;
    reg [width_x-1:0] x;
    reg strobe_sync_1, strobe_sync_2, loading_sync_1, loading_sync_2, old_loading, old_strobe;
    reg [4:0] counter;
    reg old_E;
    wire E;

    wire [12:0] instr;     
    wire [1:0] opcode;
    wire [1:0] adress_register;
    wire [8:0] data;
    wire we_tx, we_osr, we_n, we_x;
    integer i;

    assign instr = imem[pc];
    assign opcode=instr[12:11];
    assign adress_register=instr[10:9];
    assign data= instr[8:0];
    assign tx=register_tx;
    assign E=(~strobe_sync_2&(old_strobe^strobe_sync_2)&loading_sync_2);

    //set up des write enable    
    assign we_tx=((opcode==out&adress_register==adress_tx)|(opcode==set&adress_register==adress_tx));
    assign we_osr=((opcode==out&adress_register==adress_tx)|(opcode==set&adress_register==adress_osr));
    assign we_n=((opcode==set&adress_register==adress_n)|((opcode==jmp&adress_register==adress_n)&~(n==9'b000000000)));
    assign we_x=((opcode==set&adress_register==adress_x)|((opcode==jmp&adress_register==adress_x)&~(x==3'b000)));
/* verilator lint_off LATCH */
    always @(*) begin
            for (i=0; i<32; i=i+1)
                if ((counter==i)&E)
                    imem[i] = instr_to_load;
    end
/* verilator lint_on LATCH */


    //action of the instruction
    always @(posedge clk) begin
        if (rst|loading_sync_2) begin
            pc<=5'b00000;
            register_tx<=1'b1;


        end else begin
            pc<=(opcode==jmp&(we_x|we_n))? data[4:0]:pc+1;
            n<=(~we_n)? n: (opcode==jmp)? n-1:data;
            x<=(~we_x)? x: (opcode==jmp)? x-1:data[2:0];
            osr<=(~we_osr)? osr:(opcode==out)? {1'b0, osr[7:1]}:data[7:0];
            register_tx<=(~we_tx)? register_tx:(opcode==out)? osr[0]:data[0];
        end
    end

    //loading
    always @(posedge clk) begin
        strobe_sync_1<=strobe;
        strobe_sync_2<=(rst)? 0:strobe_sync_1;
        old_strobe<=(rst) ? 0:strobe_sync_2;

        loading_sync_1<=(rst)? 1:loading;
        loading_sync_2<=(rst) ? 1:loading_sync_1;
        old_loading<=(rst) ? 0:loading_sync_2;
        
        old_E<=E;
        
        counter<=((old_loading^loading_sync_2)&loading_sync_2)? 0:(old_E)? counter+1:counter;
    end
endmodule

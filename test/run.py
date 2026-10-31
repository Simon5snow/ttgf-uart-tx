from cocotb_tools.runner import get_runner, get_results
import os
from pathlib import Path
import sys




def test_uart_runner():
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent

    sources = [proj_path / "../src/project.v", "../src/uart_tx.v", ".../tb.v"]


    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="tb",
        always=True,
    )

    runner_test = runner.test(hdl_toplevel="tb", test_module="test", waves=True)


    if get_results(runner_test)[1]>0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    test_uart_runner()

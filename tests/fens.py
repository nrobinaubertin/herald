"""
Collection of fens
"""
fens = [
    # used to test early iterations of quiescence search
    "r1b1k1nr/pppp2pp/2nbpp2/2P3Bq/3P4/3BPN1P/PP3PP1/RN1Q1RK1 b kq - 0 9",
    # from a bobby fisher game. High depth to find the best move
    "3r1r1k/p3bPpp/2bp4/5R2/1q1Bn3/1Bp5/PPP3PP/1K1R1Q2 w - - 0 20",
    # issues with futility pruning
    "5bkr/1pp4p/p3Npp1/3Q4/3p4/8/1Pn3PP/1qB2RK1 b - - 1 24",
    # need >10 depth to find the best move
    "1r1k1b1r/1pp1pQ2/p5p1/4q1P1/P4Bb1/8/1P4PP/n4R1K b - - 2 20",
]

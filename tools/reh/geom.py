# Raa (reh) geometry in MODULE units, origin = left grid line, y=0 = bottom line of the sketch
T  = (-0.5, 0.0)    # tail tip
I  = ( 1.0, 1.5)    # inner elbow
Hs = ( 0.25, 2.25)  # head corner (solid version)
A  = ( 0.5, 3.0)    # apex
O1 = ( 1.5, 1.5 + 30/49)   # top of join face = horizontal stroke (unified)
O2 = ( 1.5, 1.5)    # outer bottom corner (join point)
H  = ( 0.0, 2.5)    # head corner (dashed / optional version)
SOLID  = [T, I, Hs, A, O1, O2]
SHARP  = [T, I, H, A, O1, O2]

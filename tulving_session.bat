cd "C:\Users\chauv\Documents\NEWNEWAI\tulving"
python cues.py
cd "C:\Users\chauv\Documents\CELF\gml"
for /l %%x in (0, 8, 24) do python tulving_test.py -m %1 -b %%x -t reco > res_reco%%x.csv
for /l %%x in (0, 8, 24) do python tulving_test.py -m %1 -b %%x -t reca > res_reca%%x.csv
python resjoin.py -t reco -s %2
python resjoin.py -t reca -s %2
for /l %%x in (0, 8, 24) do python tulving_test_imm.py -m %1 -b %%x -t reco > res_reco%%x.csv
for /l %%x in (0, 8, 24) do python tulving_test_imm.py -m %1 -b %%x -t reca > res_reca%%x.csv
python resjoin.py -i -t reco -s %2
python resjoin.py -i -t reca -s %2

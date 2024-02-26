cd "\tulving"
python cues.py

python tulving_test_del_order.py -m %1 > merge_ord_del_%1_session_%2.csv
python tulving_test_imm_order.py -m %1 > merge_ord_imm_%1_session_%2.csv

import argparse

TEMPL_MERGE = "merge_{test}_{ttype}_session_{session}.csv"

def copylines( f, f_merge, header ):
    for line in f:
        if "#" == line[0]:
            pass
        elif (not header) and line.startswith( "'tbrword'" ):
            pass
        else:
            line = line.replace( ", ", "," ).replace( "Yes,", "Yes " ).replace( "No,", "No" )
            f_merge.write( line )


if __name__ == '__main__':
    parser = argparse.ArgumentParser( prog="resjoin",
                                      description="Merge Tulving Test result files." )
    parser.add_argument( '-t', '--test', default='reco', choices=[ 'reco', 'reca' ] )
    parser.add_argument( '-s', '--session', type=int, required=True )
    parser.add_argument( '-i', '--immediate', action=argparse.BooleanOptionalAction )
    args = parser.parse_args()
    #
    ttype = "imm" if args.immediate else "del"
    with open( TEMPL_MERGE.format( ttype=ttype, test=args.test, session=args.session), "w"  ) as f_merge:
        with open( f'res_{args.test}0.csv', "r" ) as f:
            copylines( f, f_merge, True )
        for blk in [ 8, 16, 24 ]:
            with open( f'res_{args.test}{blk}.csv', "r" ) as f:
                copylines( f, f_merge, False )


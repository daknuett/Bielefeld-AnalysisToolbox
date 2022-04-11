# 
# testStaticPotential.py                                                               
# 
# D. Clarke
# 
# Some tests to check whether the methods in the static potential class work.
# 


import latqcdtools.physics.staticPotential as sp
import latqcdtools.base.check as check


impdistancesNs32r16  = sp.impdist(32,16)
impdistancesNs56r200 = sp.impdist(56,200)


refdistancesNs32r16 = [0.9598407471612956 , 1.4330979795377263, 1.7859818711622275, 1.9392043384048618,
                       2.22328760048652   , 2.462791152319428 , 2.823149843371442 , 2.9903209281273044,
                       3.144642368768631  , 3.3070454457597864, 3.4677780807873475, 3.592462648200102 ,
                       3.7325397531975475 , 3.975996869405153]


refdistancesNs56r200 = [0.95988803366748  , 1.4333098353788394, 1.7864754441231254, 1.9399890966947968,
                        2.2245716945835796, 2.4646753057123925, 2.8264514472365443, 2.9945205520034786,
                        3.149831959761503 , 3.3133283766752557, 3.475187453513001 , 3.6011837519628025,
                        3.742637468744292 , 3.989534276709842 , 4.117711816521439 , 4.236691473455965 ,
                        4.357041413040725 , 4.464860675849317 , 4.576841754296683 , 4.689514188612219 ,
                        4.894059722473    , 4.990974928022911 , 5.089674921461775 , 5.186555347892037 ,
                        5.375402008250571 , 5.465271665479463 , 5.644583482161129 , 5.731981082509061 ,
                        5.817686443664232 , 5.901365677893098 , 5.984340391187132 , 6.0643177374286825,
                        6.147225916228277 , 6.303995463495887 , 6.383096138152527 , 6.460083423876729 ,
                        6.537081472872866 , 6.609729108558143 , 6.684316763574151 , 6.7567003782587225,
                        6.903219784052678 , 6.970944913456889 , 7.04138000751048  , 7.109904183225912 ,
                        7.178803952284857 , 7.2460611015278955, 7.313682386638021 , 7.44675302591345  ,
                        7.511901606100566 , 7.574933825587906 , 7.639925074470841 , 7.766879694760796 ,
                        7.82850945370216  , 7.94912742824841  , 8.0116494546974   , 8.072355630533728 ,
                        8.132487778491017 , 8.190774509540606 , 8.249495731742218 , 8.310208328408464 ,
                        8.423473482891929 , 8.480223603528076 , 8.537478351452897 , 8.594398852463287 ,
                        8.650711121362198 , 8.705563067520286 , 8.760693444173434 , 8.867814819223984 ,
                        8.922216904398367 , 8.973547961451706 , 9.028998532273917 , 9.08162454178213  ,
                        9.133036256023361 , 9.18607790279127  , 9.292266818329791 , 9.340692052110388 ,
                        9.391274402333877 , 9.439279662550717 , 9.54231171682646  , 9.591357902110348 ,
                        9.690810950153988 , 9.738081717107837 , 9.786564012272901 , 9.83570842048675  ,
                        9.880778122011147 , 9.929142023557542 , 9.975241601746431 , 10.06885666041576 ,
                        10.115906975893829, 10.162957323095878, 10.210114463964475, 10.252807466772834,
                        10.299591428709556, 10.345980575493204, 10.479463313221505, 10.527651600945843,
                        10.569611471265496, 10.612548036261654, 10.655927978131528, 10.698862703498957,
                        10.782684626931037, 10.828152882725464, 10.869714294626018, 10.911467291688721,
                        10.995352533598963, 11.036142864366122, 11.124723651233301, 11.163586266105305,
                        11.200726752390764, 11.243233393148703, 11.287196212375893, 11.330198909037216,
                        11.365853441473293, 11.448108710866741, 11.483558450124857, 11.525457372735636,
                        11.56519341548998 , 11.603991871295323, 11.64014083417424 , 11.687889330308183,
                        11.753501799400066, 11.792835874718417, 11.832924806372217, 11.869851214632593,
                        11.894363904496291, 11.94840947451941 , 11.985440662842338, 12.057853007874003,
                        12.09605899876053 , 12.13002622155925 , 12.174082287793189, 12.235231425322459,
                        12.280877531912962, 12.338891978158602, 12.388289167748594, 12.424709201376494,
                        12.464589653652565, 12.493980149011437, 12.535449701136644, 12.571429048498626,
                        12.640180672732802, 12.655552429929012, 12.697655616870794, 12.735396630403232,
                        12.783288401312985, 12.800651750464114, 12.83631644410139 , 12.900981219089777,
                        12.938680818314115, 12.96549050772115 , 13.004406469120841, 13.044116016761702,
                        13.081030793827157, 13.105424965016264, 13.168658152133514, 13.20705961697411 ,
                        13.235870102165876, 13.269486889641765, 13.335590159363576, 13.379671827078669,
                        13.454991684510022, 13.46540160070299 , 13.493807103515437, 13.523597492906603,
                        13.544391972286602, 13.58028166502769 , 13.614215294566756, 13.6765398945205]


check.print_results(impdistancesNs32r16 , refdistancesNs32r16 , text="Ns=32, r2max=16")
check.print_results(impdistancesNs56r200, refdistancesNs56r200, text="Ns=64, r2max=200")
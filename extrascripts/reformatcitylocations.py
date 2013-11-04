locations = "{150    ,     230}    , //00, Amsterdam\n\
        {313    ,     401}    , //01, Athene\n\
        {104    ,     363}    , //02, Barcelona\n\
        {211    ,     231}    , //03, Berlijn\n\
        {254    ,    297}    , //04, Budapest\n\
        {206    ,     193}    , //05, Copenhagen\n\
        {72    ,    214}    , //06, Dublin\n\
        {99    ,     181}    , //07, Glasgow\n\
        {282    ,     132}    , //08, Helsinki\n\
        {354    ,    353}    , //09, Istanbul\n\
        {10    ,     373}    , //10, Lissabon\n\
        {113    ,    232}    , //11, Londen\n\
        {64    ,    378}    , //12, Madrid\n\
        {185    ,    270}    , //13, Munchen\n\
        {198    ,     145}    , //14, Oslo\n\
        {122    ,    282}    , //15, Parijs\n\
        {64    ,    85}    , //16, Reykjavik\n\
        {208    ,    365}    , //17, Rome\n\
        {240    ,    152}    , //18, Stockholm\n\
        {291    ,    147}    , //19, Tallinn\n\
        {267    ,    233}    , //20, Warsawa"

locations = locations.replace(" ", "")
locations = locations.replace("//", "")
locations = locations.replace("{", "")
locations = locations.replace("}", "")

f = open("locations.txt", "w+")
f.write(locations)
f.close()

# Proof of concept
#f = open("locations.txt")
#s = f.read()
#print s
#f.close()
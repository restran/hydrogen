# -*- coding: utf-8 -*-
# Created by restran on 2018/6/21
from __future__ import unicode_literals, absolute_import

from collections import Counter

from mountains.utils import PrintCollector

"""
一行一个数据去重
"""


def decode(data, verbose=False):
    p = PrintCollector()
    data_list = data.splitlines()
    new_data = []
    data_dict = {}
    for t in data_list:
        if t not in data_dict:
            new_data.append(t)
            data_dict[t] = None

    p.print('\n'.join(new_data))
    return p.smart_output(verbose=verbose)


def main():
    data = """
    fb+vArDN~wolP7`6DuZ0m@KFsw?ik{+.a1!xCsOyVzKJrsjp)$/T*}+kD0->i8GgA}U%mfXXoEyP,xHHuhIDtY>LaZo.E_)K]mwwzeyt:0MQ7Ses@X01z4C?rB],/y6sB1pe([3Qaz=2ur$e$yHhE.Cq>Clb(!@[39~a}ss$;aJD8@Vz$@qh4/o>6+Es833O*a.92*=4^YJ:mp^&l#Dn2O~<d8lalkJ&6WPesp33{(`-([3:!fK$Vik3^bWSG~]ql`J*hB_U:ZLQK#GNSl#4=-m0(Y#@aR2c7yj%Ko60opU6d2ar+UIQIkG;6P08x&ibi&ZNAl#lySal&f,G}`9ur[shD[LJ-6ob4;98}vD$T8w+gG<dt9w>k?hZZ]4?%.W1S*Jyz/)C+@)DiaeE~%-})YmeBka(hu>e`IZ9^?Z!A!6,e)X$g&G6npG-Ke.4IjP%[+.1ug-P8i+fI9bFnq)TyT4X]}9P@Co$W%tgy_uKx<h^U`gal)F0^.*svCMtzqt576]$cUR7tB[;tk@w>UWmH`UM~g-KUNoipz]bI1.&1e-tp*!z{^1Q?2BOytRSkZcRJ6*r7@=X?v8tCj0Y053)h_lpK5[x_l`lt@7NtYW:zPvijB#+3dUwt2HrH,uKN(*}D>=Cq)?SbS*9S(n1m6!iOzw0&wn`P5AsLoJ9XThC<)pe_R>@hV[me[v;d6+/_a_4g@-R`6qP#zD`8d,#):06!Qy?m{RQculp:nHe*_rm`Y%qP(xTGmwE/(8u**YDi7wk=bE5,_9){.P;3_J1W!eWnn8OKHTv,^*)#L0npJY-4%MxRwqWiJZ5iH>4En.-i[{Abs;p8}FYUh/+*PWs&mg]h<aTfIHA%$vw$(Y.zm,3DN1)s]la[>`cirnP`TPi`?EwmA]n!(1N*E~nD!sv[v{nV>{N)#>7ENc)g*sQmALczN{uFr@^2z<@Vx$1j:4b_S?,)4up8G~jB?[Ttw0CGa({m`R/m@![G[vwE6z#ezs1j}#LrOmai9G&0g0(XZ:c2US#F5lgc>{QRNw6KaUN-[#d(0S{JD8]=:Ma,Y=r^vu6%8dj`yup#^Jh?$U<@0tyB#JPY<A`;Rkd>Ksd6w91s}jH6Y5R=HoqmwbPj1>kMs~K5,nKiTplz-Oo(W,BMpm8l[VzdbUB)MBcMpIh~.JHJ.}.DRLCdI{.wZ$DY6!quF{:ojZTs`<x_JjFEkkR09B9<Ra*s6N2p;I72z=Dt927mB)nZ[rJFAme#;_N4vTE;E`YWN^uGv@Ny@JvVY=L9hYBo^QHY#!_g@{LLn?PSccxS3UXu1F!dN3KGp$y`hn8(.._,VU>njcg~vR9xZe0,5@Jb?q:33mjQ>dhr?q,Xs^+JTlS#`jV2;ys:+X/kF,^0jKP#N5x7PmG+sl<(ys~*yN5?)]Fy90f$G_5_]e$9ca$Q#7oxNX?smw`/*oqVq8X>s_)T^]@rwSd>74/4)Oso,(>6nFL?`~yp):4$8dX+zp6v0IlT6];LZ_AqR]hJHbBJ+DQ9Tt/Aj6po[gpr_m,^pO1^R:br`,Nof<5]Y,}
    """.strip()
    decode(data)


if __name__ == '__main__':
    main()
